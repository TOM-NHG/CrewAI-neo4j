"""
Mô-đun quản lý Sổ tay Quy tắc & Cạm bẫy Cần tránh (Negative Rules Store).
Ghi nhận các sai sót ngữ nghĩa khi người dùng đánh giá (👎) để OLM không bao giờ lặp lại.
"""

import json
from pathlib import Path
from typing import List

RULES_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "learned_rules.json"

DEFAULT_RULES = [
    "TUYỆT ĐỐI KHÔNG nối trực tiếp (Employee)-[:TEACHES]->(Student). Bắt buộc phải nối qua (:Activity): (Employee)-[:LEADS]->(Activity)<-[:PARTICIPATED_IN]-(Student).",
    "Khi người dùng hỏi 'sinh viên vắng mặt', chỉ lọc part.attendance_status = 'ABSENT', không tính trạng thái 'LATE' là vắng.",
    "Khi lọc trạng thái 'đang bảo lưu', bắt buộc phải kiểm tra st.status = 'SUSPENDED' VÀ st.effective_to IS NULL.",
    "Khi tìm kiếm theo tên người hoặc tên lớp, luôn dùng hàm toLower(p.full_name) CONTAINS toLower('...') để tránh lỗi không khớp chữ hoa/chữ thường.",
    "Mọi câu lệnh truy vấn danh sách đều phải có mệnh đề LIMIT (mặc định LIMIT 50 nếu người dùng không yêu cầu số lượng cụ thể)."
]


class RulesStore:
    def __init__(self):
        self._rules: List[str] = []
        self._load_rules()

    def _load_rules(self):
        if RULES_FILE.exists():
            try:
                with open(RULES_FILE, "r", encoding="utf-8") as f:
                    self._rules = json.load(f)
                return
            except Exception:
                pass
        self._rules = list(DEFAULT_RULES)
        self._save_rules()

    def _save_rules(self):
        RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(RULES_FILE, "w", encoding="utf-8") as f:
            json.dump(self._rules, f, ensure_ascii=False, indent=2)

    def add_rule(self, rule_text: str) -> None:
        """Thêm một quy tắc / bài học kinh nghiệm mới vào sổ tay."""
        clean_text = rule_text.strip()
        if clean_text and clean_text not in self._rules:
            self._rules.append(clean_text)
            self._save_rules()

    def get_rules(self) -> List[str]:
        self._load_rules()
        return self._rules

    def format_rules_for_prompt(self) -> str:
        """Định dạng danh sách quy tắc cấm đưa vào Prompt."""
        lines = ["[QUY TẮC BẮT BUỘC & CẠM BẪY CẦN TRÁNH ĐÃ ĐƯỢC GHI NHẬN]:"]
        for i, rule in enumerate(self._rules, 1):
            lines.append(f"{i}. {rule}")
        return "\n".join(lines)


# Singleton
rules_store = RulesStore()
