"""
Kiểm thử tích hợp (Integration Tests) cho Hệ thống Edu-Graph Multi-Agent Assistant.
Chạy: .venv\Scripts\python tests/test_pipeline.py
"""

import sys
from pathlib import Path

# Đảm bảo UTF-8 output trên Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Thêm thư mục gốc vào đường dẫn
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.memory.few_shot_pool import few_shot_pool
from src.memory.rules_store import rules_store
from src.memory.feedback_manager import feedback_manager
from src.agents.router_agent import router_agent
from src.agents.cypher_agent import cypher_agent
from src.agents.validator_agent import validator_agent
from src.agents.reporter_agent import reporter_agent
from src.crew.edu_crew import edu_crew


def test_few_shot_retrieval():
    print("Test 1: Kiểm tra lấy ví dụ Few-Shot tương đồng...")
    query = "Sinh viên nào vắng quá 20% bị cấm thi?"
    examples = few_shot_pool.get_relevant_examples(query, top_k=2)
    assert len(examples) > 0, "Few-shot pool không được rỗng"
    assert any("vắng" in ex["question"].lower() for ex in examples), "Phải tìm thấy câu mẫu về vắng học"
    print("  ✅ Pass: Dynamic Few-Shot retrieval hoạt động chính xác.")


def test_guardrail_blocking():
    print("Test 2: Kiểm tra Guardrail chặn lệnh ghi/xóa dữ liệu...")
    malicious_query = "MATCH (s:Student) DETACH DELETE s;"
    res = validator_agent.validate_and_execute(malicious_query, "Xóa toàn bộ sinh viên")
    assert not res["success"], "Lệnh nguy hiểm phải bị chặn"
    assert "chế độ đọc" in res["error"] or "trái phép" in res["error"]
    print("  ✅ Pass: Guardrail chặn thành công câu lệnh DELETE.")


def test_feedback_loop():
    print("Test 3: Kiểm tra Vòng lặp Phản hồi (Feedback Loop)...")
    q = "Sinh viên tham gia hoạt động nghiên cứu khoa học"
    c = "MATCH (s:Student)-[:JOINS]->(r:Research) RETURN s;"
    
    # 1. Test feedback tích cực (👍)
    res_pos = feedback_manager.record_feedback(q, c, is_correct=True)
    assert res_pos["success"]
    
    # 2. Test feedback tiêu cực (👎) kèm bài học
    res_neg = feedback_manager.record_feedback(
        q, c, is_correct=False, feedback_note="Không có nhãn Research trong đồ thị hiện tại"
    )
    assert res_neg["success"]
    assert "Không có nhãn Research trong đồ thị hiện tại" in rules_store.get_rules()
    print("  ✅ Pass: Feedback Loop lưu trữ kinh nghiệm và quy tắc thành công.")


def test_end_to_end_pipeline():
    print("Test 4: Kiểm tra Pipeline End-to-End EduCrew...")
    q = "Danh sách sinh viên đang bảo lưu trong học kỳ này"
    result = edu_crew.process_query(q)
    assert "cypher" in result, "Phải sinh ra Cypher"
    assert "MATCH" in result["cypher"].upper(), "Cypher phải chứa MATCH"
    assert "report" in result, "Phải có báo cáo Markdown"
    print("  ✅ Pass: Pipeline 4 Agent xử lý trơn tru.")
    print("  Cypher sinh ra:\n", result["cypher"])


if __name__ == "__main__":
    print("========================================")
    print("🚀 BẮT ĐẦU KIỂM THỬ HỆ THỐNG EDU-GRAPH")
    print("========================================")
    test_few_shot_retrieval()
    test_guardrail_blocking()
    test_feedback_loop()
    test_end_to_end_pipeline()
    print("========================================")
    print("🎉 TẤT CẢ CÁC BÀI TEST ĐỀU THÀNH CÔNG (100% PASS)!")
    print("========================================")
