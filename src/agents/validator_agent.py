"""
Agent 3: Guardrail & Validator Agent.
Thẩm định an toàn (Read-Only), kiểm tra cú pháp và điều phối vòng lặp tự sửa lỗi với Neo4j.
"""

import re
import logging
from typing import Dict, Any
from src.config import settings
from src.db.neo4j_client import neo4j_client
from src.agents.cypher_agent import cypher_agent

logger = logging.getLogger(__name__)


class ValidatorAgent:
    def __init__(self):
        self.max_retries = settings.MAX_CYPHER_RETRIES

    def validate_and_execute(self, cypher_query: str, user_question: str) -> Dict[str, Any]:
        """Thẩm định an toàn, thêm LIMIT nếu thiếu và thực thi an toàn trên Neo4j."""
        current_query = cypher_query.strip()

        # 1. Kiểm tra từ khóa bị cấm (Read-Only Guardrail)
        prohibited = [r"\bCREATE\b", r"\bMERGE\b", r"\bSET\b", r"\bDELETE\b", r"\bDETACH\b", r"\bDROP\b", r"\bREMOVE\b"]
        for p in prohibited:
            if re.search(p, current_query, re.IGNORECASE):
                return {
                    "success": False,
                    "cypher": current_query,
                    "records": [],
                    "error": f"Lệnh bị chặn: Phát hiện từ khóa thay đổi dữ liệu trái phép ({p}). Hệ thống chỉ hoạt động ở chế độ đọc."
                }

        # 2. Đảm bảo có mệnh đề LIMIT nếu truy vấn trả về danh sách
        if "RETURN" in current_query.upper() and "LIMIT" not in current_query.upper():
            current_query = f"{current_query}\nLIMIT {settings.DEFAULT_QUERY_LIMIT}"

        # 3. Vòng lặp thực thi và tự sửa lỗi (Self-Correction Loop)
        retries = 0
        last_error = None

        while retries <= self.max_retries:
            logger.info("Thực thi Cypher (lần thử %d): \n%s", retries + 1, current_query)
            result = neo4j_client.execute_read(current_query)

            if result["success"]:
                # Nếu thành công nhưng 0 kết quả, kiểm tra xem có thể tự phục hồi bằng thực thể chuẩn trong DB không
                if len(result["records"]) == 0 and "full_name" in current_query:
                    from src.db.entity_resolver import entity_resolver
                    best_person = entity_resolver.find_best_person_match(user_question, threshold=0.65)
                    if best_person:
                        healed_name = best_person["full_name"]
                        name_match = re.search(r"CONTAINS\s+toLower\(['\"]([^'\"]+)['\"]\)", current_query, re.IGNORECASE)
                        if name_match:
                            old_name = name_match.group(1)
                            if old_name.lower() != healed_name.lower():
                                healed_query = current_query.replace(f"'{old_name}'", f"'{healed_name}'").replace(f'"{old_name}"', f'"{healed_name}"')
                                logger.info("Validator Self-Healing: Thử phục hồi tên '%s' -> '%s'...", old_name, healed_name)
                                healed_res = neo4j_client.execute_read(healed_query)
                                if healed_res["success"] and len(healed_res["records"]) > 0:
                                    logger.info("Validator Self-Healing THÀNH CÔNG: Tìm thấy %d bản ghi cho '%s'",
                                                len(healed_res["records"]), healed_name)
                                    return {
                                        "success": True,
                                        "cypher": healed_query,
                                        "records": healed_res["records"],
                                        "count": len(healed_res["records"]),
                                        "retries": retries,
                                        "error": None
                                    }

                return {
                    "success": True,
                    "cypher": current_query,
                    "records": result["records"],
                    "count": len(result["records"]),
                    "retries": retries,
                    "error": None
                }

            last_error = result["error"]
            logger.warning("Truy vấn thất bại: %s", last_error)

            # Nếu lỗi kết nối (database offline), không cần retry gọi OLM sửa
            if "không thể kết nối" in str(last_error).lower() or "connection" in str(last_error).lower():
                break

            # Gọi OLM tự sửa cú pháp
            retries += 1
            if retries <= self.max_retries:
                current_query = cypher_agent.fix_cypher(current_query, last_error, user_question)

        return {
            "success": False,
            "cypher": current_query,
            "records": [],
            "count": 0,
            "retries": retries,
            "error": last_error
        }


validator_agent = ValidatorAgent()
