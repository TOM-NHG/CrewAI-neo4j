"""
Script làm sạch toàn bộ dữ liệu cũ và nạp lại DUY NHẤT dữ liệu chuẩn của dự án:
- enterprise_dw_neo4j (1).cypher
- data/seed_sample_data.cypher
Chạy: .venv\\Scripts\\python reset_and_seed.py
"""

import sys
import logging
from pathlib import Path

# Đảm bảo UTF-8 output trên Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

from src.config import settings
from src.db.neo4j_client import neo4j_client
from src.db.seed_data import split_cypher_statements

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def reset_and_reload():
    logger.info("==================================================================")
    logger.info("🧹 BẮT ĐẦU LÀM SẠCH VÀ TÁI NẠP CƠ SỞ DỮ LIỆU NEO4J")
    logger.info("==================================================================")

    if not neo4j_client.connect():
        logger.error("❌ Không thể kết nối tới Neo4j tại %s. Hãy đảm bảo container đang chạy.", settings.NEO4J_URI)
        return False

    # 1. XÓA SẠCH TOÀN BỘ DỮ LIỆU CŨ TRONG DATABASE
    logger.info("🗑️ Đang xóa toàn bộ các nút và quan hệ cũ (DETACH DELETE)...")
    clear_res = neo4j_client.execute_write("MATCH (n) DETACH DELETE n")
    if not clear_res["success"]:
        logger.error("Lỗi khi xóa dữ liệu: %s", clear_res["error"])
        return False
    logger.info("✅ Đã dọn dẹp sạch sẽ toàn bộ database.")

    # 2. NẠP SCHEMA VÀ DATA TỪ enterprise_dw_neo4j (1).cypher
    schema_file = ROOT_DIR / "enterprise_dw_neo4j (1).cypher"
    if schema_file.exists():
        logger.info("📥 Đang nạp Schema gốc: %s", schema_file.name)
        with open(schema_file, "r", encoding="utf-8") as f:
            content = f.read()
        statements = split_cypher_statements(content)
        success_count = 0
        for i, stmt in enumerate(statements, 1):
            res = neo4j_client.execute_write(stmt)
            if res["success"]:
                success_count += 1
            else:
                logger.warning("Lệnh %d lỗi: %s", i, res["error"])
        logger.info("✅ Hoàn tất Schema gốc: %d/%d câu lệnh thành công.", success_count, len(statements))

    # 3. NẠP DỮ LIỆU MẪU MỞ RỘNG TỪ data/seed_sample_data.cypher
    mock_file = ROOT_DIR / "data" / "seed_sample_data.cypher"
    if mock_file.exists():
        logger.info("📥 Đang nạp Dữ liệu Mẫu Mở Rộng: %s", mock_file.name)
        with open(mock_file, "r", encoding="utf-8") as f:
            mock_content = f.read()
        mock_statements = split_cypher_statements(mock_content)
        mock_success = 0
        for i, stmt in enumerate(mock_statements, 1):
            res = neo4j_client.execute_write(stmt)
            if res["success"]:
                mock_success += 1
            else:
                logger.warning("Khối mẫu %d lỗi: %s", i, res["error"])
        logger.info("✅ Hoàn tất Dữ liệu Mẫu: %d/%d khối thành công.", mock_success, len(mock_statements))

    # 4. KIỂM KÊ TỔNG THỂ DỮ LIỆU MỚI TRONG NEO4J
    logger.info("\n📊 KIỂM KÊ DỮ LIỆU CHUẨN TRONG NEO4J:")
    res_nodes = neo4j_client.execute_read("""
        MATCH (n)
        RETURN labels(n) AS label, count(n) AS count
        ORDER BY count DESC
    """)
    if res_nodes["success"]:
        for r in res_nodes["records"]:
            logger.info("  - Nút %s: %s", r["label"], r["count"])

    res_rels = neo4j_client.execute_read("""
        MATCH ()-[r]->()
        RETURN type(r) AS rel_type, count(r) AS count
        ORDER BY count DESC
    """)
    if res_rels["success"]:
        logger.info("🔗 DANH SÁCH QUAN HỆ CHUẨN:")
        for r in res_rels["records"]:
            logger.info("  - Cạnh %s: %s", r["rel_type"], r["count"])

    logger.info("==================================================================")
    logger.info("🎉 CƠ SỞ DỮ LIỆU NEO4J ĐÃ ĐƯỢC LÀM SẠCH VÀ TÁI NẠP HOÀN TOÀN!")
    logger.info("==================================================================")
    return True


if __name__ == "__main__":
    reset_and_reload()
