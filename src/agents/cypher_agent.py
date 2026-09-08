"""
Agent 2: Graph Cypher Specialist Agent.
Sử dụng OLM để sinh câu lệnh Cypher động 100% dựa trên Ontology, Quy tắc nghiệp vụ và Few-Shot mẫu.
Hỗ trợ vòng lặp tự sửa lỗi (Self-Correction) nếu câu Cypher bị báo lỗi cú pháp.
"""

import re
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import requests

# Đảm bảo đường dẫn gốc của project có trong sys.path khi chạy trực tiếp file
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.config import settings
from src.db.schema_provider import SchemaProvider
from src.memory.few_shot_pool import few_shot_pool
from src.memory.rules_store import rules_store

logger = logging.getLogger(__name__)


class CypherAgent:
    def __init__(self):
        self.model = settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_BASE_URL

    def build_system_prompt(self, user_question: str) -> str:
        """Tập hợp toàn bộ bối cảnh tri thức vào System Prompt cho OLM."""
        schema_context = SchemaProvider.get_full_schema_context()
        learned_rules = rules_store.format_rules_for_prompt()
        few_shots = few_shot_pool.format_examples_for_prompt(user_question, top_k=3)

        prompt = f"""Bạn là Chuyên gia Viết Truy vấn Cypher cho Neo4j 5.x phục vụ Phòng Đào tạo và Quản lý Sinh viên.
Nhiệm vụ của bạn là chuyển câu hỏi của cán bộ thành MỘT CÂU TRUY VẤN CYPHER CHÍNH XÁC, TỐI ƯU.

{schema_context}

{learned_rules}

{few_shots}

[YÊU CẦU ĐẦU RA BẮT BUỘC]:
1. Chỉ trả về DUY NHẤT câu truy vấn Cypher.
2. TUYỆT ĐỐI không viết thêm lời chào, giải thích, hay văn bản phụ.
3. Luôn sử dụng LIMIT {settings.DEFAULT_QUERY_LIMIT} nếu người dùng không yêu cầu số lượng cụ thể.
4. Đảm bảo đúng chiều mũi tên theo Bản đồ Đồ thị ở trên.
"""
        return prompt

    def generate_cypher(self, user_question: str, entities: Optional[Dict[str, Any]] = None) -> str:
        """Sinh câu lệnh Cypher từ câu hỏi người dùng."""
        system_prompt = self.build_system_prompt(user_question)
        user_prompt = f"Câu hỏi nghiệp vụ: {user_question}\n"
        if entities:
            user_prompt += f"Thực thể chuẩn xác từ Database: {entities}\n"
            if entities.get("student_name"):
                user_prompt += f"LƯU Ý: BẮT BUỘC dùng họ tên chuẩn xác từ Database là '{entities['student_name']}' khi viết điều kiện WHERE.\n"
        user_prompt += "Viết câu truy vấn Cypher:"

        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "system": system_prompt,
                "prompt": user_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1
                }
            }
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                raw_cypher = response.json().get("response", "").strip()
                return self._clean_cypher_output(raw_cypher, entities)
        except Exception as e:
            logger.warning("Không thể gọi OLM tại %s: %s", self.base_url, e)

        # Fallback từ điển mẫu nếu OLM chưa bật
        return self._fallback_cypher(user_question)

    def fix_cypher(self, failed_cypher: str, error_message: str, user_question: str) -> str:
        """Vòng lặp tự phản tỉnh và sửa câu lệnh Cypher khi Neo4j báo lỗi."""
        logger.info("Kích hoạt Self-Correction: Đang yêu cầu OLM sửa lỗi Cypher...")
        prompt = f"""Câu truy vấn Cypher trước đó bị lỗi khi thực thi trên Neo4j:
---
Câu hỏi: {user_question}
Câu Cypher bị lỗi:
{failed_cypher}
Thông báo lỗi từ Neo4j:
{error_message}
---
Hãy đọc kỹ thông báo lỗi, đối chiếu lại với Bản đồ Đồ thị và sửa lại thành một câu Cypher hợp lệ.
Chỉ trả về duy nhất câu Cypher mới đã sửa:"""

        system_prompt = self.build_system_prompt(user_question)
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "system": system_prompt,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0}
            }
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                raw_cypher = response.json().get("response", "").strip()
                return self._clean_cypher_output(raw_cypher)
        except Exception as e:
            logger.warning("Lỗi trong quá trình Self-Correction: %s", e)

        return failed_cypher

    def _clean_cypher_output(self, raw_output: str, entities: Optional[Dict[str, Any]] = None) -> str:
        """Lọc bỏ các khối markdown và tự động căn chỉnh dấu tiếng Việt theo thực thể DB chuẩn."""
        text = raw_output.strip()
        # Tìm khối ```cypher ... ```
        match = re.search(r"```(?:cypher)?\s*(.*?)\s*```", text, re.IGNORECASE | re.DOTALL)
        if match:
            text = match.group(1).strip()
        
        # Bỏ các dòng comment giải thích đầu/cuối nếu có
        lines = [line for line in text.splitlines() if not line.strip().startswith("//")]
        cleaned = "\n".join(lines).strip().rstrip(";").strip()
        result = cleaned if cleaned else text.rstrip(";").strip()

        # Tự động sửa lỗi chệch dấu thanh của OLM dựa vào thực thể Database chuẩn
        if entities and entities.get("student_name"):
            target_name = entities["student_name"]
            from src.db.entity_resolver import remove_vietnamese_accents
            target_clean = remove_vietnamese_accents(target_name)

            literals = re.findall(r"['\"]([^'\"]+)['\"]", result)
            for lit in literals:
                if remove_vietnamese_accents(lit) == target_clean and lit != target_name:
                    logger.info("Cypher Agent: Tự động sửa lệch dấu OLM '%s' -> '%s'", lit, target_name)
                    result = result.replace(f"'{lit}'", f"'{target_name}'").replace(f'"{lit}"', f'"{target_name}"')

        return result

    def _fallback_cypher(self, user_question: str) -> str:
        """Fallback mẫu câu gần nhất từ Few-Shot Pool khi OLM chưa sẵn sàng."""
        examples = few_shot_pool.get_relevant_examples(user_question, top_k=1)
        if examples:
            return examples[0]["cypher"].strip().rstrip(";").strip()
        return "MATCH (s:Student) RETURN s.student_code, s.program_code LIMIT 10"


cypher_agent = CypherAgent()
