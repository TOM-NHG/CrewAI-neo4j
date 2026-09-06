# 🎓 Edu-Graph Multi-Agent Assistant

> **Hệ thống Trợ lý AI Đa Tác Nhân Quản Lý Đào Tạo & Sinh Viên Trên Cơ Sở Dữ Liệu Đồ Thị Neo4j**  
> Tích hợp mô hình ngôn ngữ lớn cục bộ (Local LLM via Ollama), kiến trúc đa tác nhân (CrewAI Multi-Agent Architecture), cơ chế tự học hỏi ngữ nghĩa (Semantic Experience Loop), và bộ giải đoán thực thể thông minh (Database-Grounded Entity Resolution).

---

## 🌟 Tính Năng Nổi Bật

- 🔒 **100% Cục bộ & Bảo mật (On-Premise Privacy)**: Chạy hoàn toàn bằng các mô hình OLM lượng tử hóa (Quantized Qwen 2.5 3B / 7B Q4_K_M via Ollama), dữ liệu không bao giờ rời khỏi hạ tầng nội bộ.
- 🧠 **Dynamic Cypher Generation**: Sinh câu truy vấn Cypher động 100% dựa trên Bản đồ Đồ thị tối giản (Compact Graph Ontology), Từ điển nghiệp vụ Đào tạo và Kho mẫu Few-Shot thích ứng.
- 🎯 **Database-Grounded Entity Resolver**: Tự động nhận diện và đoán đúng thực thể từ Neo4j ngay cả khi người dùng:
  - Gõ sai dấu thanh tiếng Việt (ví dụ: *`lé khắc tiệp`* $\rightarrow$ *`Lê Khắc Tiệp`*)
  - Gõ hoàn toàn không dấu (ví dụ: *`le khac tiep`* $\rightarrow$ *`Lê Khắc Tiệp`*)
  - Đảo trật tự họ tên (ví dụ: *`duyên đặng`* $\rightarrow$ *`Đặng Thị Mỹ Duyên`*)
  - Gõ nhầm 1-2 ký tự (Fuzzy typo matching với độ tương đồng > 75%)
- 🛡️ **Bảo vệ Đọc An toàn (Read-Only Guardrail & Self-Correction)**:
  - Ngăn chặn triệt để các hành vi thay đổi dữ liệu trái phép (`CREATE`, `MERGE`, `SET`, `DELETE`, `DROP`).
  - Vòng lặp tự sửa lỗi Cypher khi Neo4j báo lỗi cú pháp.
  - Vòng lặp tự phục hồi (Self-Healing) khi kết quả trả về 0 bản ghi do lệch tên gọi.
- 🔁 **Semantic Experience Loop (Tự học qua phản hồi)**:
  - **👍 ĐÚNG**: Tự động lưu câu hỏi và câu Cypher tối ưu vào Kho Ví Dụ Mẫu (Dynamic Few-Shot Pool).
  - **👎 SAI**: Trích xuất quy tắc cảnh báo vào Sổ Tay Nghiệp Vụ (Rules Store) để OLM không lặp lại sai lầm.
- 💻 **Giao diện Web Hiện Đại (NHG Design System)**:
  - Giao diện Dark/Light theme chuẩn hệ thống nhận diện NHG với bảng màu HSL, hiệu ứng Glassmorphism và micro-animations.
  - Đồng hồ bấm giờ suy luận thời gian thực (Live Inference Timer).
  - Huy hiệu phân rã độ trễ (Latency Breakdown): Router, Cypher Specialist, Neo4j, Reporter.
  - Bộ chọn mô hình OLM trực tiếp trên thanh Navbar (`qwen2.5:7b`, `qwen2.5:3b`, `qwen2.5:1.5b`).
  - Hộp phản hồi (Feedback Modal) và bảng kết quả hiển thị dạng Accordion cho phép kiểm tra trực tiếp mã Cypher.

---

## 🏛️ Kiến Trúc Hệ Thống (Multi-Agent Pipeline)

```mermaid
flowchart TD
    User([👤 Cán bộ Đào tạo / QLSV]) -->|Câu hỏi nghiệp vụ tự nhiên| WebUI[🌐 Giao diện Web NHG / API]
    WebUI --> Crew[🚀 EduCrew Multi-Agent Engine]
    
    subgraph Pipeline [Quy Trình Xử Lý Đa Tác Nhân]
        Crew --> Agent1[🎯 Agent 1: Router & Semantic Extractor]
        Agent1 -->|Ý định & Thực thể thô| Resolver[🔍 Database-Grounded Entity Resolver]
        Resolver -->|Đối chiếu Neo4j Cache < 1ms| ResolvedEntities[✨ Thực thể chuẩn xác trong DB]
        
        ResolvedEntities --> Agent2[💻 Agent 2: Cypher Specialist Agent]
        Rules[(📘 Rules Store)] -.-> Agent2
        FewShots[(📗 Few-Shot Pool)] -.-> Agent2
        Ontology[(🗺️ Compact Ontology)] -.-> Agent2
        
        Agent2 -->|Câu lệnh Cypher tối ưu| Agent3[🛡️ Agent 3: Guardrail & Validator]
        Agent3 -->|Thực thi an toàn Read-Only| DB[(⚡ Neo4j Graph Database)]
        DB -->|Kết quả bản ghi| Agent3
        
        Agent3 -.->|Tự sửa lỗi cú pháp & Self-Healing| Agent2
        Agent3 --> Agent4[📊 Agent 4: Reporter & Synthesizer]
    end
    
    Agent4 -->|Báo cáo Markdown & Bảng số liệu| WebUI
    WebUI -->|Đánh giá 👍 / 👎| FeedbackMgr[🔁 Feedback Manager]
    FeedbackMgr -.->|Cập nhật câu mẫu| FewShots
    FeedbackMgr -.->|Ghi nhận cảnh báo| Rules
```

---

## 👥 Các Tác Nhân Chuyên Biệt (CrewAI Agents)

| Tác nhân | Vai trò & Nhiệm vụ |
| :--- | :--- |
| **🎯 Router Agent** | Phân loại ý định nghiệp vụ (`attendance_query`, `warning_query`, `status_query`, `lecturer_query`, `grade_query`, `general_query`) và bóc tách thực thể thô. |
| **🔍 Entity Resolver** | Ánh xạ và chuẩn hóa thực thể đối chiếu trực tiếp với dữ liệu Neo4j (khử dấu, sửa lỗi chính tả, hoán vị họ tên). |
| **💻 Cypher Specialist Agent** | Tổng hợp tri thức từ Ontology, Sổ tay quy tắc và Kho Few-shot mẫu để sinh câu lệnh Cypher chuẩn Neo4j 5.x. |
| **🛡️ Validator Agent** | Kiểm tra an toàn Read-Only, tự động thêm LIMIT, tự sửa lỗi cú pháp (Self-Correction) và tự phục hồi khi truy vấn tên trả về 0 kết quả (Self-Healing). |
| **📊 Reporter Agent** | Tổng hợp kết quả bản ghi thành bảng biểu Markdown trực quan, tóm tắt chỉ số và đưa ra nhận định chuyên môn. |

---

## 🗺️ Mô Hình Dữ Liệu Đồ Thị (Party Model Ontology)

Hệ thống áp dụng mô hình thực thể Party Model chuẩn mực trong cơ sở dữ liệu đồ thị:

```
(:Person {national_id, full_name, date_of_birth, gender, email, phone})
   ├── [:HAS_ROLE] ──► (:Student {student_code, enrollment_date, program_code, is_active})
   └── [:HAS_ROLE] ──► (:Employee {employee_code, hire_date, is_active})

(:Student) ──[:STUDIES_AT]──► (:Organization {org_code, org_name, org_type})
(:Student) ──[:ENROLLED_IN]──► (:Class {class_code, class_name, max_capacity})
(:Student) ──[:PARTICIPATED_IN {attendance_status, quiz_score, grade}]──► (:Activity)
(:Student) ──[:HAS_STATUS {status: 'ACTIVE'|'SUSPENDED'|'DROPOUT'|'GRADUATED'}]──► (:Student)

(:Employee) ──[:ASSIGNED_TO_DEPT {position_code}]──► (:Department)
(:Employee) ──[:LEADS {role: 'PRIMARY_LECTURER'|'TA'}]──► (:Activity)
(:Activity) ──[:PART_OF]──► (:Class)
(:Class) ──[:OFFERED_IN]──► (:AcademicPeriod)
```

---

## 📦 Yêu Cầu Cài Đặt

1. **Python**: Phiên bản `>= 3.10`
2. **Neo4j**: Phiên bản `>= 5.x` (hỗ trợ Neo4j Desktop, Neo4j Community Server hoặc Docker)
3. **Ollama**: Đã cài đặt và đang chạy ngầm trên máy cục bộ (`localhost:11434`)

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Clone Kho Mã Nguồn
```bash
git clone https://github.com/TOM-NHG/CrewAI-neo4j.git
cd CrewAI-neo4j
```

### 2. Thiết Lập Môi Trường Ảo & Cài Đặt Thư Viện
```bash
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt trên Windows:
.\.venv\Scripts\activate
# Kích hoạt trên Linux/macOS:
# source .venv/bin/activate

# Cài đặt thư viện phụ thuộc
pip install -r requirements.txt
```

### 3. Cấu Hình Biến Môi Trường (`.env`)
Sao chép từ file mẫu và chỉnh sửa thông số kết nối nếu cần:
```bash
cp .env.example .env
```

Nội dung cấu hình mặc định trong `.env`:
```ini
# Neo4j Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# Local Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
DEFAULT_QUERY_LIMIT=50
MAX_CYPHER_RETRIES=2
```

### 4. Kéo Mô Hình Ollama Cục Bộ
```bash
# Mô hình 3B (nhẹ, phản hồi nhanh ~15-20s trên CPU/GPU thông thường)
ollama pull qwen2.5:3b

# Mô hình 7B (suy luận sâu, chất lượng cao nhất)
ollama pull qwen2.5:7b
```

### 5. Nạp Dữ Liệu Mẫu Vào Neo4j
Chạy tập lệnh sinh dữ liệu thực tế (hơn 60 Person, 48 Student, 14 Class, 45 Activity và 190+ quan hệ điểm danh):
```bash
python generate_rich_data.py
```

### 6. Khởi Chạy Ứng Dụng

#### Cách A: Khởi chạy Giao Diện Web (Khuyên dùng)
```bash
python src/web_server.py
```
👉 Mở trình duyệt và truy cập: **`http://localhost:8080`**

#### Cách B: Chạy Chế Độ Dòng Lệnh (CLI Interactive Mode)
```bash
python main.py
```

---

## 💡 Ví Dụ Câu Hỏi Nghiệp Vụ Mẫu

Bạn có thể thử nghiệm trực tiếp các câu hỏi thực tế sau trên giao diện:

### 1. Điểm danh & Cảnh báo cấm thi
- *"Cảnh báo những sinh viên có nguy cơ cấm thi vì vắng quá 20% môn Java"*
- *"sinh viên cơ sở hà nội bị cấm thi"*
- *"Tìm những sinh viên vắng mặt ở lớp PRO192_SE1801 ngày 2024-09-02"*
- *"Danh sách sinh viên đi muộn trong các buổi học"*

### 2. Tra cứu hồ sơ & Khử lỗi gõ dấu
- *"hồ sơ sinh viên lê khắc tiệp"* *(thử gõ `lé khắc tiệp` hoặc `le khac tiep` để kiểm chứng Entity Resolver)*
- *"hồ sơ duyên đặng"* *(đảo thứ tự họ tên)*
- *"Tra cứu thông tin sinh viên mã SE180001"*

### 3. Ngành học & Cơ sở đào tạo
- *"những sinh viên ngành SE"*
- *"SINH VIÊN NGÀNH SE CƠ SỞ HÀ NỘI"*
- *"Danh sách sinh viên học tại cơ sở TP.HCM hoặc Đà Nẵng"*
- *"Thống kê số lượng sinh viên theo từng ngành học"*
- *"Thống kê số lượng sinh viên theo từng cơ sở đào tạo"*

### 4. Trạng thái học vụ
- *"Danh sách sinh viên đang bảo lưu trong học kỳ này"*
- *"Những sinh viên nào từng bảo lưu rồi quay lại học?""*
- *"Danh sách sinh viên đã thôi học"*

### 5. Giảng dạy & Điểm số
- *"Giảng viên Nguyễn Văn An đang dạy những lớp và buổi học nào?"*
- *"Ai là sinh viên vừa đi học vừa làm trợ giảng (TA)?"*
- *"Xem điểm số và xếp loại của sinh viên Nguyễn Anh Tuấn"*
- *"Lịch học và các buổi học của lớp PRO192_SE1801"*

---

## 📁 Cấu Trúc Thư Mục Dự Án

```
CrewAI-neo4j/
├── data/                                # Lưu trữ tri thức và dữ liệu khởi tạo
│   ├── seed_sample_data.cypher          # Script Cypher mẫu gốc
│   ├── verified_few_shots.json          # Kho 18+ ví dụ Cypher chuẩn mực
│   └── learned_rules.json               # Sổ tay quy tắc nghiệp vụ tự học
├── docs/                                # Tài liệu kỹ thuật chi tiết
│   ├── PROJECT_SPEC.md                  # Đặc tả dự án và lộ trình nghiệp vụ
│   └── ARCHITECTURE.md                  # Thiết kế kiến trúc đa tác nhân
├── src/                                 # Mã nguồn chính
│   ├── config.py                        # Cấu hình Pydantic Settings
│   ├── agents/                          # Định nghĩa các Agent chuyên biệt
│   │   ├── router_agent.py              # Agent 1: Router & Semantic Extractor
│   │   ├── cypher_agent.py              # Agent 2: Graph Cypher Specialist
│   │   ├── validator_agent.py           # Agent 3: Guardrail & Validator
│   │   └── reporter_agent.py            # Agent 4: Reporter & Synthesizer
│   ├── crew/                            # Điều phối luồng xử lý
│   │   └── edu_crew.py                  # Pipeline chính & đo lường độ trễ
│   ├── db/                              # Tương tác cơ sở dữ liệu Neo4j
│   │   ├── neo4j_client.py              # Neo4j Driver Client (Thread-safe)
│   │   ├── schema_provider.py           # Compact Ontology & Business Rules
│   │   └── entity_resolver.py           # Bộ giải đoán thực thể mờ (Ground Truth Resolver)
│   ├── memory/                          # Cơ chế nhớ và tự học ngữ nghĩa
│   │   ├── few_shot_pool.py             # Dynamic Few-Shot Pool (Jaccard + Keyword)
│   │   ├── rules_store.py               # Dynamic Rules Store
│   │   └── feedback_manager.py          # Quản lý phản hồi người dùng
│   └── web_server.py                    # HTTP Server phục vụ API & Web UI
├── web/                                 # Giao diện Web (NHG Design System)
│   ├── index.html                       # Trang chủ Chatbot
│   ├── style.css                        # CSS Design System & Micro-animations
│   └── app.js                           # Logic Frontend, Live Timer & Model Picker
├── generate_rich_data.py                # Script tạo sinh dữ liệu mẫu đa dạng
├── requirements.txt                     # Danh sách thư viện phụ thuộc
└── README.md                            # Tài liệu tổng quan dự án
```

---

## 📄 Bản Quyền & Giấy Phép

Dự án phát triển theo phương pháp luận **BMAD (v6.12.0)** phục vụ khối Đào tạo và Quản lý Học sinh - Sinh viên.  
Phát hành theo giấy phép [MIT License](LICENSE).
