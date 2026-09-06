// ============================================================================
// BỘ DỮ LIỆU MẪU MỞ RỘNG CHO HỆ THỐNG ĐÀO TẠO & QUẢN LÝ SINH VIÊN (NEO4J 5.x)
// Thiết kế phục vụ kiểm thử đầy đủ các tình huống nghiệp vụ:
// - Cảnh báo cấm thi (vắng > 20%)
// - Sinh viên bảo lưu, thôi học, tốt nghiệp, quay lại học
// - Sinh viên kiêm trợ giảng (Dual Role)
// - Tra cứu kết quả học tập, điểm thi, giảng viên đứng lớp
// ============================================================================

// ----------------------------------------------------------------------------
// 1. TỔ CHỨC & KHOA
// ----------------------------------------------------------------------------
MERGE (fpt:Organization {org_code: 'FPT-EDU'})
  SET fpt.org_name = 'Tổ chức Giáo dục FPT', fpt.org_type = 'CORPORATION', fpt.is_active = true;

MERGE (hn:Organization {org_code: 'FPTU-HN'})
  SET hn.org_name = 'Đại học FPT Hà Nội', hn.org_type = 'UNIVERSITY', hn.is_active = true;
MERGE (fpt)-[:PARENT_OF]->(hn);

MERGE (hcm:Organization {org_code: 'FPTU-HCM'})
  SET hcm.org_name = 'Đại học FPT TP. Hồ Chí Minh', hcm.org_type = 'UNIVERSITY', hcm.is_active = true;
MERGE (fpt)-[:PARENT_OF]->(hcm);

MERGE (dept_se:Department {dept_code: 'SE-HN-BM01'})
  SET dept_se.dept_name = 'Bộ môn Kỹ thuật Phần mềm — Hà Nội', dept_se.is_active = true;
MERGE (dept_se)-[:BELONGS_TO]->(hn);

MERGE (dept_ai:Department {dept_code: 'AI-HN-BM01'})
  SET dept_ai.dept_name = 'Bộ môn Trí tuệ Nhân tạo — Hà Nội', dept_ai.is_active = true;
MERGE (dept_ai)-[:BELONGS_TO]->(hn);

// ----------------------------------------------------------------------------
// 2. KỲ HỌC (ACADEMIC PERIODS)
// ----------------------------------------------------------------------------
MERGE (fa24:AcademicPeriod {period_code: 'FA2024'})
  SET fa24.period_name = 'Fall 2024 — Kỳ Thu 2024',
      fa24.academic_year = '2024-2025',
      fa24.semester = 'FALL',
      fa24.start_date = date('2024-09-02'),
      fa24.end_date = date('2024-12-22');

MERGE (sp24:AcademicPeriod {period_code: 'SP2024'})
  SET sp24.period_name = 'Spring 2024 — Kỳ Xuân 2024',
      sp24.academic_year = '2023-2024',
      sp24.semester = 'SPRING',
      sp24.start_date = date('2024-01-08'),
      sp24.end_date = date('2024-05-31');

// ----------------------------------------------------------------------------
// 3. GIẢNG VIÊN & TRỢ GIẢNG (EMPLOYEES)
// ----------------------------------------------------------------------------
// GV 1: Thầy Nguyễn Văn An
MERGE (p1:Person {national_id: '001234567890'})
  SET p1.full_name = 'Nguyễn Văn An', p1.email = 'an.nv@fpt.edu.vn', p1.phone = '0901234001', p1.gender = 'MALE';
MERGE (e1:Employee {employee_code: 'GV-HN-001'})
  SET e1.hire_date = date('2015-08-01'), e1.is_active = true;
MERGE (p1)-[:HAS_ROLE]->(e1);

MATCH (e1:Employee {employee_code: 'GV-HN-001'}), (dept_se:Department {dept_code: 'SE-HN-BM01'})
MERGE (e1)-[:ASSIGNED_TO_DEPT {position_code: 'SENIOR-LEC', employment_status: 'ACTIVE'}]->(dept_se);

// GV 2: Cô Trần Thị Bình
MERGE (p2:Person {national_id: '001234567891'})
  SET p2.full_name = 'Trần Thị Bình', p2.email = 'binh.tt@fpt.edu.vn', p2.phone = '0901234002', p2.gender = 'FEMALE';
MERGE (e2:Employee {employee_code: 'GV-HN-002'})
  SET e2.hire_date = date('2018-03-15'), e2.is_active = true;
MERGE (p2)-[:HAS_ROLE]->(e2);

MATCH (e2:Employee {employee_code: 'GV-HN-002'}), (dept_se:Department {dept_code: 'SE-HN-BM01'})
MERGE (e2)-[:ASSIGNED_TO_DEPT {position_code: 'LECTURER-L2', employment_status: 'ACTIVE'}]->(dept_se);

// GV 3: Thầy Lê Minh Cường (Bộ môn AI)
MERGE (p3:Person {national_id: '001234567892'})
  SET p3.full_name = 'Lê Minh Cường', p3.email = 'cuong.lm@fpt.edu.vn', p3.phone = '0901234003', p3.gender = 'MALE';
MERGE (e3:Employee {employee_code: 'GV-HN-003'})
  SET e3.hire_date = date('2012-10-01'), e3.is_active = true;
MERGE (p3)-[:HAS_ROLE]->(e3);

MATCH (e3:Employee {employee_code: 'GV-HN-003'}), (dept_ai:Department {dept_code: 'AI-HN-BM01'})
MERGE (e3)-[:ASSIGNED_TO_DEPT {position_code: 'HEAD-DEPT', employment_status: 'ACTIVE'}]->(dept_ai);

// DUAL-ROLE: Cao Minh Việt (Sinh viên K17 kiêm Trợ giảng TA)
MERGE (p_ta:Person {national_id: '091234567808'})
  SET p_ta.full_name = 'Cao Minh Việt', p_ta.email = 'viet.cm.k17@fpt.edu.vn', p_ta.phone = '0912340009', p_ta.gender = 'MALE';
MERGE (s_ta:Student {student_code: 'SE170001'})
  SET s_ta.enrollment_date = date('2021-09-06'), s_ta.program_code = 'SE', s_ta.is_active = true;
MERGE (e_ta:Employee {employee_code: 'TA-HN-001'})
  SET e_ta.hire_date = date('2024-01-15'), e_ta.is_active = true;
MERGE (p_ta)-[:HAS_ROLE]->(s_ta);
MERGE (p_ta)-[:HAS_ROLE]->(e_ta);

MATCH (s_ta:Student {student_code: 'SE170001'}), (hn:Organization {org_code: 'FPTU-HN'})
MERGE (s_ta)-[:STUDIES_AT]->(hn);

MATCH (e_ta:Employee {employee_code: 'TA-HN-001'}), (dept_se:Department {dept_code: 'SE-HN-BM01'})
MERGE (e_ta)-[:ASSIGNED_TO_DEPT {position_code: 'TA', employment_status: 'ACTIVE'}]->(dept_se);

// ----------------------------------------------------------------------------
// 4. LỚP HỌC PHẦN (CLASSES)
// ----------------------------------------------------------------------------
// Lớp 1: PRO192_SE1801 (Java OOP)
MATCH (fa24:AcademicPeriod {period_code: 'FA2024'})
MATCH (hn:Organization {org_code: 'FPTU-HN'})
MERGE (c1:Class {class_code: 'PRO192_SE1801'})
  SET c1.class_name = 'Lập trình Hướng đối tượng bằng Java — SE1801',
      c1.class_type = 'LECTURE', c1.max_capacity = 35, c1.is_active = true;
MERGE (c1)-[:OFFERED_IN]->(fa24);
MERGE (c1)-[:HOSTED_BY]->(hn);

// Lớp 2: DBI202_SE1802 (Database)
MATCH (fa24:AcademicPeriod {period_code: 'FA2024'})
MATCH (hn:Organization {org_code: 'FPTU-HN'})
MERGE (c2:Class {class_code: 'DBI202_SE1802'})
  SET c2.class_name = 'Hệ quản trị Cơ sở Dữ liệu — SE1802',
      c2.class_type = 'LECTURE', c2.max_capacity = 35, c2.is_active = true;
MERGE (c2)-[:OFFERED_IN]->(fa24);
MERGE (c2)-[:HOSTED_BY]->(hn);

// Lớp 3: AIL302_AI1901 (Trí tuệ nhân tạo)
MATCH (fa24:AcademicPeriod {period_code: 'FA2024'})
MATCH (hn:Organization {org_code: 'FPTU-HN'})
MERGE (c3:Class {class_code: 'AIL302_AI1901'})
  SET c3.class_name = 'Nhập môn Trí tuệ Nhân tạo — AI1901',
      c3.class_type = 'LECTURE', c3.max_capacity = 30, c3.is_active = true;
MERGE (c3)-[:OFFERED_IN]->(fa24);
MERGE (c3)-[:HOSTED_BY]->(hn);

// ----------------------------------------------------------------------------
// 5. CÁC BUỔI HỌC VÀ THI (ACTIVITIES)
// ----------------------------------------------------------------------------
// Các buổi môn PRO192_SE1801
UNWIND [
  {code: 'PRO192_SE1801_A01', name: 'Buổi 01: Giới thiệu OOP & Cú pháp Java', date: '2024-09-02', type: 'LECTURE', mins: 90, gv: 'GV-HN-001', role: 'PRIMARY_LECTURER'},
  {code: 'PRO192_SE1801_A02', name: 'Buổi 02: Class, Method, Constructor',   date: '2024-09-09', type: 'LECTURE', mins: 90, gv: 'GV-HN-001', role: 'PRIMARY_LECTURER'},
  {code: 'PRO192_SE1801_A03', name: 'Buổi 03: Kế thừa (Inheritance) & Đa hình', date: '2024-09-16', type: 'LECTURE', mins: 90, gv: 'GV-HN-001', role: 'PRIMARY_LECTURER'},
  {code: 'PRO192_SE1801_A04', name: 'Buổi 04: Thực hành Lab Java cơ bản',    date: '2024-09-23', type: 'LAB',     mins: 90, gv: 'TA-HN-001', role: 'TEACHING_ASSISTANT'},
  {code: 'PRO192_SE1801_A05', name: 'Buổi 05: Interface & Abstract Class',   date: '2024-09-30', type: 'LECTURE', mins: 90, gv: 'GV-HN-001', role: 'PRIMARY_LECTURER'},
  {code: 'PRO192_SE1801_A06', name: 'Thi Giữa Kỳ: Lý thuyết & Code OOP',     date: '2024-10-21', type: 'EXAM',    mins: 90, gv: 'GV-HN-001', role: 'PRIMARY_LECTURER'},
  {code: 'PRO192_SE1801_A07', name: 'Buổi 07: Java Collections & Generics',  date: '2024-11-04', type: 'LECTURE', mins: 90, gv: 'GV-HN-001', role: 'PRIMARY_LECTURER'},
  {code: 'PRO192_SE1801_A08', name: 'Thi Cuối Kỳ: Thực hành Phần mềm Java',  date: '2024-12-09', type: 'EXAM',    mins: 120, gv: 'GV-HN-001', role: 'PRIMARY_LECTURER'}
] AS act
MERGE (a:Activity {activity_code: act.code})
  SET a.activity_name = act.name,
      a.scheduled_date = date(act.date),
      a.activity_type = act.type,
      a.duration_minutes = act.mins,
      a.class_code = 'PRO192_SE1801'
WITH a, act
MATCH (c:Class {class_code: 'PRO192_SE1801'})
MERGE (a)-[:PART_OF]->(c)
WITH a, act
MATCH (e:Employee {employee_code: act.gv})
MERGE (e)-[:LEADS {role: act.role}]->(a);

// Các buổi môn DBI202_SE1802
UNWIND [
  {code: 'DBI202_SE1802_A01', name: 'Buổi 01: Cơ sở dữ liệu quan hệ & ERD', date: '2024-09-03', type: 'LECTURE', mins: 90, gv: 'GV-HN-002'},
  {code: 'DBI202_SE1802_A02', name: 'Buổi 02: Ngôn ngữ SQL căn bản',        date: '2024-09-10', type: 'LECTURE', mins: 90, gv: 'GV-HN-002'},
  {code: 'DBI202_SE1802_A03', name: 'Thi Giữa Kỳ: Truy vấn SQL nâng cao',   date: '2024-10-22', type: 'EXAM',    mins: 90, gv: 'GV-HN-002'},
  {code: 'DBI202_SE1802_A04', name: 'Thi Cuối Kỳ: Thiết kế & Tối ưu CSDL',   date: '2024-12-10', type: 'EXAM',    mins: 120, gv: 'GV-HN-002'}
] AS act
MERGE (a:Activity {activity_code: act.code})
  SET a.activity_name = act.name,
      a.scheduled_date = date(act.date),
      a.activity_type = act.type,
      a.duration_minutes = act.mins,
      a.class_code = 'DBI202_SE1802'
WITH a, act
MATCH (c:Class {class_code: 'DBI202_SE1802'})
MERGE (a)-[:PART_OF]->(c)
WITH a, act
MATCH (e:Employee {employee_code: act.gv})
MERGE (e)-[:LEADS {role: 'PRIMARY_LECTURER'}]->(a);

// ----------------------------------------------------------------------------
// 6. DANH SÁCH SINH VIÊN & TRẠNG THÁI HỌC VỤ (STUDENTS)
// ----------------------------------------------------------------------------
UNWIND [
  // Khóa K18 - Ngành SE
  {nid: '091234567800', name: 'Nguyễn Anh Tuấn', code: 'SE180001', prog: 'SE', enr: '2022-09-05', st: 'ACTIVE', note: 'Sinh viên giỏi K18'},
  {nid: '091234567801', name: 'Lê Thị Hương',   code: 'SE180002', prog: 'SE', enr: '2022-09-05', st: 'ACTIVE', note: 'Đi học lại sau bảo lưu'},
  {nid: '091234567802', name: 'Trần Đức Minh',   code: 'SE180003', prog: 'SE', enr: '2022-09-05', st: 'GRADUATED', note: 'Tốt nghiệp sớm loại Giỏi tháng 6/2024'},
  {nid: '091234567803', name: 'Phạm Thị Ngọc',   code: 'SE180004', prog: 'SE', enr: '2022-09-05', st: 'ACTIVE', note: 'Sinh viên chuyên cần'},
  {nid: '091234567804', name: 'Võ Văn Phúc',     code: 'SE180005', prog: 'SE', enr: '2022-09-05', st: 'ACTIVE', note: 'Cảnh báo nguy cơ cấm thi'},

  // Khóa K19 - Ngành SE & AI
  {nid: '091234567805', name: 'Đỗ Thị Quỳnh',    code: 'SE190001', prog: 'SE', enr: '2023-09-04', st: 'ACTIVE', note: 'Lớp trưởng K19'},
  {nid: '091234567806', name: 'Hoàng Quốc Bảo',  code: 'AI190001', prog: 'AI', enr: '2023-09-04', st: 'ACTIVE', note: 'Chuyên ngành AI'},
  {nid: '091234567807', name: 'Lý Hoàng Nam',    code: 'SE190002', prog: 'SE', enr: '2023-09-04', st: 'SUSPENDED', note: 'Đang bảo lưu kỳ FA2024 vì sức khỏe'},
  {nid: '091234567810', name: 'Vũ Hải Đăng',     code: 'AI190002', prog: 'AI', enr: '2023-09-04', st: 'DROPOUT', note: 'Thôi học tự nguyện kỳ Spring 2024'},

  // Khóa K20 - Ngành SE (Tân sinh viên)
  {nid: '091234567811', name: 'Bùi Văn Thắng',   code: 'SE200001', prog: 'SE', enr: '2024-09-02', st: 'ACTIVE', note: 'Vắng học nhiều không phép'},
  {nid: '091234567812', name: 'Ngô Thị Uyên',    code: 'SE200002', prog: 'SE', enr: '2024-09-02', st: 'ACTIVE', note: 'Đi học chuyên cần'}
] AS srow
MERGE (p:Person {national_id: srow.nid})
  SET p.full_name = srow.name, p.gender = 'MALE'
MERGE (s:Student {student_code: srow.code})
  SET s.enrollment_date = date(srow.enr),
      s.program_code = srow.prog,
      s.is_active = (srow.st = 'ACTIVE')
MERGE (p)-[:HAS_ROLE]->(s)
WITH s, srow
MATCH (hn:Organization {org_code: 'FPTU-HN'})
MERGE (s)-[:STUDIES_AT]->(hn)
WITH s, srow
// Ghi nhận trạng thái học vụ
MERGE (s)-[st:HAS_STATUS {status: srow.st, effective_from: date(srow.enr)}]->(s)
  SET st.effective_to = null, st.note = srow.note;

// Ghi nhận trường hợp sinh viên từng bảo lưu rồi quay lại học: Lê Thị Hương (SE180002)
MATCH (s:Student {student_code: 'SE180002'})
MERGE (s)-[:HAS_STATUS {status: 'SUSPENDED', effective_from: date('2023-09-01'), effective_to: date('2024-01-05'), note: 'Bảo lưu kỳ FA2023 vì lý do gia đình'}]->(s);

// ----------------------------------------------------------------------------
// 7. ĐĂNG KÝ MÔN HỌC (ENROLLMENT)
// ----------------------------------------------------------------------------
MATCH (c_pro:Class {class_code: 'PRO192_SE1801'}),
      (c_dbi:Class {class_code: 'DBI202_SE1802'})
MATCH (s:Student)
WHERE s.student_code IN ['SE180001', 'SE180002', 'SE180004', 'SE180005', 'SE200001', 'SE200002']
MERGE (s)-[:ENROLLED_IN {enrolled_at: date('2024-08-25'), status: 'ENROLLED'}]->(c_pro);

MATCH (c_dbi:Class {class_code: 'DBI202_SE1802'})
MATCH (s:Student)
WHERE s.student_code IN ['SE180001', 'SE180002', 'SE190001', 'AI190001']
MERGE (s)-[:ENROLLED_IN {enrolled_at: date('2024-08-25'), status: 'ENROLLED'}]->(c_dbi);

// ----------------------------------------------------------------------------
// 8. ĐIỂM DANH & KẾT QUẢ ĐÁNH GIÁ (PARTICIPATED_IN) — TẠO DỮ LIỆU KIỂM THỬ THỰC TẾ
// ----------------------------------------------------------------------------

// 8.1: Sinh viên Nguyễn Anh Tuấn (SE180001) — Xuất sắc, đi đủ 100%, điểm cao
MATCH (s:Student {student_code: 'SE180001'})
MATCH (a:Activity) WHERE a.class_code = 'PRO192_SE1801'
MERGE (s)-[r:PARTICIPATED_IN]->(a)
  SET r.participation_date = a.scheduled_date,
      r.attendance_status = 'PRESENT',
      r.quiz_score = 9.0,
      r.assignment_score = 8.5,
      r.grade = 'A';

// 8.2: Sinh viên Lê Thị Hương (SE180002) — Chuyên cần, có 1 buổi đến muộn
MATCH (s:Student {student_code: 'SE180002'})
MATCH (a:Activity) WHERE a.class_code = 'PRO192_SE1801'
MERGE (s)-[r:PARTICIPATED_IN]->(a)
  SET r.participation_date = a.scheduled_date,
      r.attendance_status = CASE WHEN a.activity_code = 'PRO192_SE1801_A02' THEN 'LATE' ELSE 'PRESENT' END,
      r.quiz_score = 7.5,
      r.grade = 'B+';

// 8.3: Sinh viên Võ Văn Phúc (SE180005) — NGUY CƠ CẤM THI: Vắng 3/8 buổi (37.5% > 20%)!
MATCH (s:Student {student_code: 'SE180005'})
MATCH (a:Activity) WHERE a.class_code = 'PRO192_SE1801'
MERGE (s)-[r:PARTICIPATED_IN]->(a)
  SET r.participation_date = a.scheduled_date,
      r.attendance_status = CASE 
        WHEN a.activity_code IN ['PRO192_SE1801_A01', 'PRO192_SE1801_A03', 'PRO192_SE1801_A05'] THEN 'ABSENT'
        ELSE 'PRESENT' 
      END,
      r.note = CASE WHEN a.activity_code = 'PRO192_SE1801_A01' THEN 'Vắng không phép' ELSE null END,
      r.quiz_score = CASE WHEN a.activity_code = 'PRO192_SE1801_A06' THEN 4.0 ELSE 6.0 END,
      r.grade = 'D';

// 8.4: Sinh viên Bùi Văn Thắng (SE200001) — CẤM THI: Vắng 4/8 buổi (50%)!
MATCH (s:Student {student_code: 'SE200001'})
MATCH (a:Activity) WHERE a.class_code = 'PRO192_SE1801'
MERGE (s)-[r:PARTICIPATED_IN]->(a)
  SET r.participation_date = a.scheduled_date,
      r.attendance_status = CASE 
        WHEN a.activity_code IN ['PRO192_SE1801_A01', 'PRO192_SE1801_A02', 'PRO192_SE1801_A04', 'PRO192_SE1801_A07'] THEN 'ABSENT'
        ELSE 'PRESENT' 
      END,
      r.note = 'Thường xuyên nghỉ học',
      r.quiz_score = 3.5,
      r.grade = 'F';

// 8.5: Sinh viên Ngô Thị Uyên (SE200002) — Đi đủ, điểm khá
MATCH (s:Student {student_code: 'SE200002'})
MATCH (a:Activity) WHERE a.class_code = 'PRO192_SE1801'
MERGE (s)-[r:PARTICIPATED_IN]->(a)
  SET r.participation_date = a.scheduled_date,
      r.attendance_status = 'PRESENT',
      r.quiz_score = 8.0,
      r.grade = 'A-';
