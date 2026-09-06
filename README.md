# Edu-Graph Multi-Agent Assistant

> Hệ thống Trợ lý AI Đa tác nhân Quản lý Đào tạo & Sinh viên trên Cơ sở Dữ liệu Đồ thị Neo4j.

---

## 📖 Tài liệu Dự án

Chi tiết về thiết kế và kiến trúc đã được chuẩn hóa trong thư mục [`docs/`](docs/):
- **[Đặc tả Dự án (PROJECT_SPEC.md)](docs/PROJECT_SPEC.md)**: Bối cảnh, phân tích mô hình dữ liệu đồ thị, phạm vi nghiệp vụ phòng Đào tạo & QLSV, lộ trình 3 giai đoạn.
- **[Kiến trúc Kỹ thuật (ARCHITECTURE.md)](docs/ARCHITECTURE.md)**: Thiết kế đa tác nhân CrewAI, đường dẫn suy luận 100% động (không dùng Fast-Path), cơ chế tự học qua phản hồi (Semantic Experience Loop), và bản đồ đồ thị tối giản (Compact Ontology).

---

## 🛠️ Công nghệ Chính

- **Graph Database**: Neo4j 5.x (Cypher Query Language)
- **Local LLM**: OLM Lượng tử hóa (Quantized Qwen 2.5 3B/7B Q4_K_M via Ollama) - 100% On-premise, bảo mật nội bộ
- **Multi-Agent Orchestrator**: CrewAI
- **Development Lifecycle**: BMAD Method (v6.12.0)
- **Data Seed**: [`enterprise_dw_neo4j (1).cypher`](enterprise_dw_neo4j%20(1).cypher)

---

## 🚀 Các Tác nhân trong Hệ thống (CrewAI Agents)

1. **🎯 Intent & Semantic Extractor Agent**: Phân tích ngữ nghĩa tự nhiên, bóc tách thực thể và điều kiện lọc.
2. **💻 Graph Cypher Specialist Agent**: Tham khảo Ontology và Few-shot động để sinh Cypher chính xác.
3. **🛡️ Guardrail & Validator Agent**: Thẩm định an toàn (Read-Only), kiểm tra cú pháp và tự sửa lỗi trước khi gửi vào database.
4. **📊 Reporter & Synthesizer Agent**: Định dạng kết quả truy vấn thành bảng biểu và báo cáo trực quan cho cán bộ đào tạo.
