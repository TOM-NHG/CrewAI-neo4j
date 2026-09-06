"""
Agent 1: Intent & Semantic Extractor Agent (Router Agent).
Phân tích câu hỏi tiếng Việt, nhận diện ý định và bóc tách các thực thể chính.
"""

import json
import logging
from typing import Dict, Any
import requests
from src.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là Trợ lý Phân tích Ý định & Thực thể cho Hệ thống Đào tạo & Quản lý Sinh viên.
Nhiệm vụ của bạn là đọc câu hỏi của người dùng và trích xuất thông tin dưới dạng JSON chuẩn.

Các miền ý định (intent):
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
                return parsed
        except Exception as e:
            logger.warning("OLM chưa sẵn sàng hoặc timeout khi bóc tách thực thể: %s", e)

        # Fallback phân tích heuristic nếu OLM tạm thời chưa bật
        return self._heuristic_fallback(user_question)

    def _heuristic_fallback(self, question: str) -> Dict[str, Any]:
        q_lower = question.lower()
        intent = "general_query"
        if any(k in q_lower for k in ["vắng", "điểm danh", "nghỉ học", "chuyên cần"]):
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
