"""
Mô-đun quản lý kết nối và thực thi truy vấn an toàn tới Neo4j.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, Driver
from src.config import settings

logger = logging.getLogger(__name__)


class Neo4jClient:
    _instance: Optional["Neo4jClient"] = None

    def __init__(self):
        self._driver: Optional[Driver] = None
        self._connected: bool = False

    @classmethod
    def get_instance(cls) -> "Neo4jClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def connect(self) -> bool:
        if self._driver is not None and self._connected:
            return True
        try:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            # Verify connectivity
            self._driver.verify_connectivity()
            self._connected = True
            logger.info("Kết nối Neo4j thành công tại %s", settings.NEO4J_URI)
            return True
        except Exception as e:
            self._connected = False
            logger.warning("Không thể kết nối Neo4j tại %s: %s", settings.NEO4J_URI, e)
            return False

    def is_connected(self) -> bool:
        return self._connected

    def check_connection(self) -> Dict[str, Any]:
        success = self.connect()
        return {
            "status": "connected" if success else "disconnected",
            "uri": settings.NEO4J_URI,
            "database": settings.NEO4J_DATABASE
        }

    def execute_read(self, cypher_query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Thực thi câu lệnh Cypher chỉ đọc (Read-only).
        Chặn đứng các câu lệnh có chứa từ khóa ghi/sửa/xóa.
        """
        # Kiểm tra an toàn (Guardrail)
        prohibited = [r"\bCREATE\b", r"\bMERGE\b", r"\bSET\b", r"\bDELETE\b", r"\bDETACH\b", r"\bDROP\b", r"\bREMOVE\b"]
        for pattern in prohibited:
            if re.search(pattern, cypher_query, re.IGNORECASE):
                return {
                    "success": False,
                    "error": f"Lệnh bị chặn: Phát hiện từ khóa thay đổi dữ liệu trái phép ({pattern}) trong chế độ chỉ đọc.",
                    "records": []
                }

        if not self.connect():
            return {
                "success": False,
                "error": f"Không thể kết nối tới cơ sở dữ liệu Neo4j tại {settings.NEO4J_URI}.",
                "records": []
            }

        params = params or {}
        try:
            with self._driver.session(database=settings.NEO4J_DATABASE) as session:
                result = session.run(cypher_query, params)
                records = [record.data() for record in result]
                summary = result.consume()

                # Bắt các cảnh báo ảo giác nhãn hoặc quan hệ không tồn tại
                notifs = getattr(summary, "notifications", []) or []
                missing_schema_warnings = [
                    n.get("description") if isinstance(n, dict) else getattr(n, "description", str(n))
                    for n in notifs
                    if "UnknownRelationshipTypeWarning" in str(n) or "UnknownLabelWarning" in str(n)
                ]
                if missing_schema_warnings:
                    return {
                        "success": False,
                        "error": f"Lỗi cấu trúc đồ thị: {missing_schema_warnings[0]}. Hãy dùng đúng nhãn và quan hệ có trong ontology.",
                        "records": [],
                        "count": 0
                    }

                return {
                    "success": True,
                    "error": None,
                    "records": records,
                    "count": len(records)
                }
        except Exception as e:
            logger.error("Lỗi thực thi Cypher: %s", e)
            return {
                "success": False,
                "error": str(e),
                "records": []
            }

    def execute_write(self, cypher_query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Thực thi câu lệnh Cypher có ghi (dùng riêng cho khởi tạo schema/seed data).
        """
        if not self.connect():
            return {
                "success": False,
                "error": f"Không thể kết nối tới Neo4j tại {settings.NEO4J_URI}.",
                "summary": None
            }

        params = params or {}
        try:
            with self._driver.session(database=settings.NEO4J_DATABASE) as session:
                result = session.run(cypher_query, params)
                summary = result.consume()
                return {
                    "success": True,
                    "error": None,
                    "summary": {
                        "nodes_created": summary.counters.nodes_created,
                        "relationships_created": summary.counters.relationships_created,
                        "properties_set": summary.counters.properties_set
                    }
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary": None
            }

    def close(self):
        if self._driver:
            self._driver.close()
            self._connected = False
            logger.info("Đã đóng kết nối Neo4j.")


# Khởi tạo singleton instance
neo4j_client = Neo4jClient.get_instance()
