#!/usr/bin/env bash
# ==============================================================================
# 🎓 EDU-GRAPH MULTI-AGENT ASSISTANT - SERVICE STARTER SCRIPT
# Tự động kiểm tra và khởi động toàn bộ dịch vụ (Neo4j, Ollama, Web Server)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo "================================================================================"
echo "🚀 KHỞI ĐỘNG HỆ THỐNG EDU-GRAPH MULTI-AGENT ASSISTANT"
echo "================================================================================"

# 1. Xác định môi trường Python
if [ -d ".venv" ] && [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Lỗi: Không tìm thấy Python! Vui lòng cài đặt Python 3.10+."
    exit 1
fi
echo "🐍 Python: $($PYTHON_CMD --version) ($PYTHON_CMD)"

# 2. Kiểm tra & Khởi động Neo4j (qua Docker Compose nếu có)
echo ""
echo "📦 [1/3] Kiểm tra Cơ sở dữ liệu đồ thị Neo4j (Port 7687, 7474)..."
if nc -z localhost 7687 2>/dev/null || nc -z 127.0.0.1 7687 2>/dev/null; then
    echo "   ✅ Neo4j đang hoạt động tại bolt://localhost:7687"
else
    if command -v docker &>/dev/null; then
        echo "   🔄 Đang khởi động Neo4j container qua Docker Compose..."
        docker compose up -d neo4j 2>/dev/null || docker-compose up -d neo4j 2>/dev/null || {
            echo "   ⚠️ Không thể bật container tự động. Bạn hãy chạy: docker compose up -d"
        }
        # Đợi tối đa 15s cho Neo4j khởi động
        for i in {1..15}; do
            if nc -z localhost 7687 2>/dev/null || nc -z 127.0.0.1 7687 2>/dev/null; then
                echo "   ✅ Neo4j đã sẵn sàng!"
                break
            fi
            sleep 1
        done
    else
        echo "   ⚠️ Không tìm thấy Docker hoặc Neo4j chưa bật. Hệ thống sẽ chạy ở chế độ fallback/dry-run nếu không có DB."
    fi
fi

# 3. Kiểm tra & Khởi động Ollama (Local OLM)
echo ""
echo "🤖 [2/3] Kiểm tra Mô hình ngôn ngữ Ollama (Port 11434)..."
if nc -z localhost 11434 2>/dev/null || nc -z 127.0.0.1 11434 2>/dev/null; then
    echo "   ✅ Ollama server đang hoạt động tại http://localhost:11434"
else
    if command -v ollama &>/dev/null; then
        echo "   🔄 Đang chạy ngầm 'ollama serve'..."
        ollama serve > /dev/null 2>&1 &
        sleep 2
        echo "   ✅ Ollama đã được kích hoạt."
    else
        echo "   ⚠️ Không tìm thấy lệnh 'ollama'. Vui lòng đảm bảo Ollama đang chạy tại http://localhost:11434"
    fi
fi

# Kiểm tra model qwen2.5:3b nếu ollama có sẵn
if command -v ollama &>/dev/null; then
    if ! ollama list 2>/dev/null | grep -q "qwen2.5:3b"; then
        echo "   📥 Đang tải mô hình qwen2.5:3b (chỉ tải lần đầu)..."
        ollama pull qwen2.5:3b || echo "   ⚠️ Chưa tải được model, hãy chạy: ollama pull qwen2.5:3b"
    fi
fi

# 4. Khởi động Web Server
echo ""
echo "🌐 [3/3] Khởi động Edu-Graph Web Server (Port 8080)..."
echo "   👉 Giao diện Web: http://localhost:8080"
echo "   👉 Neo4j Browser: http://localhost:7474 (user: neo4j / pass: password)"
echo ""
echo "================================================================================"
echo "⚡ Hệ thống sẵn sàng! Nhấn Ctrl+C để dừng Web Server."
echo "================================================================================"

exec "$PYTHON_CMD" src/web_server.py
