"""
Quy trình điều phối Đa Tác Nhân (Multi-Agent Workflow / EduCrew).
Kết nối 4 Agent: Router -> Cypher Specialist -> Validator -> Reporter.
100% Dynamic Semantic Reasoning, không dùng Fast-Path.
"""

import time
import logging
from typing import Dict, Any, Optional
from src.config import settings
from src.agents.router_agent import router_agent
from src.agents.cypher_agent import cypher_agent
from src.agents.validator_agent import validator_agent
from src.agents.reporter_agent import reporter_agent

logger = logging.getLogger(__name__)


class EduCrew:
    def __init__(self):
        self.router = router_agent
        self.cypher_gen = cypher_agent
        self.validator = validator_agent
        self.reporter = reporter_agent

    def process_query(self, user_question: str, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Thực thi quy trình xử lý câu hỏi qua 4 Agent chuyên môn:
        1. Router Agent bóc tách ý định & thực thể
        2. Cypher Specialist Agent sinh câu lệnh Cypher động
        3. Validator Agent thẩm định cú pháp, an toàn và thực thi trên Neo4j
        4. Reporter Agent tổng hợp bảng biểu và phân tích
        Đo lường độ trễ (latency breakdown) chi tiết từng bước.
        """
        active_model = model_name or settings.OLLAMA_MODEL
        if model_name:
            self.router.model = model_name
            self.cypher_gen.model = model_name

        logger.info("Bắt đầu xử lý câu hỏi: '%s' (Mô hình: %s)", user_question, active_model)
        t_start = time.perf_counter()

        # Bước 1: Phân tích ý định & Thực thể (Router Agent)
        t0 = time.perf_counter()
        analysis = self.router.analyze(user_question)
        t1 = time.perf_counter()
        latency_router_ms = round((t1 - t0) * 1000, 1)

        intent = analysis.get("intent", "general_query")
        entities = analysis.get("entities", {})
        logger.info("Agent 1 (Router): Intent=%s | Entities=%s | Độ trễ: %.1f ms", intent, entities, latency_router_ms)

        # Bước 1.5: Đối chiếu thực thể với Database (Ground Truth Entity Resolution)
        from src.db.entity_resolver import entity_resolver
        entities = entity_resolver.resolve_query_context(user_question, entities)
        if entities.get("student_name"):
            logger.info("Entity Resolver: Đã khớp thực thể chuẩn trong Database -> %s (Mã: %s)",
                        entities["student_name"], entities.get("matched_student_code"))

        # Bước 2: Sinh câu lệnh Cypher Động (Cypher Specialist Agent)
        t2_start = time.perf_counter()
        cypher_query = self.cypher_gen.generate_cypher(user_question, entities)
        t2 = time.perf_counter()
        latency_cypher_ms = round((t2 - t2_start) * 1000, 1)
        logger.info("Agent 2 (Cypher Specialist): Độ trễ: %.1f ms\n%s", latency_cypher_ms, cypher_query)

        # Bước 3: Thẩm định & Thực thi với Neo4j (Validator Agent + Self-Correction)
        t3_start = time.perf_counter()
        execution_result = self.validator.validate_and_execute(cypher_query, user_question)
        t3 = time.perf_counter()
        latency_neo4j_ms = round((t3 - t3_start) * 1000, 1)
        logger.info("Agent 3 (Validator): Thành công=%s | Số bản ghi=%d | Độ trễ: %.1f ms", 
                    execution_result["success"], execution_result.get("count", 0), latency_neo4j_ms)

        # Bước 4: Tổng hợp báo cáo Markdown (Reporter Agent)
        t4_start = time.perf_counter()
        report = self.reporter.format_report(user_question, execution_result)
        t4 = time.perf_counter()
        latency_reporter_ms = round((t4 - t4_start) * 1000, 1)

        total_latency_sec = round(t4 - t_start, 2)
        total_latency_ms = round((t4 - t_start) * 1000, 1)

        logger.info("Hoàn tất pipeline: Tổng độ trễ = %.2f s (Router: %.1f ms, Cypher: %.1f ms, Neo4j: %.1f ms, Reporter: %.1f ms)",
                    total_latency_sec, latency_router_ms, latency_cypher_ms, latency_neo4j_ms, latency_reporter_ms)

        return {
            "question": user_question,
            "intent": intent,
            "entities": entities,
            "cypher": execution_result.get("cypher", cypher_query),
            "success": execution_result.get("success", False),
            "records": execution_result.get("records", []),
            "count": execution_result.get("count", 0),
            "report": report,
            "model": active_model,
            "latency": {
                "total_seconds": total_latency_sec,
                "total_ms": total_latency_ms,
                "router_ms": latency_router_ms,
                "cypher_ms": latency_cypher_ms,
                "neo4j_ms": latency_neo4j_ms,
                "reporter_ms": latency_reporter_ms
            }
        }


edu_crew = EduCrew()
