"""
Mô-đun quản lý Kho ví dụ mẫu (Dynamic Few-Shot Pool).
Tự động tìm kiếm các ví dụ Cypher tương đồng nhất để đưa vào Prompt cho OLM.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

# File lưu trữ các câu mẫu đã xác nhận
FEW_SHOT_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "verified_few_shots.json"

# Tập ví dụ mẫu khởi tạo chuẩn mực của Phòng Đào tạo & Quản lý Sinh viên
DEFAULT_FEW_SHOTS = [
    {
        "id": "att_01",
        "question": "Tìm những sinh viên vắng mặt ở lớp PRO192_SE1801 ngày 2024-09-02",
        "intent": "attendance_query",
        "cypher": """MATCH (p:Person)-[:HAS_ROLE]->(s:Student)-[part:PARTICIPATED_IN]->(a:Activity)
WHERE a.class_code = 'PRO192_SE1801'
  AND a.scheduled_date = date('2024-09-02')
  AND part.attendance_status = 'ABSENT'
RETURN p.full_name AS student_name, s.student_code AS student_code, a.activity_name AS activity, part.note AS note"""
    },
    {
        "id": "att_02",
        "question": "Cảnh báo những sinh viên có nguy cơ cấm thi vì vắng quá 20% số buổi môn PRO192_SE1801",
        "intent": "warning_query",
        "cypher": """MATCH (c:Class {class_code: 'PRO192_SE1801'})<-[:PART_OF]-(all_act:Activity)
WITH c, count(DISTINCT all_act) AS total_sessions
MATCH (p:Person)-[:HAS_ROLE]->(s:Student)-[part:PARTICIPATED_IN]->(a:Activity)-[:PART_OF]->(c)
WHERE part.attendance_status = 'ABSENT'
WITH p, s, c, total_sessions, count(part) AS absent_count,
     round(100.0 * count(part) / total_sessions, 1) AS absent_rate
WHERE absent_rate >= 20.0
RETURN p.full_name AS student_name, s.student_code AS student_code,
       absent_count, total_sessions, absent_rate AS `absent_percentage_%`
ORDER BY absent_rate DESC"""
    },
    {
        "id": "status_01",
        "question": "Danh sách sinh viên đang bảo lưu trong học kỳ này",
        "intent": "status_query",
        "cypher": """MATCH (p:Person)-[:HAS_ROLE]->(s:Student)-[st:HAS_STATUS]->(s)
WHERE st.status = 'SUSPENDED' AND st.effective_to IS NULL
RETURN p.full_name AS student_name, s.student_code AS student_code,
       st.effective_from AS suspended_from, st.note AS reason"""
    },
    {
        "id": "status_02",
        "question": "Những sinh viên nào từng bảo lưu rồi quay lại học?",
        "intent": "status_history_query",
        "cypher": """MATCH (p:Person)-[:HAS_ROLE]->(s:Student)-[st:HAS_STATUS]->(s)
WHERE st.status = 'SUSPENDED' AND st.effective_to IS NOT NULL
RETURN p.full_name AS student_name, s.student_code AS student_code,
       st.effective_from AS suspended_from, st.effective_to AS returned_at, st.note AS note"""
    },
    {
        "id": "lecturer_01",
        "question": "Giảng viên Nguyễn Văn An đang dạy những lớp và buổi học nào?",
        "intent": "lecturer_teaching_query",
        "cypher": """MATCH (p:Person)-[:HAS_ROLE]->(e:Employee)-[lead:LEADS]->(a:Activity)-[:PART_OF]->(c:Class)
WHERE toLower(p.full_name) CONTAINS toLower('Nguyễn Văn An')
RETURN c.class_code AS class_code, c.class_name AS class_name,
       a.activity_name AS activity_name, a.scheduled_date AS date, lead.role AS role
ORDER BY a.scheduled_date ASC"""
    },
    {
        "id": "dual_01",
        "question": "Ai là sinh viên vừa đi học vừa làm trợ giảng (TA)?",
        "intent": "dual_role_query",
        "cypher": """MATCH (p:Person)-[:HAS_ROLE]->(s:Student)
MATCH (p)-[:HAS_ROLE]->(e:Employee)-[r:ASSIGNED_TO_DEPT]->(d:Department)
WHERE r.position_code = 'TA'
RETURN p.full_name AS full_name, s.student_code AS student_code,
       e.employee_code AS employee_code, d.dept_name AS department"""
    },
    {
        "id": "grade_01",
        "question": "Xem điểm số và xếp loại của sinh viên Nguyễn Anh Tuấn",
        "intent": "grade_query",
        "cypher": """MATCH (p:Person)-[:HAS_ROLE]->(s:Student)-[part:PARTICIPATED_IN]->(a:Activity)-[:PART_OF]->(c:Class)
WHERE toLower(p.full_name) CONTAINS toLower('Nguyễn Anh Tuấn')
RETURN c.class_code AS class_code, a.activity_name AS activity,
       a.scheduled_date AS date, part.quiz_score AS quiz,
       part.assignment_score AS assignment, part.grade AS grade
ORDER BY a.scheduled_date ASC"""
    }
]


class FewShotPool:
    def __init__(self):
        self._pool: List[Dict[str, Any]] = []
        self._load_pool()

    def _load_pool(self):
        if FEW_SHOT_FILE.exists():
            try:
                with open(FEW_SHOT_FILE, "r", encoding="utf-8") as f:
                    self._pool = json.load(f)
                return
            except Exception:
                pass
        
        # Dùng mặc định nếu file chưa có
        self._pool = list(DEFAULT_FEW_SHOTS)
        self._save_pool()

    def _save_pool(self):
        FEW_SHOT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(FEW_SHOT_FILE, "w", encoding="utf-8") as f:
            json.dump(self._pool, f, ensure_ascii=False, indent=2)

    def add_verified_example(self, question: str, cypher: str, intent: str = "custom") -> None:
        """Lưu một câu hỏi và câu Cypher đã được xác nhận đúng (👍) vào kho."""
        new_item = {
            "id": f"dyn_{len(self._pool) + 1:03d}",
            "question": question.strip(),
            "intent": intent,
            "cypher": cypher.strip()
        }
        self._pool.append(new_item)
        self._save_pool()

    def get_relevant_examples(self, user_query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Tìm kiếm các ví dụ mẫu tương đồng nhất về mặt ngữ nghĩa bằng thuật toán
        Jaccard & Keyword token overlap nhẹ nhàng mà không cần server vector riêng.
        """
        self._load_pool()
        query_words = set(user_query.lower().split())
        scored = []

        for item in self._pool:
            target_words = set(item["question"].lower().split())
            intersection = query_words.intersection(target_words)
            union = query_words.union(target_words)
            jaccard = len(intersection) / len(union) if union else 0.0

            # Ưu tiên các từ khóa cốt lõi của nghiệp vụ
            keywords = [
                "vắng", "cấm thi", "bảo lưu", "trợ giảng", "điểm", "giảng viên", 
                "thôi học", "tốt nghiệp", "lớp", "ngành", "cơ sở", "hà nội", 
                "hồ chí minh", "hcm", "đà nẵng", "hồ sơ", "sinh viên", "học kỳ"
            ]
            bonus = sum(2.0 for kw in keywords if kw in user_query.lower() and kw in item["question"].lower())

            total_score = jaccard + bonus
            scored.append((total_score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]]

    def format_examples_for_prompt(self, user_query: str, top_k: int = 3) -> str:
        """Định dạng các câu mẫu thành chuỗi Markdown đưa vào Prompt."""
        examples = self.get_relevant_examples(user_query, top_k=top_k)
        lines = ["[CÁC VÍ DỤ CYPHER MẪU THAM KHẢO]:"]
        for i, ex in enumerate(examples, 1):
            lines.append(f"--- Ví dụ {i} ---")
            lines.append(f"Câu hỏi: {ex['question']}")
            lines.append(f"Cypher chuẩn:\n{ex['cypher']}\n")
        return "\n".join(lines)


# Singleton
few_shot_pool = FewShotPool()
