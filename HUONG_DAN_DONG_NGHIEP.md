# 🚀 HƯỚNG DẪN ĐỒNG BỘ 100% DỮ LIỆU DỰ ÁN CHO ĐỒNG NGHIỆP

> **Không cần server trung gian, không tốn chi phí Cloud.**  
> Bạn có thể tái tạo lại 100% dữ liệu đồ thị Neo4j (bao gồm toàn bộ sinh viên, lớp học, điểm danh, điểm thi, giảng viên và kho tri thức few-shot) ngay trên máy tính của bạn chỉ với **1 cú click**.

---

## 📋 Bước 1: Chuẩn bị môi trường máy cá nhân

Trước khi chạy, hãy đảm bảo máy tính của bạn đã có:
1. **Python >= 3.10**: Tải tại [python.org](https://www.python.org/downloads/) (nhớ tick chọn *"Add Python to PATH"* khi cài).
2. **Neo4j Database**:
   * **Cách A (Khuyên dùng)**: Tải và cài [Neo4j Desktop](https://neo4j.com/download/), tạo một Database 5.x cục bộ và bấm **Start** (Mặc định cổng `bolt://localhost:7687`).
   * **Cách B (Dành cho ai quen dùng Docker)**:
     ```bash
     docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.20.0
     ```
3. **(Tùy chọn) Ollama**: Nếu muốn chạy Local LLM, tải tại [ollama.com](https://ollama.com/) và tải model:
   ```bash
   ollama run qwen2.5:3b
   ```
   *(Nếu chưa cài Ollama, hệ thống vẫn có cơ chế Fallback để chạy thử nghiệm và kiểm thử bình thường).*

---

## ⚡ Bước 2: Tự động cài đặt & nạp 100% dữ liệu

### 👉 Cách nhanh nhất (Dành cho Windows):
1. Mở thư mục dự án trên máy bạn.
2. Kiểm tra file `.env` (nếu mật khẩu Neo4j của bạn khác `password`, hãy sửa lại dòng `NEO4J_PASSWORD=...`).
3. **Click đúp vào file `setup_colleague.bat`**.

Script sẽ tự động:
- Khởi tạo môi trường ảo Python (`.venv`)
- Cài đặt đầy đủ các thư viện (`requirements.txt`)
- Xóa sạch database trắng và nạp **100% dữ liệu chuẩn**:
  - Schema gốc và các quan hệ thực thể
  - 80 sinh viên mẫu đa dạng (bao gồm cả các trường hợp tên không dấu, đảo họ tên)
  - 100+ hoạt động học tập, lớp học phần, bảng điểm và điểm danh vắng cấm thi
  - Bản đồ Ontology chuyên ngành (`:Major`)
- Tự động chạy bộ Test tích hợp để xác nhận hệ thống hoạt động 100% Pass!

---

### 👉 Hoặc chạy thủ công bằng dòng lệnh (Terminal / PowerShell):

```bash
# 1. Khởi tạo và kích hoạt môi trường ảo
python -m venv .venv
.venv\Scripts\activate

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Tạo file cấu hình .env (nếu chưa có)
copy .env.example .env

# 4. Chạy script nạp 100% dữ liệu
python generate_rich_data.py

# 5. Kiểm thử xác nhận 100% Pass
python tests/test_pipeline.py
```

---

## 🖥️ Bước 3: Khởi chạy và Trải nghiệm

Sau khi nạp data xong, bạn có thể khởi chạy hệ thống bằng 2 cách:

1. **Giao diện Web NHG Design System (Khuyên dùng)**:
   ```bash
   python src/web_server.py
   ```
   Mở trình duyệt truy cập: **[http://localhost:8080](http://localhost:8080)**

2. **Giao diện Dòng lệnh (CLI Interactive)**:
   ```bash
   python main.py
   ```

---

## 🔄 Cách đồng bộ khi có dữ liệu mới phát sinh trong tương lai

Dự án có cơ chế **Semantic Experience Loop** (học hỏi từ phản hồi của người dùng).
Khi bạn hoặc đồng nghiệp chat và đánh giá:
- **👍 ĐÚNG**: Tự động bổ sung câu mẫu vào `data/verified_few_shots.json`.
- **👎 SAI**: Tự động bổ sung bài học cảnh báo vào `data/learned_rules.json`.

Để chia sẻ những gì AI vừa học được cho cả team:
* **Người cập nhật**: Commit và Push thư mục `data/` lên Git.
* **Người nhận**: Chỉ cần gõ `git pull` là AI trên máy bạn lập tức có chung dữ liệu tri thức mới mà không cần nạp lại database!
