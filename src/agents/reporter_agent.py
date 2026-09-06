"""
Agent 4: Reporter & Synthesizer Agent.
Chuyển đổi dữ liệu thô từ Neo4j thành báo cáo và bảng biểu tiếng Việt rõ ràng, chuyên nghiệp.
"""

from typing import List, Dict, Any
from tabulate import tabulate


class ReporterAgent:
    def format_report(self, user_question: str, query_result: Dict[str, Any]) -> str:
        """Định dạng kết quả truy vấn thành báo cáo trực quan cho cán bộ đào tạo."""
        if not query_result["success"]:
            error_msg = query_result.get("error", "Lỗi không xác định")
            return (
                f"⚠️ **Không thể truy xuất dữ liệu**\n\n"
                f"- **Lý do**: {error_msg}\n"
                f"- **Câu lệnh Cypher đã thử**:\n```cypher\n{query_result.get('cypher', '')}\n```\n"
                f"*Gợi ý*: Vui lòng kiểm tra lại kết nối cơ sở dữ liệu Neo4j hoặc điều chỉnh câu hỏi."
            )

        records: List[Dict[str, Any]] = query_result.get("records", [])
        if not records:
            return (
                f"ℹ️ **Kết quả tra cứu**: Không tìm thấy dữ liệu nào phù hợp với câu hỏi của bạn trong hệ thống.\n\n"
                f"- **Câu lệnh Cypher đã thực thi**:\n```cypher\n{query_result.get('cypher', '')}\n```"
            )

        # Trích xuất tiêu đề cột và hàng
        headers = list(records[0].keys())
        rows = [[row.get(h, "") for h in headers] for row in records]

        # Tạo bảng định dạng Markdown
        table_md = tabulate(rows, headers=headers, tablefmt="github")

        # Đánh giá cảnh báo nếu có cột absent_rate hoặc cấm thi
        warnings = []
        for row in records:
            # Kiểm tra nếu có cảnh báo vắng > 20%
            for k, v in row.items():
                if "absent" in k.lower() and isinstance(v, (int, float)) and v >= 20.0:
                    student_name = row.get("student_name") or row.get("full_name") or "Sinh viên"
                    warnings.append(f"- 🚨 **CẢNH BÁO**: Sinh viên `{student_name}` có tỷ lệ vắng {v}% (vượt ngưỡng 20% cấm thi)!")

        response_parts = [
            f"### 📊 KẾT QUẢ TRA CỨU ĐÀO TẠO ({len(records)} bản ghi):",
            table_md,
            ""
        ]

        if warnings:
            response_parts.append("### ⚠️ LƯU Ý HỌC VỤ:")
            response_parts.extend(warnings)
            response_parts.append("")

        response_parts.append(f"<details><summary>🔍 Xem câu lệnh Cypher đã sinh</summary>\n\n```cypher\n{query_result.get('cypher', '')}\n```\n</details>")

        return "\n".join(response_parts)


reporter_agent = ReporterAgent()
