"""
Script tự động nạp Schema và Bộ Dữ Liệu Mẫu (Mock Data) vào Neo4j.
Chạy trực tiếp: python src/db/seed_data.py
"""

import sys
import logging
from pathlib import Path

# Thêm thư mục gốc vào PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.config import settings
from src.db.neo4j_client import neo4j_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def split_cypher_statements(cypher_text: str):
    """
    Tách file Cypher thành từng câu lệnh riêng lẻ để thực thi.
    Bỏ qua các comment (//) và dòng trống.
    """
    # Xóa các comment dòng
    lines = []
    for line in cypher_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("//") or not stripped:
            continue
        lines.append(line)
    
    clean_text = "\n".join(lines)
    # Tách bằng dấu chấm phẩy ';'
    statements = [stmt.strip() for stmt in clean_text.split(";") if stmt.strip()]
    return statements


def seed_database():
    logger.info("Bắt đầu quy trình nạp dữ liệu mẫu vào Neo4j...")
    
    # 1. Kiểm tra kết nối
    if not neo4j_client.connect():
        logger.error(
            "\n❌ KHÔNG THỂ KẾT NỐI TỚI NEO4J tại: %s\n"
            "Vui lòng đảm bảo Neo4j đã được khởi động.\n"
            "- Nếu dùng Docker, bạn có thể chạy lệnh:\n"
            "  docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/%s neo4j:5.20.0\n"
            "- Hoặc khởi động database trên Neo4j Desktop.",
            settings.NEO4J_URI,
            settings.NEO4J_PASSWORD
        )
        return False

    # 2. Đọc file Schema gốc (nếu có)
    base_file = settings.BASE_CYPHER_SCHEMA_PATH
    if base_file.exists():
        logger.info("Đang nạp Schema gốc từ: %s", base_file.name)
        with open(base_file, "r", encoding="utf-8") as f:
            base_content = f.read()
        
        statements = split_cypher_statements(base_content)
        logger.info("Tìm thấy %d câu lệnh trong Schema gốc.", len(statements))
        success_count = 0
        for i, stmt in enumerate(statements, 1):
            res = neo4j_client.execute_write(stmt)
            if res["success"]:
                success_count += 1
            else:
                # Bỏ qua lỗi đã tồn tại constraint
                if "already exists" not in res["error"].lower():
                    logger.debug("Lệnh %d: %s", i, res["error"])
        logger.info("Đã hoàn tất nạp Schema gốc (%d/%d câu lệnh).", success_count, len(statements))

    # 3. Đọc file Dữ liệu Mẫu Mở Rộng
    mock_file = settings.MOCK_DATA_CYPHER_PATH
    if mock_file.exists():
        logger.info("Đang nạp Dữ liệu Mẫu Mở Rộng từ: %s", mock_file.name)
        with open(mock_file, "r", encoding="utf-8") as f:
            mock_content = f.read()
        
        mock_statements = split_cypher_statements(mock_content)
        logger.info("Tìm thấy %d khối câu lệnh dữ liệu mẫu.", len(mock_statements))
        mock_success = 0
        for i, stmt in enumerate(mock_statements, 1):
            res = neo4j_client.execute_write(stmt)
            if res["success"]:
                mock_success += 1
            else:
                logger.warning("Lỗi khi chạy khối %d: %s", i, res["error"])
        logger.info("Đã hoàn tất nạp Dữ liệu Mẫu (%d/%d khối thành công).", mock_success, len(mock_statements))

    # 4. Thống kê số lượng Nút & Quan hệ sau khi nạp
    count_query = """
    MATCH (n)
    RETURN labels(n) AS label, count(n) AS count
    ORDER BY count DESC
    """
    res = neo4j_client.execute_read(count_query)
    if res["success"]:
        logger.info("\n📊 THỐNG KÊ DỮ LIỆU HIỆN CÓ TRONG NEO4J:")
        for r in res["records"]:
            logger.info("  - Nhãn %s: %s nút", r["label"], r["count"])

    rel_query = """
    MATCH ()-[r]->()
    RETURN type(r) AS rel_type, count(r) AS count
    ORDER BY count DESC
    """
    rel_res = neo4j_client.execute_read(rel_query)
    if rel_res["success"]:
        logger.info("🔗 QUAN HỆ TRONG ĐỒ THỊ:")
        for r in rel_res["records"]:
            logger.info("  - Quan hệ %s: %s cạnh", r["rel_type"], r["count"])

    logger.info("✅ DỮ LIỆU ĐÃ SẴN SÀNG ĐỂ KIỂM THỬ TRUY VẤN!")
    return True


if __name__ == "__main__":
    seed_database()
