# 📊 Báo Cáo Kiểm Thử E2E Tự Động (Edu-Graph Multi-Agent Assistant)

> **Thời gian thực hiện:** 2026-09-06 14:05:58  
> **Mô hình OLM:** `qwen2.5:3b` | **Cơ sở dữ liệu:** Neo4j 5.26 (Docker)

## 1. Tổng Quan Kết Quả Kiểm Thử

| Chỉ số đánh giá | Giá trị thực tế | Mục tiêu chuẩn | Đánh giá |
| :--- | :---: | :---: | :---: |
| **Tổng số kịch bản kiểm thử** | **15** | 15 | 100% Phủ kín |
| **Số ca thành công (PASS)** | **11** | >= 12 | ⚠️ Cần tối ưu |
| **Số ca thất bại (FAIL)** | **4** | <= 3 | ❌ Cao |
| **Tỷ lệ chính xác (Pass Rate)** | **73.33%** | **>= 80.0%** | **⚠️ CHƯA ĐẠT** |

---

## 2. Bảng Chi Tiết Kết Quả Từng Test Case

| Mã TC | Chuyên đề nghiệp vụ | Câu hỏi đầu vào (Input) | Nhận diện thực thể / Ý định | Bản ghi DB | Thời gian | Trạng thái |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| `TC01` | Điểm danh & Vắng học | *"Tìm những sinh viên vắng mặt ở lớp PRO192_SE1801 ngày 2024-09-02"* | `attendance_query` (PRO192_SE1801) | 3 bản ghi | 14.61s | **✅ PASS** |
| `TC02` | Cảnh báo cấm thi | *"Cảnh báo những sinh viên có nguy cơ cấm thi vì vắng quá 20% môn Java"* | `warning_query` (Java / PRO192) | 0 bản ghi | 7.47s | **❌ FAIL** |
| `TC03` | Điểm danh & Đi muộn | *"Danh sách sinh viên đi muộn trong các buổi học"* | `attendance_query` (LATE) | 0 bản ghi | 10.94s | **❌ FAIL** |
| `TC04` | Hồ sơ & Khử lỗi dấu | *"hồ sơ sinh viên lê khắc tiệp"* | `general_query` (Lê Khắc Tiệp) | 1 bản ghi | 3.82s | **✅ PASS** |
| `TC05` | Hồ sơ & Gõ sai dấu (Fuzzy) | *"thông tin sinh viên lé khắc tiệp"* | `general_query` (Lê Khắc Tiệp) | 1 bản ghi | 3.64s | **✅ PASS** |
| `TC06` | Hồ sơ & Không dấu | *"ho so sinh vien le khac tiep"* | `general_query` (Lê Khắc Tiệp) | 1 bản ghi | 4.69s | **✅ PASS** |
| `TC07` | Hồ sơ & Đảo trật tự tên | *"Hồ sơ sinh viên Duyên Đặng"* | `general_query` (Đặng Thị Mỹ Duyên) | 1 bản ghi | 4.79s | **✅ PASS** |
| `TC08` | Hồ sơ theo Mã SV | *"Tra cứu thông tin sinh viên mã SE180001"* | `status_query` (SE180001) | 1 bản ghi | 5.23s | **✅ PASS** |
| `TC09` | Trạng thái học vụ | *"Danh sách sinh viên đang bảo lưu trong học kỳ này"* | `status_query` (SUSPENDED) | 0 bản ghi | 3.73s | **❌ FAIL** |
| `TC10` | Trạng thái học vụ | *"Danh sách sinh viên đã thôi học"* | `status_query` (DROPOUT) | 4 bản ghi | 3.5s | **✅ PASS** |
| `TC11` | Giảng viên & Phân công | *"Giảng viên Nguyễn Văn An đang dạy những lớp và buổi học nào?"* | `lecturer_query` (Nguyễn Văn An) | 0 bản ghi | 4.1s | **❌ FAIL** |
| `TC12` | Trợ giảng kép (Dual-role) | *"Ai là sinh viên vừa đi học vừa làm trợ giảng (TA)?"* | `general_query` (TA / Dual Role) | 28 bản ghi | 9.96s | **✅ PASS** |
| `TC13` | Ngành học & Chương trình | *"những sinh viên ngành SE"* | `knowledge_query` (SE) | 42 bản ghi | 3.76s | **✅ PASS** |
| `TC14` | Cơ sở đào tạo | *"sinh viên ngành SE cơ sở hà nội"* | `knowledge_query` (SE & Hà Nội) | 38 bản ghi | 4.94s | **✅ PASS** |
| `TC15` | Thống kê tổng hợp | *"Thống kê số lượng sinh viên theo từng ngành học"* | `general_query` (Major / Program) | 3 bản ghi | 3.07s | **✅ PASS** |

---

## 3. Tệp Tin Báo Cáo Chi Tiết Đính Kèm
- File Excel chi tiết: [E2E_Test_Report.xlsx](file:///Users/apple/Main/project/NHG/CrewAI-neo4j/tests/E2E_Test_Report.xlsx)
- Bao gồm phân rã độ trễ, câu lệnh Cypher tương ứng và thống kê theo từng danh mục nghiệp vụ.
