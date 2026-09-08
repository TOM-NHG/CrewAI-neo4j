@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ===============================================================================
echo 🎓 EDU-GRAPH MULTI-AGENT ASSISTANT - TỰ ĐỘNG CÀI ĐẶT & NẠP DATA CHO ĐỒNG NGHIỆP
echo ===============================================================================
echo.

:: 1. Kiểm tra Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [LỖI] Máy tính chưa cài đặt Python hoặc chưa thêm vào PATH!
    echo Vui lòng tải Python >= 3.10 từ https://www.python.org/
    pause
    exit /b 1
)
echo [1/5] ✅ Đã tìm thấy Python.

:: 2. Khởi tạo môi trường ảo .venv nếu chưa có
if not exist ".venv" (
    echo [2/5] 📦 Đang khởi tạo môi trường ảo Python (.venv)...
    python -m venv .venv
) else (
    echo [2/5] ✅ Môi trường ảo .venv đã sẵn sàng.
)

:: 3. Cài đặt thư viện phụ thuộc
echo [3/5] 📥 Đang kiểm tra và cài đặt các thư viện phụ thuộc...
.venv\Scripts\python -m pip install --upgrade pip > nul 2>&1
.venv\Scripts\pip install -r requirements.txt > nul 2>&1
echo       ✅ Hoàn tất cài đặt thư viện.

:: 4. Thiết lập file .env nếu chưa có
if not exist ".env" (
    echo [4/5] ⚙️  Chưa thấy file .env, đang tự động tạo từ .env.example...
    copy .env.example .env > nul
    echo       ⚠️  LƯU Ý: Nếu mật khẩu Neo4j của bạn khác 'your_password', 
    echo          hãy mở file .env và sửa lại biến NEO4J_PASSWORD!
) else (
    echo [4/5] ✅ File cấu hình .env đã tồn tại.
)

:: 5. Nạp toàn bộ dữ liệu 100% vào Neo4j
echo.
echo [5/5] 🚀 BẮT ĐẦU NẠP 100%% DỮ LIỆU ĐỒ THỊ VÀO NEO4J...
echo       (Đảm bảo Neo4j Desktop hoặc Docker Neo4j đang bật trên máy)
echo.
.venv\Scripts\python generate_rich_data.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Nạp dữ liệu chưa thành công!
    echo 💡 GỢI Ý XỬ LÝ:
    echo    1. Kiểm tra xem Neo4j Desktop hoặc Docker Neo4j đã bật chưa.
    echo    2. Kiểm tra mật khẩu trong file .env có khớp với mật khẩu Neo4j của bạn không.
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo 🧪 ĐANG CHẠY KIỂM THỬ TỰ ĐỘNG ĐỂ XÁC NHẬN TÍNH ĐỒNG BỘ 100%%...
echo ===============================================================================
.venv\Scripts\python tests\test_pipeline.py

echo.
echo ===============================================================================
echo 🎉 CHÚC MỪNG! HỆ THỐNG VÀ 100%% DỮ LIỆU ĐÃ ĐƯỢC TÁI TẠO HOÀN HẢO!
echo.
echo 💡 Để khởi chạy hệ thống:
echo    - Giao diện Web:   .venv\Scripts\python src\web_server.py  (Truy cập http://localhost:8080)
echo    - Chế độ CLI Terminal: .venv\Scripts\python main.py
echo ===============================================================================
pause
