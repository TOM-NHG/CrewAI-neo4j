"""
Điểm khởi chạy chính của Hệ thống Edu-Graph Multi-Agent Assistant.
Giao diện dòng lệnh tương tác (Interactive CLI) hỗ trợ Vòng lặp Phản hồi (Feedback Loop).
"""

import sys
import logging
from pathlib import Path

# Đảm bảo UTF-8 output trên Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Đảm bảo đường dẫn import
sys.path.append(str(Path(__file__).resolve().parent))

from src.config import settings
from src.db.neo4j_client import neo4j_client
from src.crew.edu_crew import edu_crew
from src.memory.feedback_manager import feedback_manager
from src.memory.rules_store import rules_store
from src.memory.few_shot_pool import few_shot_pool

logging.basicConfig(level=logging.WARNING)


def print_banner():
    banner = """
================================================================================
🎓 EDU-GRAPH MULTI-AGENT ASSISTANT 
   Hệ thống Trợ lý AI Quản lý Đào tạo & Sinh viên trên Đồ thị Neo4j 5.x
   100% Dynamic Semantic Reasoning | Local Quantized OLM (Qwen 2.5) | On-Premise
================================================================================
    """
    print(banner)


def check_environment():
    print("🔍 Đang kiểm tra môi trường hệ thống...")
    
    # 1. Kiểm tra Neo4j
    neo_status = neo4j_client.check_connection()
    if neo_status["status"] == "connected":
        print(f"  ✅ Neo4j: Đã kết nối thành công ({settings.NEO4J_URI})")
    else:
        print(f"  ⚠️  Neo4j: Chưa kết nối ({settings.NEO4J_URI})")
        print("     (Hệ thống vẫn sinh Cypher và kiểm tra cú pháp bình thường; hãy bật Neo4j khi cần thực thi thực tế)")

    # 2. Kiểm tra OLM / Ollama
    print(f"  🤖 OLM Model: {settings.OLLAMA_MODEL} tại {settings.OLLAMA_BASE_URL}")
    print(f"  📚 Kho Ví Dụ Mẫu (Few-Shot): Đang có {len(few_shot_pool.get_relevant_examples('', top_k=100))} mẫu câu chuẩn.")
    print(f"  🛡️ Sổ Tay Quy Tắc Ngữ Nghĩa: Đang có {len(rules_store.get_rules())} quy tắc nghiệp vụ.")
    print("-" * 80)
    print("Gợi ý câu hỏi bạn có thể thử:")
    print("  1. 'Cảnh báo những sinh viên có nguy cơ cấm thi vì vắng quá 20% môn Java?'")
    print("  2. 'Danh sách sinh viên đang bảo lưu trong học kỳ này?'")
    print("  3. 'Giảng viên Nguyễn Văn An đang dạy những lớp và buổi nào?'")
    print("  4. 'Ai là sinh viên vừa đi học vừa làm trợ giảng (TA)?'")
    print("  5. 'Xem điểm số và xếp loại của sinh viên Nguyễn Anh Tuấn'")
    print("  (Gõ 'exit' hoặc 'quit' để thoát)\n" + "=" * 80 + "\n")


def interactive_loop():
    print_banner()
    check_environment()

    while True:
        try:
            user_input = input("\n💬 Cán bộ Đào tạo hỏi: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "thoat", "q"]:
                print("\n👋 Tạm biệt! Hẹn gặp lại.")
                break

            print("\n⏳ Đang phân tích ngữ nghĩa và sinh truy vấn đồ thị Cypher...")
            result = edu_crew.process_query(user_input)

            # In kết quả báo cáo
            print("\n" + result["report"] + "\n")

            # Vòng lặp phản hồi người dùng (Feedback Loop)
            print("-" * 60)
            feedback = input("💡 Đánh giá câu trả lời này? (1: Đúng 👍 | 2: Chưa đúng 👎 | Enter để bỏ qua): ").strip()

            if feedback == "1":
                fb_res = feedback_manager.record_feedback(
                    user_question=user_input,
                    generated_cypher=result["cypher"],
                    is_correct=True
                )
                print(f"  ✅ {fb_res['message']}")
            elif feedback == "2":
                note = input("  📝 Vui lòng nhập lý do hoặc lưu ý (ví dụ: 'Không tính buổi LATE là vắng'): ").strip()
                corr_cypher = input("  🔧 Câu Cypher đúng (nếu có, hoặc nhấn Enter để bỏ qua): ").strip()
                fb_res = feedback_manager.record_feedback(
                    user_question=user_input,
                    generated_cypher=result["cypher"],
                    is_correct=False,
                    feedback_note=note if note else None,
                    corrected_cypher=corr_cypher if corr_cypher else None
                )
                print(f"  🎯 {fb_res['message']}")

        except KeyboardInterrupt:
            print("\n\nĐã dừng phiên làm việc.")
            break
        except Exception as e:
            print(f"\n❌ Đã xảy ra lỗi: {e}")


if __name__ == "__main__":
    interactive_loop()
