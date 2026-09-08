"""
Agent 1: Intent & Semantic Extractor Agent (Router Agent).
Phân tích câu hỏi tiếng Việt, nhận diện ý định và bóc tách các thực thể chính.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any
import requests

# Đảm bảo đường dẫn gốc của project có trong sys.path khi chạy trực tiếp file từ bất kỳ thư mục nào
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là Trợ lý Phân tích Ý định & Thực thể cho Hệ thống Đào tạo & Quản lý Sinh viên.
Nhiệm vụ của bạn là đọc câu hỏi của người dùng và trích xuất thông tin dưới dạng JSON chuẩn.

Các miền ý định (intent):
- "knowledge_query": Tra cứu khái niệm, định nghĩa mã ngành, mã cơ sở, giải nghĩa thuật ngữ học vụ (ví dụ: "mã SE là ngành gì", "FPTU-HN là cơ sở nào", "bảo lưu là gì").
- "attendance_query": Tra cứu điểm danh, vắng mặt, đi muộn.
- "warning_query": Cảnh báo sinh viên có nguy cơ cấm thi, học vụ.
- "status_query": Tra cứu trạng thái học vụ (bảo lưu, thôi học, tốt nghiệp).
- "lecturer_query": Tra cứu thông tin giảng viên, lớp dạy, lịch dạy.
- "grade_query": Tra cứu điểm số, đánh giá, xếp loại.
- "general_query": Các câu hỏi chung về sinh viên hoặc lớp học.

Đầu ra BẮT BUỘC chỉ là một đối tượng JSON thuần túy (không kèm giải thích, không bọc trong ```json):
{
  "intent": "tên_intent",
  "entities": {
    "student_name": "tên nếu có hoặc null (BẮT BUỘC GIỮ NGUYÊN VẸN DẤU TIẾNG VIỆT, ví dụ: 'Duyên Đặng')",
    "student_code": "mã số sinh viên (ví dụ: 'SE180001') nếu có hoặc null. TUYỆT ĐỐI KHÔNG gán tên cơ sở/địa danh vào student_code!",
    "program_code": "mã ngành (ví dụ: 'SE', 'AI', 'IA', 'BA') nếu có hoặc null",
    "campus": "tên cơ sở/khuôn viên (ví dụ: 'Hà Nội', 'TP.HCM', 'Đà Nẵng') nếu có hoặc null",
    "lecturer_name": "tên gv nếu có hoặc null (BẮT BUỘC GIỮ NGUYÊN VẸN DẤU TIẾNG VIỆT)",
    "class_code": "mã lớp nếu có hoặc null",
    "date": "ngày nếu có (YYYY-MM-DD) hoặc null",
    "condition": "điều kiện lọc đặc biệt như 'cấm thi', 'vắng > 20%', 'điểm < 5'..."
  }
}
"""


class RouterAgent:
    def __init__(self):
        self.model = settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_BASE_URL

    def analyze(self, user_question: str) -> Dict[str, Any]:
        """Phân tích câu hỏi tiếng Việt thành cấu trúc ý định & thực thể."""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "system": SYSTEM_PROMPT,
                "prompt": f"Câu hỏi: {user_question}\nPhân tích JSON:",
                "stream": False,
                "options": {
                    "temperature": 0.1
                }
            }
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                raw_text = response.json().get("response", "").strip()
                # Làm sạch markdown nếu có
                if raw_text.startswith("```"):
                    raw_text = raw_text.strip("`").replace("json", "").strip()
                parsed = json.loads(raw_text)
                # Chuẩn hóa giá trị chuỗi "null", "none", "None" thành None thực sự
                if isinstance(parsed, dict) and "entities" in parsed and isinstance(parsed["entities"], dict):
                    clean_entities = {}
                    for k, v in parsed["entities"].items():
                        if v and str(v).strip().lower() not in ["null", "none", "không", ""]:
                            clean_entities[k] = v.strip() if isinstance(v, str) else v
                    parsed["entities"] = clean_entities
                return parsed
        except Exception as e:
            logger.warning("OLM chưa sẵn sàng hoặc timeout khi bóc tách thực thể: %s", e)

        # Fallback phân tích heuristic nếu OLM tạm thời chưa bật
        return self._heuristic_fallback(user_question)

    def _heuristic_fallback(self, question: str) -> Dict[str, Any]:
        q_lower = question.lower()
        intent = "general_query"
        if any(k in q_lower for k in ["là ngành gì", "nghĩa là gì", "viết tắt", "là gì", "ở đâu"]):
            intent = "knowledge_query"
        elif any(k in q_lower for k in ["vắng", "điểm danh", "nghỉ học", "chuyên cần"]):
            intent = "attendance_query"
        elif any(k in q_lower for k in ["cấm thi", "nguy cơ", "cảnh báo"]):
            intent = "warning_query"
        elif any(k in q_lower for k in ["bảo lưu", "thôi học", "tốt nghiệp", "trạng thái"]):
            intent = "status_query"
        elif any(k in q_lower for k in ["giảng viên", "thầy", "cô", "dạy"]):
            intent = "lecturer_query"
        elif any(k in q_lower for k in ["điểm", "thi", "quiz", "kết quả"]):
            intent = "grade_query"

        return {
            "intent": intent,
            "entities": {
                "raw_query": question
            }
        }


router_agent = RouterAgent()


if __name__ == "__main__":
    import pprint
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    print("=" * 80)
    print("🎯 DEMO CHẠY ROUTER AGENT (INTENT & SEMANTIC EXTRACTOR)")
    print(f"   Model: {router_agent.model} | Endpoint: {router_agent.base_url}")
    print("=" * 80)

    sample_questions = [
        "Mã SE là ngành gì?",
        "Cảnh báo những sinh viên có nguy cơ cấm thi vì vắng quá 20% môn Java?",
        "Sinh viên Duyên Đặng nghỉ học bao nhiêu buổi rồi?",
        "Danh sách sinh viên đang bảo lưu trong học kỳ này?",
        "Giảng viên Nguyễn Văn An đang dạy những lớp nào?",
        "Điểm trung bình của sinh viên SE180001 là bao nhiêu?",
    ]

    print("\n--- 1. CHẠY BỘ CÂU HỎI MẪU ---")
    for idx, q in enumerate(sample_questions, 1):
        print(f"\n[{idx}] Câu hỏi: {q}")
        res = router_agent.analyze(q)
        print("    👉 Kết quả phân tích:")
        print(json.dumps(res, ensure_ascii=False, indent=6))

    print("\n" + "=" * 80)
    print("--- 2. CHẾ ĐỘ NHẬP CÂU HỎI TƯƠNG TÁC (Gõ 'exit' hoặc 'quit' để thoát) ---")
    try:
        while True:
            user_input = input("\nNhập câu hỏi của bạn: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Đã thoát.")
                break
            result = router_agent.analyze(user_input)
            print("👉 Kết quả phân tích JSON:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except (KeyboardInterrupt, EOFError):
        print("\nĐã dừng.")
