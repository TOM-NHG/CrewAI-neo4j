"""
Mô-đun cung cấp Bản đồ Đồ thị Tối giản (Compact Graph Ontology)
và Từ điển Quy ước Nghiệp vụ cho OLM sinh Cypher.
"""

COMPACT_GRAPH_ONTOLOGY = """
[BẢN ĐỒ ĐỒ THỊ TỐI GIẢN (BẮT BUỘC TUÂN THỦ CHIỀU MŨI TÊN)]:
1. Con người & Vai trò:
   (:Person {national_id, full_name, date_of_birth, gender, email, phone}) -[:HAS_ROLE]-> (:Student {student_code, enrollment_date, program_code, is_active})
   (:Person {national_id, full_name, date_of_birth, gender, email, phone}) -[:HAS_ROLE]-> (:Employee {employee_code, hire_date, is_active})

2. Cơ cấu Đơn vị & Giảng dạy:
   (:Employee) -[:ASSIGNED_TO_DEPT {position_code, assignment_type, employment_status, effective_from, effective_to}]-> (:Department {dept_code, dept_name})
   (:Employee) -[:LEADS {role: 'PRIMARY_LECTURER' | 'TEACHING_ASSISTANT'}]-> (:Activity)
   (:Department) -[:BELONGS_TO]-> (:Organization {org_code, org_name, org_type})

3. Lớp học & Buổi học:
   (:Class {class_code, class_name, class_type, max_capacity, is_active}) -[:OFFERED_IN]-> (:AcademicPeriod {period_code, period_name, academic_year, semester, start_date, end_date})
   (:Class) -[:HOSTED_BY]-> (:Organization)
   (:Activity {class_code, scheduled_date, activity_name, activity_type: 'LECTURE' | 'LAB' | 'EXAM', duration_minutes}) -[:PART_OF]-> (:Class)

4. Sinh viên & Tham gia học tập:
   (:Student) -[:STUDIES_AT]-> (:Organization)
   (:Student) -[:ENROLLED_IN {enrolled_at, status: 'ENROLLED'}]-> (:Class)
   (:Student) -[:PARTICIPATED_IN {participation_date, attendance_status: 'PRESENT' | 'ABSENT' | 'LATE', quiz_score, assignment_score, grade, note}]-> (:Activity)

5. Lịch sử trạng thái học vụ (Quan hệ vòng lặp trên Student):
   (:Student) -[:HAS_STATUS {status: 'ACTIVE' | 'SUSPENDED' | 'GRADUATED' | 'DROPOUT', effective_from, effective_to, note}]-> (:Student)
"""

BUSINESS_SEMANTIC_RULES = """
[TỪ ĐIỂN QUY ƯỚC NGHIỆP VỤ PHÒNG ĐÀO TẠO]:
1. "Sinh viên đang học":
   (s:Student {is_active: true}) VÀ (s)-[st:HAS_STATUS]->(s) WHERE st.status = 'ACTIVE' AND st.effective_to IS NULL

2. "Sinh viên đang bảo lưu":
   (s:Student)-[st:HAS_STATUS]->(s) WHERE st.status = 'SUSPENDED' AND st.effective_to IS NULL

3. "Sinh viên từng bảo lưu rồi quay lại học":
   (s:Student)-[st:HAS_STATUS]->(s) WHERE st.status = 'SUSPENDED' AND st.effective_to IS NOT NULL

4. "Sinh viên đã thôi học":
   (s:Student)-[st:HAS_STATUS]->(s) WHERE st.status = 'DROPOUT'

5. "Sinh viên đã tốt nghiệp":
   (s:Student)-[st:HAS_STATUS]->(s) WHERE st.status = 'GRADUATED'

6. "Vắng mặt / Nghỉ học":
   part.attendance_status = 'ABSENT'

7. "Đi muộn":
   part.attendance_status = 'LATE'

8. "Có mặt (hợp lệ)":
   part.attendance_status IN ['PRESENT', 'LATE']

9. "Giảng viên dạy sinh viên":
   KHÔNG NỐI TRỰC TIẾP (Employee)-[:TEACHES]->(Student)!
   Bắt buộc qua Activity: (emp:Person)-[:HAS_ROLE]->(e:Employee)-[:LEADS]->(a:Activity)<-[:PARTICIPATED_IN]-(s:Student)<-[:HAS_ROLE]-(stu:Person)

10. "Tìm kiếm tên không phân biệt hoa thường":
    Sử dụng toLower(p.full_name) CONTAINS toLower('...') hoặc p.full_name =~ '(?i).*...*'

11. "Ngành học của sinh viên (SE, AI, IA, BA, CS, ...)":
    Được lưu TRỰC TIẾP tại thuộc tính s.program_code trên nhãn Student (ví dụ: s.program_code = 'SE').
    TUYỆT ĐỐI KHÔNG tìm ngành qua (:Organization) hay (:Major).
    Tổ chức (:Organization) chỉ đại diện cho Trường/Phân hiệu/Khoa (org_type: 'UNIVERSITY', 'FACULTY', 'CORPORATION').
    Mẫu truy vấn chuẩn:
    MATCH (p:Person)-[:HAS_ROLE]->(s:Student)
    WHERE s.program_code = 'SE'
    RETURN s.student_code AS ma_sinh_vien, p.full_name AS ho_va_ten, s.program_code AS ma_nganh, s.enrollment_date AS ngay_nhap_hoc
    LIMIT 50

12. "Thuộc tính Họ tên và Thông tin cá nhân":
    Nút (:Student) KHÔNG CÓ full_name, email, phone.
    Tất cả họ tên, email, phone nằm trên nút (:Person) nối qua (p:Person)-[:HAS_ROLE]->(s:Student).
    BẮT BUỘC MATCH (p:Person)-[:HAS_ROLE]->(s:Student) để lấy họ tên p.full_name.

13. "Cơ sở đào tạo / Khuôn viên (Hà Nội, TP.HCM, Đà Nẵng, Cần Thơ, Quy Nhơn)":
    Sinh viên học tại cơ sở nào nối qua: (s:Student)-[:STUDIES_AT]->(o:Organization)
    Để lọc theo cơ sở, luôn dùng toLower(o.org_name) CONTAINS '...' hoặc mã o.org_code:
    - Hà Nội: (toLower(o.org_name) CONTAINS 'hà nội' OR o.org_code = 'FPTU-HN')
    - TP. Hồ Chí Minh: (toLower(o.org_name) CONTAINS 'hồ chí minh' OR toLower(o.org_name) CONTAINS 'hcm' OR o.org_code = 'FPTU-HCM')
    - Đà Nẵng: (toLower(o.org_name) CONTAINS 'đà nẵng' OR o.org_code = 'FPTU-DN')
    Mẫu chuẩn:
    MATCH (p:Person)-[:HAS_ROLE]->(s:Student)-[:STUDIES_AT]->(o:Organization)
    WHERE s.program_code = 'SE' AND (toLower(o.org_name) CONTAINS 'hà nội' OR o.org_code = 'FPTU-HN')
    RETURN s.student_code AS ma_sinh_vien, p.full_name AS ho_va_ten, s.program_code AS ma_nganh, o.org_name AS co_so
    LIMIT 50

14. "Xử lý kiểu Ngày tháng (Date) & Cấm tự bịa mốc thời gian":
    - Các trường ngày: s.enrollment_date, a.scheduled_date là kiểu Neo4j Date.
    - Khi so sánh ngày, BẮT BUỘC dùng hàm date('YYYY-MM-DD') (ví dụ: a.scheduled_date = date('2024-09-02')). TUYỆT ĐỐI KHÔNG so sánh trực tiếp Date với chuỗi String.
    - TUYỆT ĐỐI KHÔNG tự thêm điều kiện ngày tháng (như s.enrollment_date >= ...) nếu người dùng không yêu cầu thời gian cụ thể!
"""


class SchemaProvider:
    @staticmethod
    def get_compact_ontology() -> str:
        return COMPACT_GRAPH_ONTOLOGY.strip()

    @staticmethod
    def get_business_rules() -> str:
        return BUSINESS_SEMANTIC_RULES.strip()

    @classmethod
    def get_full_schema_context(cls) -> str:
        return f"{cls.get_compact_ontology()}\n\n{cls.get_business_rules()}"
