// ============================================================================
// ENTERPRISE DATA WAREHOUSE — NEO4J CYPHER IMPLEMENTATION
// Kiến trúc gốc: db/enterprise_dw.sql (PostgreSQL Dimensional Model)
// Chuyển đổi sang: Neo4j Property Graph Model
// Phiên bản: 1.0 (Neo4j 5.x)
//
// MAPPING TRIẾT LÝ:
//   Table (Dim/Fact)  → Node Label
//   Foreign Key        → Relationship
//   Attribute          → Node/Relationship Property
//   Bridge Table       → Relationship với properties
//   Factless Fact      → Relationship (event edge)
//   State-Duration Fact→ Relationship với effective_from/effective_to
// ============================================================================


// ============================================================================
// PHẦN 1: SCHEMA CONSTRAINTS & INDEXES
// (Chạy trước khi import data — mỗi lệnh 1 transaction)
// ============================================================================

// --- Node: Organization ---
CREATE CONSTRAINT uq_org_code IF NOT EXISTS
    FOR (o:Organization) REQUIRE o.org_code IS UNIQUE;

CREATE INDEX idx_org_name IF NOT EXISTS
    FOR (o:Organization) ON (o.org_name);

// --- Node: Person ---
CREATE CONSTRAINT uq_person_national_id IF NOT EXISTS
    FOR (p:Person) REQUIRE p.national_id IS UNIQUE;

CREATE CONSTRAINT uq_person_email IF NOT EXISTS
    FOR (p:Person) REQUIRE p.email IS UNIQUE;

// --- Node: Student (Registration Fact — sub-role của Person) ---
CREATE CONSTRAINT uq_student_code IF NOT EXISTS
    FOR (s:Student) REQUIRE s.student_code IS UNIQUE;

// --- Node: Employee ---
CREATE CONSTRAINT uq_employee_code IF NOT EXISTS
    FOR (e:Employee) REQUIRE e.employee_code IS UNIQUE;

// --- Node: Department ---
CREATE CONSTRAINT uq_dept_code IF NOT EXISTS
    FOR (d:Department) REQUIRE d.dept_code IS UNIQUE;

// --- Node: Position ---
CREATE CONSTRAINT uq_position_code IF NOT EXISTS
    FOR (pos:Position) REQUIRE pos.position_code IS UNIQUE;

// --- Node: AcademicPeriod ---
CREATE CONSTRAINT uq_period_code IF NOT EXISTS
    FOR (ap:AcademicPeriod) REQUIRE ap.period_code IS UNIQUE;

// --- Node: Class ---
CREATE CONSTRAINT uq_class_code IF NOT EXISTS
    FOR (c:Class) REQUIRE c.class_code IS UNIQUE;

// --- Node: Activity ---
CREATE INDEX idx_activity_date IF NOT EXISTS
    FOR (a:Activity) ON (a.scheduled_date);

CREATE INDEX idx_activity_type IF NOT EXISTS
    FOR (a:Activity) ON (a.activity_type);

// --- Node: CalendarDate ---
CREATE CONSTRAINT uq_calendar_date IF NOT EXISTS
    FOR (cal:CalendarDate) REQUIRE cal.date_id IS UNIQUE;

// --- Relationship indexes ---
CREATE INDEX idx_rel_status IF NOT EXISTS
    FOR ()-[r:HAS_STATUS]-() ON (r.effective_to);

CREATE INDEX idx_rel_assign_current IF NOT EXISTS
    FOR ()-[r:ASSIGNED_TO_DEPT]-() ON (r.effective_to);


// ============================================================================
// PHẦN 2: SEED DATA — shared layer
// ============================================================================

// --- 2.1: Organization nodes ---
MERGE (o0:Organization {org_code: 'FPT-EDU'})
    SET o0.org_name = 'Tổ chức Giáo dục FPT',
        o0.org_type = 'CORPORATION',
        o0.is_active = true;

MERGE (o1:Organization {org_code: 'FPTU-HN'})
    SET o1.org_name = 'Đại học FPT Hà Nội',
        o1.org_type = 'UNIVERSITY',
        o1.is_active = true;

MERGE (o2:Organization {org_code: 'FPTU-HCM'})
    SET o2.org_name = 'Đại học FPT TP. Hồ Chí Minh',
        o2.org_type = 'UNIVERSITY',
        o2.is_active = true;

MERGE (o3:Organization {org_code: 'FPTU-DN'})
    SET o3.org_name = 'Đại học FPT Đà Nẵng',
        o3.org_type = 'UNIVERSITY',
        o3.is_active = true;

MERGE (o4:Organization {org_code: 'FAC-SE-HN'})
    SET o4.org_name = 'Khoa Kỹ thuật Phần mềm — Hà Nội',
        o4.org_type = 'FACULTY',
        o4.is_active = true;

MERGE (o5:Organization {org_code: 'FAC-SE-HCM'})
    SET o5.org_name = 'Khoa Kỹ thuật Phần mềm — TP.HCM',
        o5.org_type = 'FACULTY',
        o5.is_active = true;

MERGE (o6:Organization {org_code: 'FAC-AI-HCM'})
    SET o6.org_name = 'Khoa Trí tuệ Nhân tạo — TP.HCM',
        o6.org_type = 'FACULTY',
        o6.is_active = true;

// Organization hierarchy relationships
MATCH (parent:Organization {org_code: 'FPT-EDU'}),
      (child:Organization)
WHERE child.org_code IN ['FPTU-HN','FPTU-HCM','FPTU-DN']
MERGE (parent)-[:PARENT_OF]->(child);

MATCH (hn:Organization {org_code: 'FPTU-HN'}),
      (fac:Organization {org_code: 'FAC-SE-HN'})
MERGE (hn)-[:PARENT_OF]->(fac);

MATCH (hcm:Organization {org_code: 'FPTU-HCM'}),
      (fac:Organization)
WHERE fac.org_code IN ['FAC-SE-HCM','FAC-AI-HCM']
MERGE (hcm)-[:PARENT_OF]->(fac);


// --- 2.2: Person nodes (Party Model — Single Source of Truth) ---
MERGE (p:Person {national_id: '001234567890'})
    SET p.full_name = 'Nguyễn Văn An', p.date_of_birth = date('1980-05-15'),
        p.gender = 'MALE', p.email = 'an.nv@fpt.edu.vn', p.phone = '0901234001';

MERGE (p:Person {national_id: '001234567891'})
    SET p.full_name = 'Trần Thị Bình', p.date_of_birth = date('1985-08-22'),
        p.gender = 'FEMALE', p.email = 'binh.tt@fpt.edu.vn', p.phone = '0901234002';

MERGE (p:Person {national_id: '001234567892'})
    SET p.full_name = 'Lê Minh Cường', p.date_of_birth = date('1978-03-10'),
        p.gender = 'MALE', p.email = 'cuong.lm@fpt.edu.vn', p.phone = '0901234003';

MERGE (p:Person {national_id: '001234567893'})
    SET p.full_name = 'Phạm Thị Dung', p.date_of_birth = date('1990-11-30'),
        p.gender = 'FEMALE', p.email = 'dung.pt@fpt.edu.vn', p.phone = '0901234004';

MERGE (p:Person {national_id: '001234567894'})
    SET p.full_name = 'Hoàng Văn Em', p.date_of_birth = date('1982-07-04'),
        p.gender = 'MALE', p.email = 'em.hv@fpt.edu.vn', p.phone = '0901234005';

// Sinh viên
MERGE (p:Person {national_id: '091234567800'})
    SET p.full_name = 'Nguyễn Anh Tuấn', p.date_of_birth = date('2004-01-20'),
        p.gender = 'MALE', p.email = 'tuan.na.k18@fpt.edu.vn', p.phone = '0912340001';

MERGE (p:Person {national_id: '091234567801'})
    SET p.full_name = 'Lê Thị Hương', p.date_of_birth = date('2004-03-14'),
        p.gender = 'FEMALE', p.email = 'huong.lt.k18@fpt.edu.vn', p.phone = '0912340002';

MERGE (p:Person {national_id: '091234567802'})
    SET p.full_name = 'Trần Đức Minh', p.date_of_birth = date('2004-06-05'),
        p.gender = 'MALE', p.email = 'minh.td.k18@fpt.edu.vn', p.phone = '0912340003';

MERGE (p:Person {national_id: '091234567803'})
    SET p.full_name = 'Phạm Thị Ngọc', p.date_of_birth = date('2005-09-17'),
        p.gender = 'FEMALE', p.email = 'ngoc.pt.k19@fpt.edu.vn', p.phone = '0912340004';

MERGE (p:Person {national_id: '091234567804'})
    SET p.full_name = 'Võ Văn Phúc', p.date_of_birth = date('2005-12-01'),
        p.gender = 'MALE', p.email = 'phuc.vv.k19@fpt.edu.vn', p.phone = '0912340005';

MERGE (p:Person {national_id: '091234567805'})
    SET p.full_name = 'Đỗ Thị Quỳnh', p.date_of_birth = date('2005-02-28'),
        p.gender = 'FEMALE', p.email = 'quynh.dt.k19@fpt.edu.vn', p.phone = '0912340006';

MERGE (p:Person {national_id: '091234567806'})
    SET p.full_name = 'Bùi Văn Thắng', p.date_of_birth = date('2006-04-10'),
        p.gender = 'MALE', p.email = 'thang.bv.k20@fpt.edu.vn', p.phone = '0912340007';

MERGE (p:Person {national_id: '091234567807'})
    SET p.full_name = 'Ngô Thị Uyên', p.date_of_birth = date('2006-07-23'),
        p.gender = 'FEMALE', p.email = 'uyen.nt.k20@fpt.edu.vn', p.phone = '0912340008';

// DUAL_ROLE nodes
MERGE (p:Person {national_id: '091234567808'})
    SET p.full_name = 'Cao Minh Việt', p.date_of_birth = date('2003-11-11'),
        p.gender = 'MALE', p.email = 'viet.cm.k17@fpt.edu.vn', p.phone = '0912340009';

MERGE (p:Person {national_id: '091234567809'})
    SET p.full_name = 'Đinh Thị Xuân', p.date_of_birth = date('2003-08-30'),
        p.gender = 'FEMALE', p.email = 'xuan.dt.k17@fpt.edu.vn', p.phone = '0912340010';


// --- 2.3: CalendarDate nodes ---
UNWIND [
    {date_id: 20240902, full_date: '2024-09-02', year: 2024, quarter: 3, month: 9, week_of_year: 36, day_of_week: 1, is_weekend: false, is_holiday: false},
    {date_id: 20240903, full_date: '2024-09-03', year: 2024, quarter: 3, month: 9, week_of_year: 36, day_of_week: 2, is_weekend: false, is_holiday: false},
    {date_id: 20240904, full_date: '2024-09-04', year: 2024, quarter: 3, month: 9, week_of_year: 36, day_of_week: 3, is_weekend: false, is_holiday: false},
    {date_id: 20240909, full_date: '2024-09-09', year: 2024, quarter: 3, month: 9, week_of_year: 37, day_of_week: 1, is_weekend: false, is_holiday: false},
    {date_id: 20240910, full_date: '2024-09-10', year: 2024, quarter: 3, month: 9, week_of_year: 37, day_of_week: 2, is_weekend: false, is_holiday: false},
    {date_id: 20240916, full_date: '2024-09-16', year: 2024, quarter: 3, month: 9, week_of_year: 38, day_of_week: 1, is_weekend: false, is_holiday: false},
    {date_id: 20241021, full_date: '2024-10-21', year: 2024, quarter: 4, month: 10, week_of_year: 43, day_of_week: 1, is_weekend: false, is_holiday: false},
    {date_id: 20241028, full_date: '2024-10-28', year: 2024, quarter: 4, month: 10, week_of_year: 44, day_of_week: 1, is_weekend: false, is_holiday: false},
    {date_id: 20241104, full_date: '2024-11-04', year: 2024, quarter: 4, month: 11, week_of_year: 45, day_of_week: 1, is_weekend: false, is_holiday: false},
    {date_id: 20241209, full_date: '2024-12-09', year: 2024, quarter: 4, month: 12, week_of_year: 50, day_of_week: 1, is_weekend: false, is_holiday: false},
    {date_id: 20241216, full_date: '2024-12-16', year: 2024, quarter: 4, month: 12, week_of_year: 51, day_of_week: 1, is_weekend: false, is_holiday: false}
] AS row
MERGE (cal:CalendarDate {date_id: row.date_id})
    SET cal.full_date    = date(row.full_date),
        cal.year         = row.year,
        cal.quarter      = row.quarter,
        cal.month        = row.month,
        cal.week_of_year = row.week_of_year,
        cal.day_of_week  = row.day_of_week,
        cal.is_weekend   = row.is_weekend,
        cal.is_holiday   = row.is_holiday;


// ============================================================================
// PHẦN 3: HR DOMAIN
// ============================================================================

// --- 3.1: Department nodes ---
MERGE (d:Department {dept_code: 'SE-HN-BM01'})
    SET d.dept_name = 'Bộ môn Lập trình — Hà Nội', d.is_active = true;

MERGE (d:Department {dept_code: 'SE-HN-BM02'})
    SET d.dept_name = 'Bộ môn Cơ sở Dữ liệu — Hà Nội', d.is_active = true;

MERGE (d:Department {dept_code: 'SE-HCM-BM01'})
    SET d.dept_name = 'Bộ môn Lập trình — TP.HCM', d.is_active = true;

MERGE (d:Department {dept_code: 'AI-HCM-BM01'})
    SET d.dept_name = 'Bộ môn Học máy & AI — TP.HCM', d.is_active = true;

// Department → Organization
MATCH (d:Department {dept_code: 'SE-HN-BM01'}),  (o:Organization {org_code: 'FPTU-HN'})  MERGE (d)-[:BELONGS_TO]->(o);
MATCH (d:Department {dept_code: 'SE-HN-BM02'}),  (o:Organization {org_code: 'FPTU-HN'})  MERGE (d)-[:BELONGS_TO]->(o);
MATCH (d:Department {dept_code: 'SE-HCM-BM01'}), (o:Organization {org_code: 'FPTU-HCM'}) MERGE (d)-[:BELONGS_TO]->(o);
MATCH (d:Department {dept_code: 'AI-HCM-BM01'}), (o:Organization {org_code: 'FPTU-HCM'}) MERGE (d)-[:BELONGS_TO]->(o);


// --- 3.2: Position nodes ---
UNWIND [
    {code: 'LECTURER-L1',  name: 'Giảng viên',                    family: 'ACADEMIC',       band: 'L1'},
    {code: 'LECTURER-L2',  name: 'Giảng viên Chính',               family: 'ACADEMIC',       band: 'L2'},
    {code: 'SENIOR-LEC',   name: 'Giảng viên Cao cấp',             family: 'ACADEMIC',       band: 'Senior'},
    {code: 'HEAD-DEPT',    name: 'Trưởng bộ môn',                  family: 'MANAGEMENT',     band: 'Manager'},
    {code: 'TA',           name: 'Trợ giảng (Teaching Assistant)',  family: 'ACADEMIC',       band: 'L0'},
    {code: 'ACAD-STAFF',   name: 'Chuyên viên Học vụ',              family: 'ADMINISTRATIVE', band: 'L1'}
] AS row
MERGE (pos:Position {position_code: row.code})
    SET pos.position_name = row.name,
        pos.job_family    = row.family,
        pos.level_band    = row.band;


// --- 3.3: Employee nodes (IDENTIFIES Person) ---
MATCH (p:Person {national_id: '001234567890'})
MERGE (e:Employee {employee_code: 'GV-HN-001'})
    SET e.hire_date = date('2010-08-01'), e.is_active = true
MERGE (p)-[:HAS_ROLE]->(e);

MATCH (p:Person {national_id: '001234567891'})
MERGE (e:Employee {employee_code: 'GV-HN-002'})
    SET e.hire_date = date('2015-03-15'), e.is_active = true
MERGE (p)-[:HAS_ROLE]->(e);

MATCH (p:Person {national_id: '001234567892'})
MERGE (e:Employee {employee_code: 'GV-HCM-001'})
    SET e.hire_date = date('2008-09-01'), e.is_active = true
MERGE (p)-[:HAS_ROLE]->(e);

MATCH (p:Person {national_id: '001234567893'})
MERGE (e:Employee {employee_code: 'GV-HCM-002'})
    SET e.hire_date = date('2018-01-10'), e.is_active = true
MERGE (p)-[:HAS_ROLE]->(e);

MATCH (p:Person {national_id: '001234567894'})
MERGE (e:Employee {employee_code: 'GV-DN-001'})
    SET e.hire_date = date('2012-07-01'), e.is_active = true
MERGE (p)-[:HAS_ROLE]->(e);

// DUAL_ROLE: TA là sinh viên kiêm nhân viên
MATCH (p:Person {national_id: '091234567808'})
MERGE (e:Employee {employee_code: 'TA-HN-001'})
    SET e.hire_date = date('2024-01-15'), e.is_active = true
MERGE (p)-[:HAS_ROLE]->(e);

MATCH (p:Person {national_id: '091234567809'})
MERGE (e:Employee {employee_code: 'TA-HN-002'})
    SET e.hire_date = date('2024-01-15'), e.is_active = true
MERGE (p)-[:HAS_ROLE]->(e);


// --- 3.4: Employment Assignment (State-Duration as relationship properties) ---
MATCH (e:Employee {employee_code: 'GV-HN-001'}),
      (d:Department {dept_code: 'SE-HN-BM01'}),
      (pos:Position {position_code: 'LECTURER-L2'})
MERGE (e)-[r:ASSIGNED_TO_DEPT {effective_from: date('2010-08-01')}]->(d)
    SET r.position_code   = 'LECTURER-L2',
        r.assignment_type = 'PRIMARY',
        r.employment_status = 'ACTIVE',
        r.effective_to    = null;

MATCH (e:Employee {employee_code: 'GV-HN-002'}),
      (d:Department {dept_code: 'SE-HN-BM02'}),
      (pos:Position {position_code: 'LECTURER-L1'})
MERGE (e)-[r:ASSIGNED_TO_DEPT {effective_from: date('2015-03-15')}]->(d)
    SET r.position_code   = 'LECTURER-L1',
        r.assignment_type = 'PRIMARY',
        r.employment_status = 'ACTIVE',
        r.effective_to    = null;

MATCH (e:Employee {employee_code: 'GV-HCM-001'}),
      (d:Department {dept_code: 'AI-HCM-BM01'})
MERGE (e)-[r:ASSIGNED_TO_DEPT {effective_from: date('2021-01-01')}]->(d)
    SET r.position_code   = 'HEAD-DEPT',
        r.assignment_type = 'PRIMARY',
        r.employment_status = 'ACTIVE',
        r.effective_to    = null;

MATCH (e:Employee {employee_code: 'TA-HN-001'}),
      (d:Department {dept_code: 'SE-HN-BM01'})
MERGE (e)-[r:ASSIGNED_TO_DEPT {effective_from: date('2024-01-15')}]->(d)
    SET r.position_code   = 'TA',
        r.assignment_type = 'PRIMARY',
        r.employment_status = 'ACTIVE',
        r.effective_to    = null;


// ============================================================================
// PHẦN 4: EDU DOMAIN
// ============================================================================

// --- 4.1: AcademicPeriod nodes ---
MERGE (ap:AcademicPeriod {period_code: 'FA2024'})
    SET ap.period_name    = 'Fall 2024 — Kỳ Thu 2024',
        ap.academic_year  = '2024-2025',
        ap.semester       = 'FALL',
        ap.start_date     = date('2024-09-02'),
        ap.end_date       = date('2024-12-20');

MERGE (ap:AcademicPeriod {period_code: 'SP2024'})
    SET ap.period_name    = 'Spring 2024 — Kỳ Xuân 2024',
        ap.academic_year  = '2023-2024',
        ap.semester       = 'SPRING',
        ap.start_date     = date('2024-01-08'),
        ap.end_date       = date('2024-05-31');


// --- Bridge: CalendarDate → AcademicPeriod ---
MATCH (cal:CalendarDate), (ap:AcademicPeriod {period_code: 'FA2024'})
WHERE cal.full_date >= date('2024-09-02') AND cal.full_date <= date('2024-12-20')
MERGE (cal)-[:IN_PERIOD]->(ap);


// --- 4.2: Class nodes ---
MATCH (ap:AcademicPeriod {period_code: 'FA2024'}),
      (o:Organization {org_code: 'FPTU-HN'})
MERGE (c:Class {class_code: 'PRO192_SE1801'})
    SET c.class_name  = 'Lập trình Hướng đối tượng bằng Java — SE1801',
        c.class_type  = 'LECTURE',
        c.max_capacity = 35,
        c.is_active   = true
MERGE (c)-[:OFFERED_IN]->(ap)
MERGE (c)-[:HOSTED_BY]->(o);

MATCH (ap:AcademicPeriod {period_code: 'FA2024'}),
      (o:Organization {org_code: 'FPTU-HN'})
MERGE (c:Class {class_code: 'DBI202_SE1802'})
    SET c.class_name   = 'Hệ quản trị Cơ sở Dữ liệu — SE1802',
        c.class_type   = 'LECTURE',
        c.max_capacity = 30,
        c.is_active    = true
MERGE (c)-[:OFFERED_IN]->(ap)
MERGE (c)-[:HOSTED_BY]->(o);

MATCH (ap:AcademicPeriod {period_code: 'FA2024'}),
      (o:Organization {org_code: 'FPTU-HN'})
MERGE (c:Class {class_code: 'LAB_PRO192_01'})
    SET c.class_name   = 'Thực hành Lập trình Java — Lab01',
        c.class_type   = 'LAB',
        c.max_capacity = 20,
        c.is_active    = true
MERGE (c)-[:OFFERED_IN]->(ap)
MERGE (c)-[:HOSTED_BY]->(o);


// --- 4.3: Activity nodes ---
MATCH (c:Class {class_code: 'PRO192_SE1801'}),
      (e:Employee {employee_code: 'GV-HN-001'})
UNWIND [
    {name: 'Buổi 01: Giới thiệu OOP & Java Basics',  type: 'LECTURE', date: '2024-09-02', mins: 90},
    {name: 'Buổi 02: Class, Object, Constructor',     type: 'LECTURE', date: '2024-09-09', mins: 90},
    {name: 'Buổi 03: Inheritance & Polymorphism',     type: 'LECTURE', date: '2024-09-16', mins: 90},
    {name: 'Giữa kỳ: Kiểm tra lý thuyết OOP',        type: 'EXAM',    date: '2024-10-21', mins: 90},
    {name: 'Buổi 10: Collections & Generics',         type: 'LECTURE', date: '2024-11-04', mins: 90},
    {name: 'Cuối kỳ: Thi thực hành Final',            type: 'EXAM',    date: '2024-12-09', mins: 120}
] AS row
MERGE (a:Activity {class_code: 'PRO192_SE1801', scheduled_date: date(row.date), activity_type: row.type})
    SET a.activity_name     = row.name,
        a.duration_minutes  = row.mins
MERGE (a)-[:PART_OF]->(c)
MERGE (e)-[:LEADS {role: 'PRIMARY_LECTURER'}]->(a);

MATCH (c:Class {class_code: 'PRO192_SE1801'}),
      (ta:Employee {employee_code: 'TA-HN-001'})
MERGE (lab:Activity {class_code: 'PRO192_SE1801', scheduled_date: date('2024-09-04'), activity_type: 'LAB'})
    SET lab.activity_name    = 'Thực hành 01: Viết Class Java đơn giản',
        lab.duration_minutes = 90
MERGE (lab)-[:PART_OF]->(c)
MERGE (ta)-[:LEADS {role: 'TEACHING_ASSISTANT'}]->(lab);

MATCH (c:Class {class_code: 'DBI202_SE1802'}),
      (e:Employee {employee_code: 'GV-HN-002'})
UNWIND [
    {name: 'Buổi 01: Giới thiệu DBMS & SQL',     type: 'LECTURE', date: '2024-09-03', mins: 90},
    {name: 'Buổi 02: SELECT, WHERE, ORDER BY',    type: 'LECTURE', date: '2024-09-10', mins: 90},
    {name: 'Giữa kỳ: Kiểm tra SQL',              type: 'EXAM',    date: '2024-10-28', mins: 90},
    {name: 'Cuối kỳ: Thi lý thuyết DBMS',        type: 'EXAM',    date: '2024-12-16', mins: 90}
] AS row
MERGE (a:Activity {class_code: 'DBI202_SE1802', scheduled_date: date(row.date), activity_type: row.type})
    SET a.activity_name    = row.name,
        a.duration_minutes = row.mins
MERGE (a)-[:PART_OF]->(c)
MERGE (e)-[:LEADS {role: 'PRIMARY_LECTURER'}]->(a);


// ============================================================================
// PHẦN 5: STUDENT DOMAIN
// ============================================================================

// --- 5.1: Student nodes (Registration Fact — Factless Fact)
//          Person → [HAS_ROLE] → Student
// ---
MATCH (p:Person {national_id: '091234567800'})
MERGE (s:Student {student_code: 'SE180001'})
    SET s.enrollment_date = date('2022-09-05'), s.program_code = 'SE', s.is_active = true
MERGE (p)-[:HAS_ROLE]->(s);

MATCH (p:Person {national_id: '091234567801'})
MERGE (s:Student {student_code: 'SE180002'})
    SET s.enrollment_date = date('2022-09-05'), s.program_code = 'SE', s.is_active = true
MERGE (p)-[:HAS_ROLE]->(s);

MATCH (p:Person {national_id: '091234567802'})
MERGE (s:Student {student_code: 'SE180003'})
    SET s.enrollment_date = date('2022-09-05'), s.program_code = 'SE', s.is_active = true
MERGE (p)-[:HAS_ROLE]->(s);

MATCH (p:Person {national_id: '091234567803'})
MERGE (s:Student {student_code: 'SE190001'})
    SET s.enrollment_date = date('2023-09-04'), s.program_code = 'SE', s.is_active = true
MERGE (p)-[:HAS_ROLE]->(s);

MATCH (p:Person {national_id: '091234567804'})
MERGE (s:Student {student_code: 'IA190001'})
    SET s.enrollment_date = date('2023-09-04'), s.program_code = 'IA', s.is_active = true
MERGE (p)-[:HAS_ROLE]->(s);

MATCH (p:Person {national_id: '091234567805'})
MERGE (s:Student {student_code: 'AI190001'})
    SET s.enrollment_date = date('2023-09-04'), s.program_code = 'AI', s.is_active = true
MERGE (p)-[:HAS_ROLE]->(s);

MATCH (p:Person {national_id: '091234567806'})
MERGE (s:Student {student_code: 'SE200001'})
    SET s.enrollment_date = date('2024-09-02'), s.program_code = 'SE', s.is_active = true
MERGE (p)-[:HAS_ROLE]->(s);

MATCH (p:Person {national_id: '091234567807'})
MERGE (s:Student {student_code: 'SE200002'})
    SET s.enrollment_date = date('2024-09-02'), s.program_code = 'SE', s.is_active = true
MERGE (p)-[:HAS_ROLE]->(s);

// DUAL_ROLE: K17 vừa là Student vừa là Employee
MATCH (p:Person {national_id: '091234567808'})
MERGE (s:Student {student_code: 'SE170001'})
    SET s.enrollment_date = date('2021-09-06'), s.program_code = 'SE', s.is_active = true
MERGE (p)-[:HAS_ROLE]->(s);

MATCH (p:Person {national_id: '091234567809'})
MERGE (s:Student {student_code: 'SE170002'})
    SET s.enrollment_date = date('2021-09-06'), s.program_code = 'SE', s.is_active = true
MERGE (p)-[:HAS_ROLE]->(s);

// Student → Organization (đang theo học)
MATCH (s:Student) WHERE s.student_code IN ['SE180001','SE180002','SE180003','SE200001','SE200002','SE170001','SE170002']
MATCH (o:Organization {org_code: 'FPTU-HN'})
MERGE (s)-[:STUDIES_AT]->(o);

MATCH (s:Student) WHERE s.student_code IN ['SE190001','IA190001','AI190001']
MATCH (o:Organization {org_code: 'FPTU-HCM'})
MERGE (s)-[:STUDIES_AT]->(o);


// --- 5.2: Status History (State-Duration as chained relationships) ---
MATCH (s:Student {student_code: 'SE180001'})
MERGE (s)-[st:HAS_STATUS {status: 'ACTIVE', effective_from: date('2022-09-05')}]->(s)
    SET st.effective_to = null, st.note = 'Nhập học K18 ngành SE';

MATCH (s:Student {student_code: 'SE180002'})
MERGE (s)-[:HAS_STATUS {status: 'ACTIVE',     effective_from: date('2022-09-05'), effective_to: date('2023-08-31'), note: 'Nhập học K18'}]->(s)
MERGE (s)-[:HAS_STATUS {status: 'SUSPENDED',  effective_from: date('2023-09-01'), effective_to: date('2024-01-05'), note: 'Bảo lưu FA2023 vì sức khoẻ'}]->(s)
MERGE (s)-[st:HAS_STATUS {status: 'ACTIVE',     effective_from: date('2024-01-06')}]->(s)
    SET st.effective_to = null, st.note = 'Đi học lại từ kỳ SP2024';

MATCH (s:Student {student_code: 'SE180003'})
MERGE (s)-[:HAS_STATUS {status: 'ACTIVE',    effective_from: date('2022-09-05'), effective_to: date('2024-06-01'), note: 'Nhập học K18'}]->(s)
MERGE (s)-[st:HAS_STATUS {status: 'GRADUATED', effective_from: date('2024-06-01')}]->(s)
    SET st.effective_to = null, st.note = 'Tốt nghiệp loại Giỏi tháng 6/2024';

MATCH (s:Student {student_code: 'AI190001'})
MERGE (s)-[:HAS_STATUS {status: 'ACTIVE',  effective_from: date('2023-09-04'), effective_to: date('2024-03-31'), note: 'Nhập học K19 ngành AI'}]->(s)
MERGE (s)-[st:HAS_STATUS {status: 'DROPOUT', effective_from: date('2024-04-01')}]->(s)
    SET st.effective_to = null, st.note = 'Thôi học theo nguyện vọng cá nhân';


// --- 5.3: Enrollment (Factless Fact → ENROLLED_IN relationship) ---
MATCH (s:Student {student_code: 'SE180001'}), (c:Class {class_code: 'PRO192_SE1801'})
MERGE (s)-[:ENROLLED_IN {enrolled_at: date('2024-08-25'), status: 'ENROLLED'}]->(c);

MATCH (s:Student {student_code: 'SE180001'}), (c:Class {class_code: 'DBI202_SE1802'})
MERGE (s)-[:ENROLLED_IN {enrolled_at: date('2024-08-25'), status: 'ENROLLED'}]->(c);

MATCH (s:Student {student_code: 'SE180002'}), (c:Class {class_code: 'PRO192_SE1801'})
MERGE (s)-[:ENROLLED_IN {enrolled_at: date('2024-08-25'), status: 'ENROLLED'}]->(c);

MATCH (s:Student {student_code: 'SE180002'}), (c:Class {class_code: 'DBI202_SE1802'})
MERGE (s)-[:ENROLLED_IN {enrolled_at: date('2024-08-25'), status: 'ENROLLED'}]->(c);

MATCH (s:Student {student_code: 'SE200001'}), (c:Class {class_code: 'PRO192_SE1801'})
MERGE (s)-[:ENROLLED_IN {enrolled_at: date('2024-08-26'), status: 'ENROLLED'}]->(c);

MATCH (s:Student {student_code: 'SE200002'}), (c:Class {class_code: 'PRO192_SE1801'})
MERGE (s)-[:ENROLLED_IN {enrolled_at: date('2024-08-26'), status: 'ENROLLED'}]->(c);

MATCH (s:Student {student_code: 'SE190001'}), (c:Class {class_code: 'DBI202_SE1802'})
MERGE (s)-[:ENROLLED_IN {enrolled_at: date('2024-08-27'), status: 'ENROLLED'}]->(c);


// ============================================================================
// PHẦN 6: PARTICIPATION, ATTENDANCE & ASSESSMENT
// (Transaction Facts → Relationships với properties đo lường)
// ============================================================================

MATCH (s:Student {student_code: 'SE180001'}),
      (a:Activity {class_code: 'PRO192_SE1801', scheduled_date: date('2024-09-02'), activity_type: 'LECTURE'})
MERGE (s)-[r:PARTICIPATED_IN]->(a)
    SET r.participation_date = date('2024-09-02'),
        r.attendance_status  = 'PRESENT',
        r.checkin_device     = 'SCANNER_A101',
        r.quiz_score         = 8.5,
        r.quiz_max           = 10.0,
        r.grade              = 'A';

MATCH (s:Student {student_code: 'SE180002'}),
      (a:Activity {class_code: 'PRO192_SE1801', scheduled_date: date('2024-09-02'), activity_type: 'LECTURE'})
MERGE (s)-[r:PARTICIPATED_IN]->(a)
    SET r.participation_date = date('2024-09-02'),
        r.attendance_status  = 'PRESENT',
        r.checkin_device     = 'SCANNER_A101',
        r.quiz_score         = 7.0,
        r.quiz_max           = 10.0,
        r.grade              = 'B';

MATCH (s:Student {student_code: 'SE200001'}),
      (a:Activity {class_code: 'PRO192_SE1801', scheduled_date: date('2024-09-02'), activity_type: 'LECTURE'})
MERGE (s)-[r:PARTICIPATED_IN]->(a)
    SET r.participation_date = date('2024-09-02'),
        r.attendance_status  = 'ABSENT',
        r.checkin_device     = null,
        r.note               = 'Không liên lạc được';

MATCH (s:Student {student_code: 'SE180001'}),
      (a:Activity {class_code: 'PRO192_SE1801', scheduled_date: date('2024-09-09'), activity_type: 'LECTURE'})
MERGE (s)-[r:PARTICIPATED_IN]->(a)
    SET r.participation_date = date('2024-09-09'),
        r.attendance_status  = 'PRESENT',
        r.assignment_score   = 8.0,
        r.assignment_max     = 10.0,
        r.grade              = 'B+';

MATCH (s:Student {student_code: 'SE180002'}),
      (a:Activity {class_code: 'PRO192_SE1801', scheduled_date: date('2024-09-09'), activity_type: 'LECTURE'})
MERGE (s)-[r:PARTICIPATED_IN]->(a)
    SET r.participation_date = date('2024-09-09'),
        r.attendance_status  = 'LATE',
        r.note               = 'Đến muộn 15 phút',
        r.assignment_score   = 6.5,
        r.assignment_max     = 10.0,
        r.grade              = 'C+';

MATCH (s:Student {student_code: 'SE180001'}),
      (a:Activity {class_code: 'DBI202_SE1802', scheduled_date: date('2024-09-03'), activity_type: 'LECTURE'})
MERGE (s)-[r:PARTICIPATED_IN]->(a)
    SET r.participation_date = date('2024-09-03'),
        r.attendance_status  = 'PRESENT',
        r.quiz_score         = 7.0,
        r.quiz_max           = 10.0,
        r.grade              = 'B';

MATCH (s:Student {student_code: 'SE180002'}),
      (a:Activity {class_code: 'DBI202_SE1802', scheduled_date: date('2024-09-03'), activity_type: 'LECTURE'})
MERGE (s)-[r:PARTICIPATED_IN]->(a)
    SET r.participation_date = date('2024-09-03'),
        r.attendance_status  = 'PRESENT',
        r.quiz_score         = 8.0,
        r.quiz_max           = 10.0,
        r.grade              = 'B+';


// ============================================================================
// PHẦN 7: VERIFICATION QUERIES (Bỏ comment để chạy)
// ============================================================================

// Q1: Party Model — Ai đang đóng vai DUAL_ROLE?
// MATCH (p:Person)-[:HAS_ROLE]->(s:Student)
// MATCH (p)-[:HAS_ROLE]->(e:Employee)
// RETURN p.full_name, s.student_code, e.employee_code, 'DUAL_ROLE' AS identity_category;

// Q2: Traverse graph — Sinh viên Tuấn học ở lớp nào, buổi nào?
// MATCH (p:Person {full_name: 'Nguyễn Anh Tuấn'})-[:HAS_ROLE]->(s:Student)
// MATCH (s)-[:ENROLLED_IN]->(c:Class)
// MATCH (s)-[part:PARTICIPATED_IN]->(a:Activity)-[:PART_OF]->(c)
// RETURN p.full_name, c.class_code, a.activity_name, a.scheduled_date,
//        part.attendance_status, part.quiz_score;

// Q3: Đường dẫn cross-domain — Giảng viên nào dạy sinh viên nào?
// MATCH (emp_person:Person)-[:HAS_ROLE]->(e:Employee)-[:LEADS]->(a:Activity)
// MATCH (stu_person:Person)-[:HAS_ROLE]->(s:Student)-[:PARTICIPATED_IN]->(a)
// RETURN emp_person.full_name AS lecturer, stu_person.full_name AS student,
//        a.activity_name, a.scheduled_date
// ORDER BY a.scheduled_date;

// Q4: Sinh viên có lịch sử trạng thái phức tạp (bảo lưu + quay lại)
// MATCH (s:Student)-[r:HAS_STATUS]->(s)
// WHERE r.status = 'SUSPENDED'
// MATCH (p:Person)-[:HAS_ROLE]->(s)
// RETURN p.full_name, s.student_code, r.status, r.effective_from, r.effective_to, r.note;

// Q5: Shortest path — Kết nối gián tiếp giữa 2 sinh viên qua cùng giảng viên
// MATCH path = shortestPath(
//     (s1:Student {student_code: 'SE180001'})-[*]-(s2:Student {student_code: 'SE180002'})
// )
// RETURN path;
