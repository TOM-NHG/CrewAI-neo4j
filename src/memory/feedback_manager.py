"""
Mô-đun quản lý phản hồi người dùng (Feedback Manager).
Hiện thực hóa Vòng lặp Học hỏi Ngữ nghĩa (Semantic Experience Loop):
- 👍 ĐÚNG: Lưu câu mẫu vào Dynamic Few-Shot Pool để tái sử dụng làm mẫu chuẩn.
- 👎 SAI: Trích xuất quy tắc cảnh báo nghiệp vụ và lưu vào Rules Store.
"""

import logging
from typing import Optional, Dict, Any
from src.memory.few_shot_pool import few_shot_pool
from src.memory.rules_store import rules_store

logger = logging.getLogger(__name__)


class FeedbackManager:
    @staticmethod
    def record_feedback(
        user_question: str,
        generated_cypher: str,
        is_correct: bool,
        feedback_note: Optional[str] = None,
        corrected_cypher: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tiếp nhận và xử lý phản hồi từ người dùng.
        Hoàn toàn không chạy thuật toán train lại model; chỉ cập nhật tri thức ngữ nghĩa.
        """
        if is_correct:
            few_shot_pool.add_verified_example(
                question=user_question,
                cypher=generated_cypher,
                intent="verified_user_query"
            )
            logger.info("Đã lưu câu hỏi và Cypher chuẩn vào Kho Ví Dụ Mẫu (Few-Shot Pool).")
            return {
                "success": True,
                "type": "positive",
                "message": "Cảm ơn bạn! Câu truy vấn này đã được lưu vào Kho Mẫu Chuẩn để OLM tham khảo."
            }
        else:
            msg_parts = []
            # Chỉ lưu câu Cypher nếu người dùng thực sự sửa đổi khác với câu lỗi do OLM sinh ra
            clean_corr = corrected_cypher.strip() if corrected_cypher else ""
            clean_gen = generated_cypher.strip() if generated_cypher else ""
            if clean_corr and clean_corr != clean_gen:
                few_shot_pool.add_verified_example(
                    question=user_question,
                    cypher=clean_corr,
                    intent="user_corrected_query"
                )
                msg_parts.append("Đã cập nhật câu Cypher sửa đổi vào Kho Mẫu.")

            # Nếu người dùng có ghi chú giải thích tại sao sai
            if feedback_note and feedback_note.strip():
                rules_store.add_rule(feedback_note.strip())
                msg_parts.append(f"Đã ghi nhận quy tắc cảnh báo mới: '{feedback_note.strip()}'.")

            if not msg_parts:
                msg_parts.append("Đã ghi nhận đánh giá để cải thiện.")

            return {
                "success": True,
                "type": "negative",
                "message": " ".join(msg_parts)
            }


feedback_manager = FeedbackManager()
