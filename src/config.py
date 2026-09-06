"""
Mô-đun cấu hình tập trung cho toàn bộ hệ thống Edu-Graph.
Đọc các biến môi trường từ .env.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Tìm file .env từ thư mục gốc
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class Settings:
    # Neo4j Database
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")

    # Local Quantized OLM via Ollama
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

    # Execution controls
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_CYPHER_RETRIES: int = int(os.getenv("MAX_CYPHER_RETRIES", "2"))
    DEFAULT_QUERY_LIMIT: int = int(os.getenv("DEFAULT_QUERY_LIMIT", "50"))

    # File Paths
    BASE_CYPHER_SCHEMA_PATH: Path = ROOT_DIR / "enterprise_dw_neo4j (1).cypher"
    MOCK_DATA_CYPHER_PATH: Path = ROOT_DIR / "data" / "seed_sample_data.cypher"


settings = Settings()
