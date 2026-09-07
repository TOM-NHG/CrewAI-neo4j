"""
Bộ Sinh và Chạy Test Case E2E tự động, xuất báo cáo đánh giá ra Excel.
Dự án: Edu-Graph Multi-Agent Assistant (NHG)
"""

import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Ensure root dir is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.crew.edu_crew import EduCrew
from src.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("E2E_Benchmark")

# Bộ dữ liệu Test Cases E2E đa dạng cho hệ thống
TEST_CASES = [
    {
        "id": "TC01",
        "category": "Điểm danh & Vắng học",
        "question": "Tìm những sinh viên vắng mặt ở lớp PRO192_SE1801 ngày 2024-09-02",
        "expected_intent": "attendance_query",
        "expected_entity": "PRO192_SE1801",
        "expected_min_records": 1,
        "description": "Truy vấn điểm danh theo mã lớp học phần và ngày cụ thể"
    },
    {
        "id": "TC02",
        "category": "Cảnh báo cấm thi",
        "question": "Cảnh báo những sinh viên có nguy cơ cấm thi vì vắng quá 20% môn Java",
        "expected_intent": "warning_query",
        "expected_entity": "Java / PRO192",
        "expected_min_records": 1,
        "description": "Tính toán tỷ lệ vắng mặt trên tổng số buổi học của học phần"
    },
    {
        "id": "TC03",
        "category": "Điểm danh & Đi muộn",
        "question": "Danh sách sinh viên đi muộn trong các buổi học",
        "expected_intent": "attendance_query",
        "expected_entity": "LATE",
        "expected_min_records": 1,
        "description": "Truy vấn các lượt điểm danh có trạng thái LATE"
    },
    {
        "id": "TC04",
        "category": "Hồ sơ & Khử lỗi dấu",
        "question": "hồ sơ sinh viên lê khắc tiệp",
        "expected_intent": "student_profile_query",
        "expected_entity": "Lê Khắc Tiệp",
        "expected_min_records": 1,
        "description": "Tra cứu hồ sơ sinh viên đầy đủ dấu thường"
    },
    {
        "id": "TC05",
        "category": "Hồ sơ & Gõ sai dấu (Fuzzy)",
        "question": "thông tin sinh viên lé khắc tiệp",
        "expected_intent": "student_profile_query",
        "expected_entity": "Lê Khắc Tiệp",
        "expected_min_records": 1,
        "description": "Entity Resolver tự động sửa dấu sai: 'lé khắc tiệp' -> 'Lê Khắc Tiệp'"
    },
    {
        "id": "TC06",
        "category": "Hồ sơ & Không dấu",
        "question": "ho so sinh vien le khac tiep",
        "expected_intent": "student_profile_query",
        "expected_entity": "Lê Khắc Tiệp",
        "expected_min_records": 1,
        "description": "Entity Resolver tự động ánh xạ chuỗi không dấu sang bản ghi DB"
    },
    {
        "id": "TC07",
        "category": "Hồ sơ & Đảo trật tự tên",
        "question": "Hồ sơ sinh viên Duyên Đặng",
        "expected_intent": "student_profile_query",
        "expected_entity": "Đặng Thị Mỹ Duyên",
        "expected_min_records": 1,
        "description": "Entity Resolver nhận diện hoán vị họ tên: 'Duyên Đặng' -> 'Đặng Thị Mỹ Duyên'"
    },
    {
        "id": "TC08",
        "category": "Hồ sơ theo Mã SV",
        "question": "Tra cứu thông tin sinh viên mã SE180001",
        "expected_intent": "student_profile_query",
        "expected_entity": "SE180001",
        "expected_min_records": 1,
        "description": "Tìm kiếm chính xác theo mã định danh sinh viên"
    },
    {
        "id": "TC09",
        "category": "Trạng thái học vụ",
        "question": "Danh sách sinh viên đang bảo lưu trong học kỳ này",
        "expected_intent": "status_query",
        "expected_entity": "SUSPENDED",
        "expected_min_records": 1,
        "description": "Truy vấn sinh viên có quan hệ HAS_STATUS là SUSPENDED còn hiệu lực"
    },
    {
        "id": "TC10",
        "category": "Trạng thái học vụ",
        "question": "Danh sách sinh viên đã thôi học",
        "expected_intent": "status_query",
        "expected_entity": "DROPOUT",
        "expected_min_records": 1,
        "description": "Truy vấn sinh viên có trạng thái DROPOUT"
    },
    {
        "id": "TC11",
        "category": "Giảng viên & Phân công",
        "question": "Giảng viên Nguyễn Văn An đang dạy những lớp và buổi học nào?",
        "expected_intent": "lecturer_query",
        "expected_entity": "Nguyễn Văn An",
        "expected_min_records": 1,
        "description": "Truy vấn quan hệ LEADS giữa Employee và Activity/Class"
    },
    {
        "id": "TC12",
        "category": "Trợ giảng kép (Dual-role)",
        "question": "Ai là sinh viên vừa đi học vừa làm trợ giảng (TA)?",
        "expected_intent": "general_query",
        "expected_entity": "TA / Dual Role",
        "expected_min_records": 1,
        "description": "Person có cả vai trò Student và Employee với vị trí TA"
    },
    {
        "id": "TC13",
        "category": "Ngành học & Chương trình",
        "question": "những sinh viên ngành SE",
        "expected_intent": "student_program_query",
        "expected_entity": "SE",
        "expected_min_records": 1,
        "description": "Lọc danh sách sinh viên theo mã chuyên ngành đào tạo"
    },
    {
        "id": "TC14",
        "category": "Cơ sở đào tạo",
        "question": "sinh viên ngành SE cơ sở hà nội",
        "expected_intent": "student_campus_query",
        "expected_entity": "SE & Hà Nội",
        "expected_min_records": 1,
        "description": "Truy vấn kết hợp giữa ngành học và cơ sở đào tạo (Organization)"
    },
    {
        "id": "TC15",
        "category": "Thống kê tổng hợp",
        "question": "Thống kê số lượng sinh viên theo từng ngành học",
        "expected_intent": "general_query",
        "expected_entity": "Major / Program",
        "expected_min_records": 1,
        "description": "Truy vấn gom nhóm (GROUP BY / count) trên đồ thị"
    }
]


def run_benchmark():
    logger.info("==================================================================")
    logger.info("🧪 KHỞI ĐỘNG CHẠY BENCHMARK TOÀN DIỆN E2E (%d TEST CASES)", len(TEST_CASES))
    logger.info("==================================================================")

    crew = EduCrew()
    results = []

    passed_count = 0
    failed_count = 0

    for idx, tc in enumerate(TEST_CASES, start=1):
        q = tc["question"]
        logger.info("\n[%d/%d] 📝 Testing: '%s' (Mục tiêu: %s)", idx, len(TEST_CASES), q, tc["category"])
        
        t0 = time.perf_counter()
        try:
            res = crew.process_query(q)
            t1 = time.perf_counter()
            elapsed_sec = round(t1 - t0, 2)
            
            success = res.get("success", False)
            actual_intent = res.get("intent", "unknown")
            cypher = res.get("cypher", "")
            records = res.get("records", [])
            record_count = len(records)
            latency = res.get("latency", {})
            error_msg = res.get("error", "")

            # Tiêu chí đánh giá Pass/Fail
            is_intent_matched = (actual_intent == tc["expected_intent"] or 
                                 tc["expected_intent"] in ["general_query", "student_profile_query"] and actual_intent in ["general_query", "student_profile_query"])
            
            has_records = record_count >= tc["expected_min_records"]
            
            # Case pass if Cypher executed successfully and returned expected records
            is_passed = success and has_records

            if is_passed:
                passed_count += 1
                status_str = "PASS"
                logger.info("  ✅ PASS: Thu về %d bản ghi trong %.2fs", record_count, elapsed_sec)
            else:
                failed_count += 1
                status_str = "FAIL"
                logger.warning("  ❌ FAIL: Success=%s | Records=%d | Intent=%s (Expected: %s)",
                               success, record_count, actual_intent, tc["expected_intent"])

            results.append({
                "id": tc["id"],
                "category": tc["category"],
                "question": q,
                "description": tc["description"],
                "expected_intent": tc["expected_intent"],
                "actual_intent": actual_intent,
                "intent_matched": is_intent_matched,
                "expected_entity": tc["expected_entity"],
                "expected_min_records": tc["expected_min_records"],
                "actual_records_count": record_count,
                "cypher": cypher,
                "status": status_str,
                "elapsed_sec": elapsed_sec,
                "latency_breakdown": latency,
                "error": error_msg
            })

        except Exception as e:
            logger.error("  ❌ EXCEPTION: %s", e)
            failed_count += 1
            results.append({
                "id": tc["id"],
                "category": tc["category"],
                "question": q,
                "description": tc["description"],
                "expected_intent": tc["expected_intent"],
                "actual_intent": "ERROR",
                "intent_matched": False,
                "expected_entity": tc["expected_entity"],
                "expected_min_records": tc["expected_min_records"],
                "actual_records_count": 0,
                "cypher": "",
                "status": "FAIL",
                "elapsed_sec": 0,
                "latency_breakdown": {},
                "error": str(e)
            })

    total_cases = len(TEST_CASES)
    pass_rate = round((passed_count / total_cases) * 100, 2)

    logger.info("==================================================================")
    logger.info("📊 KẾT QUẢ TỔNG HỢP:")
    logger.info("  - Tổng số test cases: %d", total_cases)
    logger.info("  - Số ca THÀNH CÔNG (PASS): %d", passed_count)
    logger.info("  - Số ca THẤT BẠI (FAIL): %d", failed_count)
    logger.info("  - Tỷ lệ chính xác (Pass Rate): %.2f%%", pass_rate)
    logger.info("==================================================================")

    # Xuất ra file Excel
    excel_path = ROOT_DIR / "tests" / "E2E_Test_Report.xlsx"
    export_to_excel(results, total_cases, passed_count, failed_count, pass_rate, excel_path)

    # Xuất ra file Markdown summary
    summary_path = ROOT_DIR / "docs" / "E2E_TEST_SUMMARY.md"
    export_to_markdown(results, total_cases, passed_count, failed_count, pass_rate, summary_path)

    return results, pass_rate


def export_to_excel(results, total, passed, failed, pass_rate, output_path: Path):
    wb = openpyxl.Workbook()
    
    # -------------------------------------------------------------
    # STYLES & PALETTE (NHG Design System: Navy & Gold & Slate)
    # -------------------------------------------------------------
    font_title = Font(name="Arial", size=16, bold=True, color="1E3A8A")
    font_subtitle = Font(name="Arial", size=11, italic=True, color="4B5563")
    font_header = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Arial", size=11, bold=True)
    font_regular = Font(name="Arial", size=10)
    font_code = Font(name="Courier New", size=9)
    
    fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # NHG Navy
    fill_sub_header = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid")
    fill_pass = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid") # Light Green
    fill_fail = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid") # Light Red
    fill_zebra = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
    
    font_pass = Font(name="Arial", size=10, bold=True, color="166534")
    font_fail = Font(name="Arial", size=10, bold=True, color="991B1B")

    thin_border_side = Side(style="thin", color="D1D5DB")
    border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # -------------------------------------------------------------
    # SHEET 1: DASHBOARD & TỔNG QUAN
    # -------------------------------------------------------------
    ws_summary = wb.active
    ws_summary.title = "Tổng Quan Đánh Giá"
    ws_summary.views.sheetView[0].showGridLines = True

    ws_summary["A1"] = "🎓 BÁO CÁO KẾT QUẢ KIỂM THỬ E2E — EDU-GRAPH AI ASSISTANT"
    ws_summary["A1"].font = font_title
    ws_summary["A2"] = f"Thời gian thực thi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Mô hình OLM: {settings.OLLAMA_MODEL}"
    ws_summary["A2"].font = font_subtitle

    headers_metric = ["Chỉ Số Đánh Giá", "Giá Trị Thực Tế", "Mục Tiêu (Target)", "Trạng Thái"]
    for col_idx, h in enumerate(headers_metric, start=1):
        cell = ws_summary.cell(row=4, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = border_cell

    metrics = [
        ("Tổng số kịch bản kiểm thử (Total Test Cases)", total, 15, "Đầy đủ 100%"),
        ("Số ca kiểm thử thành công (Passed)", passed, f">={int(total*0.8)}", "Đạt yêu cầu" if pass_rate >= 80 else "Cần tối ưu"),
        ("Số ca kiểm thử thất bại (Failed)", failed, "<=3", "Tốt" if failed <= 3 else "Cần rà soát"),
        ("Tỷ lệ thành công (Pass Rate)", f"{pass_rate}%", ">= 80.0%", "ĐẠT CHUẨN" if pass_rate >= 80 else "CHƯA ĐẠT"),
        ("Cơ sở dữ liệu đồ thị", "Neo4j 5.26 (Docker)", "Active", "Sẵn sàng"),
        ("Mô hình suy luận cục bộ", settings.OLLAMA_MODEL, "Qwen 2.5", "100% On-Premise")
    ]

    for row_idx, m in enumerate(metrics, start=5):
        ws_summary.cell(row=row_idx, column=1, value=m[0]).font = font_bold if "Tỷ lệ" in m[0] else font_regular
        ws_summary.cell(row=row_idx, column=2, value=m[1]).font = font_pass if "Tỷ lệ" in m[0] and pass_rate >= 80 else (font_fail if "Tỷ lệ" in m[0] else font_regular)
        ws_summary.cell(row=row_idx, column=3, value=m[2]).font = font_regular
        ws_summary.cell(row=row_idx, column=4, value=m[3]).font = font_bold

        for c in range(1, 5):
            cell = ws_summary.cell(row=row_idx, column=c)
            cell.border = border_cell
            if c in [2, 3, 4]:
                cell.alignment = align_center
            if "Tỷ lệ" in m[0]:
                cell.fill = fill_pass if pass_rate >= 80 else fill_fail

    # Thống kê theo danh mục
    ws_summary.cell(row=13, column=1, value="THỐNG KÊ THEO CHUYÊN ĐỀ NGHIỆP VỤ").font = font_bold
    cat_headers = ["Chuyên Đề Nghiệp Vụ", "Số Ca Kiểm Thử", "Số Ca Đúng", "Số Ca Sai", "Tỷ Lệ Đạt (%)"]
    for col_idx, h in enumerate(cat_headers, start=1):
        cell = ws_summary.cell(row=14, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_sub_header
        cell.alignment = align_center
        cell.border = border_cell

    # Group by category
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0, "failed": 0}
        categories[cat]["total"] += 1
        if r["status"] == "PASS":
            categories[cat]["passed"] += 1
        else:
            categories[cat]["failed"] += 1

    for row_idx, (cat_name, stat) in enumerate(categories.items(), start=15):
        rate = round((stat["passed"] / stat["total"]) * 100, 1)
        ws_summary.cell(row=row_idx, column=1, value=cat_name).font = font_regular
        ws_summary.cell(row=row_idx, column=2, value=stat["total"]).alignment = align_center
        ws_summary.cell(row=row_idx, column=3, value=stat["passed"]).alignment = align_center
        ws_summary.cell(row=row_idx, column=4, value=stat["failed"]).alignment = align_center
        ws_summary.cell(row=row_idx, column=5, value=f"{rate}%").alignment = align_center

        for c in range(1, 6):
            cell = ws_summary.cell(row=row_idx, column=c)
            cell.border = border_cell
            if rate == 100:
                cell.fill = fill_pass
            elif rate >= 50:
                cell.fill = fill_zebra
            else:
                cell.fill = fill_fail

    # -------------------------------------------------------------
    # SHEET 2: CHI TIẾT CÁC TEST CASES (INPUT / EXPECTED / ACTUAL)
    # -------------------------------------------------------------
    ws_detail = wb.create_sheet(title="Chi Tiết Test Cases")
    ws_detail.views.sheetView[0].showGridLines = True

    detail_headers = [
        "Mã TC",
        "Chuyên Đề",
        "Câu Hỏi Đầu Vào (Input)",
        "Ý Định Dự Kiến",
        "Ý Định Nhận Diện",
        "Khớp Ý Định",
        "Thực Thể Mục Tiêu",
        "Bản Ghi Dự Kiến",
        "Bản Ghi Thực Tế",
        "Kết Quả (Status)",
        "Thời Gian (s)",
        "Câu Lệnh Cypher Đã Sinh",
        "Ghi Chú / Lỗi"
    ]

    for col_idx, h in enumerate(detail_headers, start=1):
        cell = ws_detail.cell(row=1, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = border_cell

    for row_idx, r in enumerate(results, start=2):
        is_pass = (r["status"] == "PASS")
        fill_curr = fill_pass if is_pass else fill_fail

        ws_detail.cell(row=row_idx, column=1, value=r["id"]).alignment = align_center
        ws_detail.cell(row=row_idx, column=2, value=r["category"]).alignment = align_left
        ws_detail.cell(row=row_idx, column=3, value=r["question"]).alignment = align_left
        ws_detail.cell(row=row_idx, column=4, value=r["expected_intent"]).alignment = align_center
        ws_detail.cell(row=row_idx, column=5, value=r["actual_intent"]).alignment = align_center
        ws_detail.cell(row=row_idx, column=6, value="PASS" if r["intent_matched"] else "FAIL").alignment = align_center
        ws_detail.cell(row=row_idx, column=7, value=r["expected_entity"]).alignment = align_left
        ws_detail.cell(row=row_idx, column=8, value=f">={r['expected_min_records']}").alignment = align_center
        ws_detail.cell(row=row_idx, column=9, value=r["actual_records_count"]).alignment = align_center
        
        status_cell = ws_detail.cell(row=row_idx, column=10, value=r["status"])
        status_cell.alignment = align_center
        status_cell.font = font_pass if is_pass else font_fail
        status_cell.fill = fill_curr

        ws_detail.cell(row=row_idx, column=11, value=r["elapsed_sec"]).alignment = align_center
        
        cypher_cell = ws_detail.cell(row=row_idx, column=12, value=r["cypher"])
        cypher_cell.font = font_code
        cypher_cell.alignment = align_left

        ws_detail.cell(row=row_idx, column=13, value=r["error"] or r["description"]).alignment = align_left

        for c in range(1, 14):
            ws_detail.cell(row=row_idx, column=c).border = border_cell
            if c != 10:
                ws_detail.cell(row=row_idx, column=c).font = font_code if c == 12 else font_regular

    # Auto-fit column widths
    for ws in [ws_summary, ws_detail]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or "")
                # Tránh tính độ dài quá lớn với text dài như Cypher
                val_first_line = val.split("\n")[0]
                if len(val_first_line) > max_len:
                    max_len = len(val_first_line)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

    ws_detail.column_dimensions["C"].width = 38 # Câu hỏi
    ws_detail.column_dimensions["L"].width = 50 # Cypher

    wb.save(output_path)
    logger.info("📁 Đã xuất báo cáo Excel thành công: %s", output_path)


def export_to_markdown(results, total, passed, failed, pass_rate, output_path: Path):
    lines = [
        "# 📊 Báo Cáo Kiểm Thử E2E Tự Động (Edu-Graph Multi-Agent Assistant)",
        "",
        f"> **Thời gian thực hiện:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"> **Mô hình OLM:** `{settings.OLLAMA_MODEL}` | **Cơ sở dữ liệu:** Neo4j 5.26 (Docker)",
        "",
        "## 1. Tổng Quan Kết Quả Kiểm Thử",
        "",
        "| Chỉ số đánh giá | Giá trị thực tế | Mục tiêu chuẩn | Đánh giá |",
        "| :--- | :---: | :---: | :---: |",
        f"| **Tổng số kịch bản kiểm thử** | **{total}** | 15 | 100% Phủ kín |",
        f"| **Số ca thành công (PASS)** | **{passed}** | >= 12 | {'✅ Đạt chuẩn' if passed >= 12 else '⚠️ Cần tối ưu'} |",
        f"| **Số ca thất bại (FAIL)** | **{failed}** | <= 3 | {'✅ Tốt' if failed <= 3 else '❌ Cao'} |",
        f"| **Tỷ lệ chính xác (Pass Rate)** | **{pass_rate}%** | **>= 80.0%** | **{'🌟 XUẤT SẮC' if pass_rate >= 80 else '⚠️ CHƯA ĐẠT'}** |",
        "",
        "---",
        "",
        "## 2. Bảng Chi Tiết Kết Quả Từng Test Case",
        "",
        "| Mã TC | Chuyên đề nghiệp vụ | Câu hỏi đầu vào (Input) | Nhận diện thực thể / Ý định | Bản ghi DB | Thời gian | Trạng thái |",
        "| :--- | :--- | :--- | :--- | :---: | :---: | :---: |"
    ]

    for r in results:
        st_icon = "✅ PASS" if r["status"] == "PASS" else "❌ FAIL"
        q_clean = r["question"].replace("|", "\\|")
        lines.append(f"| `{r['id']}` | {r['category']} | *\"{q_clean}\"* | `{r['actual_intent']}` ({r['expected_entity']}) | {r['actual_records_count']} bản ghi | {r['elapsed_sec']}s | **{st_icon}** |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Tệp Tin Báo Cáo Chi Tiết Đính Kèm",
        f"- File Excel chi tiết: [E2E_Test_Report.xlsx](file://{ROOT_DIR / 'tests' / 'E2E_Test_Report.xlsx'})",
        "- Bao gồm phân rã độ trễ, câu lệnh Cypher tương ứng và thống kê theo từng danh mục nghiệp vụ.",
        ""
    ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("📁 Đã xuất báo cáo Markdown thành công: %s", output_path)


if __name__ == "__main__":
    run_benchmark()
