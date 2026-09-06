"""
Máy chủ Web API & Static Server phục vụ Giao diện Chatbot NHG Design System.
Chạy mặc định trên cổng 8080 (hoặc cấu hình qua biến WEB_PORT).
Lệnh chạy: python src/web_server.py
"""

import sys
import json
import logging
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import urllib.request

# Đảm bảo đường dẫn import
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# Đảm bảo UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from src.config import settings
from src.db.neo4j_client import neo4j_client
from src.crew.edu_crew import edu_crew
from src.memory.feedback_manager import feedback_manager
from src.memory.few_shot_pool import few_shot_pool
from src.memory.rules_store import rules_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

WEB_DIR = ROOT_DIR / "web"
PORT = 8080


class EduGraphHTTPHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, default=str, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, file_path: Path, content_type: str):
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, f"File not found: {file_path.name}")
            return
        
        with open(file_path, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            neo_ok = neo4j_client.connect()
            status_data = {
                "neo4j_connected": neo_ok,
                "neo4j_uri": settings.NEO4J_URI,
                "model": settings.OLLAMA_MODEL,
                "few_shot_count": len(few_shot_pool._pool),
                "rules_count": len(rules_store._rules)
            }
            self._send_json(status_data)
            return

        if path == "/api/models":
            models_list = []
            try:
                tags_url = f"{settings.OLLAMA_BASE_URL}/api/tags"
                req = urllib.request.Request(tags_url)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    raw_models = data.get("models", [])
                    for m in raw_models:
                        m_name = m.get("name", "")
                        details = m.get("details", {})
                        param_size = details.get("parameter_size", "")
                        quant_level = details.get("quantization_level", "Q4_K_M")
                        size_gb = round(m.get("size", 0) / (1024**3), 2)
                        
                        is_current = (m_name == settings.OLLAMA_MODEL)
                        models_list.append({
                            "name": m_name,
                            "param_size": param_size,
                            "quantization": quant_level,
                            "size_gb": size_gb,
                            "is_current": is_current,
                            "label": f"{m_name} ({param_size} • {quant_level} Lượng tử • {size_gb}GB)"
                        })
            except Exception as e:
                logger.warning("Lỗi khi lấy danh sách mô hình từ Ollama: %s", e)
                models_list = [
                    {"name": "qwen2.5:7b", "param_size": "7.6B", "quantization": "Q4_K_M", "size_gb": 4.68, "is_current": settings.OLLAMA_MODEL == "qwen2.5:7b", "label": "qwen2.5:7b (7.6B • Q4_K_M Lượng tử • 4.68GB)"},
                    {"name": "qwen2.5:3b", "param_size": "3.1B", "quantization": "Q4_K_M", "size_gb": 1.93, "is_current": settings.OLLAMA_MODEL == "qwen2.5:3b", "label": "qwen2.5:3b (3.1B • Q4_K_M Lượng tử • 1.93GB)"},
                    {"name": "qwen2.5:1.5b", "param_size": "1.5B", "quantization": "Q4_K_M", "size_gb": 0.99, "is_current": settings.OLLAMA_MODEL == "qwen2.5:1.5b", "label": "qwen2.5:1.5b (1.5B • Q4_K_M Lượng tử • 0.99GB)"},
                ]

            self._send_json({"models": models_list, "current_model": settings.OLLAMA_MODEL})
            return

        # Serve static files
        if path in ["/", "/index.html"]:
            self._serve_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
        elif path == "/style.css":
            self._serve_file(WEB_DIR / "style.css", "text/css; charset=utf-8")
        elif path == "/app.js":
            self._serve_file(WEB_DIR / "app.js", "application/javascript; charset=utf-8")
        elif path.startswith("/assets/"):
            rel_path = path[len("/assets/"):]
            file_path = WEB_DIR / "assets" / rel_path
            # Xác định content-type
            suffix = file_path.suffix.lower()
            mime = "application/octet-stream"
            if suffix == ".png":
                mime = "image/png"
            elif suffix == ".svg":
                mime = "image/svg+xml"
            elif suffix in [".jpg", ".jpeg"]:
                mime = "image/jpeg"
            self._serve_file(file_path, mime)
        else:
            self.send_error(404, "Page Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_len) if content_len > 0 else b"{}"

        try:
            body = json.loads(post_data.decode("utf-8"))
        except Exception:
            self._send_json({"error": "Dữ liệu JSON không hợp lệ."}, status=400)
            return

        if path == "/api/query":
            question = body.get("question", "").strip()
            model_override = body.get("model", settings.OLLAMA_MODEL)
            if not question:
                self._send_json({"error": "Vui lòng nhập câu hỏi."}, status=400)
                return

            logger.info("Nhận yêu cầu truy vấn từ Web UI: '%s' (Mô hình: %s)", question, model_override)
            result = edu_crew.process_query(question, model_name=model_override)
            self._send_json(result)

        elif path == "/api/model":
            new_model = body.get("model")
            if new_model:
                settings.OLLAMA_MODEL = new_model
                logger.info("Đã chuyển mô hình OLM hoạt động sang: %s", new_model)
                self._send_json({"success": True, "current_model": new_model})
            else:
                self._send_json({"error": "Thiếu tên mô hình."}, status=400)

        elif path == "/api/feedback":
            q = body.get("question", "")
            cypher = body.get("cypher", "")
            is_correct = body.get("is_correct", True)
            note = body.get("note")
            corr_cypher = body.get("corrected_cypher")

            logger.info("Nhận phản hồi người dùng: is_correct=%s | note=%s", is_correct, note)
            res = feedback_manager.record_feedback(
                user_question=q,
                generated_cypher=cypher,
                is_correct=is_correct,
                feedback_note=note,
                corrected_cypher=corr_cypher
            )
            self._send_json(res)

        else:
            self.send_error(404, "Endpoint Not Found")


def run_server(port=PORT):
    server_address = ("", port)
    httpd = HTTPServer(server_address, EduGraphHTTPHandler)
    print(f"\n==================================================================")
    print(f"🌟 EDU-GRAPH CHATBOT (NHG DESIGN SYSTEM) ĐANG CHẠY TẠI:")
    print(f"👉 http://localhost:{port}")
    print(f"==================================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nĐang tắt máy chủ Web...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
