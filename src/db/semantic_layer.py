"""
Semantic Layer - Tầng Tri thức & Ngữ nghĩa Nghiệp vụ Quản lý Đào tạo.
Cung cấp từ điển danh mục (Business Glossary), từ đồng nghĩa, bản đồ thực thể (Ontology),
và công thức nghiệp vụ (Business Metrics) để làm cầu nối giữa ngôn ngữ tự nhiên và Neo4j.
"""

from typing import Dict, Any, Optional, List
import unicodedata


def normalize_str(text: str) -> str:
    """Loại bỏ dấu tiếng Việt và chuẩn hóa về chữ thường để so sánh."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFD", text)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn").lower().strip()


# 1. Từ điển Danh mục Ngành đào tạo (Major Glossary & Synonyms)
MAJORS_GLOSSARY: Dict[str, Dict[str, Any]] = {
    "SE": {
        "major_code": "SE",
        "major_name_vi": "Kỹ thuật phần mềm",
        "major_name_en": "Software Engineering",
        "degree": "Kỹ sư",
        "faculty": "Công nghệ thông tin",
        "description": "Chuyên ngành đào tạo kỹ sư phát triển phần mềm, kiến trúc hệ thống, kiểm thử và quản trị dự án phần mềm.",
        "synonyms": [
            "kỹ thuật phần mềm", "phần mềm", "software engineering", "software engineer",
            "lap trinh phan mem", "dev", "se", "ktpm"
        ]
    },
    "AI": {
        "major_code": "AI",
        "major_name_vi": "Trí tuệ nhân tạo",
        "major_name_en": "Artificial Intelligence",
        "degree": "Kỹ sư",
        "faculty": "Công nghệ thông tin",
        "description": "Chuyên ngành đào tạo kỹ sư chuyên sâu về học máy, thị giác máy tính, xử lý ngôn ngữ tự nhiên và khoa học dữ liệu.",
        "synonyms": [
            "trí tuệ nhân tạo", "tri tue nhan tao", "artificial intelligence", "ai",
            "machine learning", "khoa học dữ liệu", "data science"
        ]
    },
    "IA": {
        "major_code": "IA",
        "major_name_vi": "An toàn thông tin",
        "major_name_en": "Information Assurance",
        "degree": "Kỹ sư",
        "faculty": "Công nghệ thông tin",
        "description": "Chuyên ngành đào tạo kỹ sư an ninh mạng, mật mã học, phòng thủ tấn công mạng và bảo mật hệ thống thông tin.",
        "synonyms": [
            "an toàn thông tin", "an toan thong tin", "an ninh mạng", "an ninh mang",
            "bảo mật", "bao mat", "information assurance", "cyber security", "cybersecurity", "ia"
        ]
    },
    "BA": {
        "major_code": "BA",
        "major_name_vi": "Quản trị kinh doanh",
        "major_name_en": "Business Administration",
        "degree": "Cử nhân",
        "faculty": "Kinh tế",
        "description": "Chuyên ngành đào tạo cử nhân quản trị điều hành doanh nghiệp, marketing, tài chính và phân tích kinh doanh.",
        "synonyms": [
            "quản trị kinh doanh", "quan tri kinh doanh", "business administration", "ba", "kinh doanh", "qtkd"
        ]
    },
    "GD": {
        "major_code": "GD",
        "major_name_vi": "Thiết kế mỹ thuật số",
        "major_name_en": "Graphic Design",
        "degree": "Cử nhân",
        "faculty": "Thiết kế Đồ họa",
        "description": "Chuyên ngành đào tạo cử nhân thiết kế đồ họa, truyền thông đa phương tiện, giao diện UI/UX và hoạt hình 3D.",
        "synonyms": [
            "thiết kế mỹ thuật số", "thiết kế đồ họa", "thiet ke do hoa", "graphic design", "gd", "do hoa"
        ]
    },
    "IS": {
        "major_code": "IS",
        "major_name_vi": "Hệ thống thông tin",
        "major_name_en": "Information Systems",
        "degree": "Kỹ sư",
        "faculty": "Công nghệ thông tin",
        "description": "Chuyên ngành đào tạo kỹ sư tích hợp hệ thống thông tin quản lý, cơ sở dữ liệu doanh nghiệp và chuyển đổi số.",
        "synonyms": [
            "hệ thống thông tin", "he thong thong tin", "information systems", "is", "httt"
        ]
    }
}


# 2. Từ điển Cơ sở / Đơn vị tổ chức (Campus Glossary & Synonyms)
CAMPUS_GLOSSARY: Dict[str, Dict[str, Any]] = {
    "FPTU-HN": {
        "org_code": "FPTU-HN",
        "org_name": "Trường Đại học FPT Hà Nội",
        "location": "Khu CNC Hòa Lạc, Thạch Thất, Hà Nội",
        "synonyms": ["hà nội", "ha noi", "hòa lạc", "hoa lac", "hn", "fptu-hn"]
    },
    "FPTU-HCM": {
        "org_code": "FPTU-HCM",
        "org_name": "Trường Đại học FPT TP. Hồ Chí Minh",
        "location": "Khu CNC TP. Thủ Đức, TP. Hồ Chí Minh",
        "synonyms": ["hồ chí minh", "ho chi minh", "sài gòn", "sai gon", "hcm", "tp hcm", "fptu-hcm"]
    },
    "FPTU-DN": {
        "org_code": "FPTU-DN",
        "org_name": "Trường Đại học FPT Đà Nẵng",
        "location": "Khu đô thị FPT City, Ngũ Hành Sơn, Đà Nẵng",
        "synonyms": ["đà nẵng", "da nang", "dn", "fptu-dn"]
    },
    "FPTU-CT": {
        "org_code": "FPTU-CT",
        "org_name": "Trường Đại học FPT Cần Thơ",
        "location": "Số 600 đường Nguyễn Văn Cừ, An Bình, Ninh Kiều, Cần Thơ",
        "synonyms": ["cần thơ", "can tho", "ct", "fptu-ct"]
    },
    "FPTU-QNH": {
        "org_code": "FPTU-QNH",
        "org_name": "Trường Đại học FPT Quy Nhơn",
        "location": "Khu Đô thị An Phú Thịnh, Quy Nhơn, Bình Định",
        "synonyms": ["quy nhơn", "quy nhon", "bình định", "binh dinh", "qnh", "fptu-qnh"]
    }
}


# 3. Định nghĩa Trạng thái học vụ & Công thức Nghiệp vụ (Status Metrics)
STATUS_GLOSSARY: Dict[str, Dict[str, Any]] = {
    "ACTIVE": {
        "code": "ACTIVE",
        "name_vi": "Đang học",
        "cypher_condition": "s.is_active = true",
        "description": "Sinh viên đang theo học bình thường tại học kỳ hiện tại."
    },
    "SUSPENDED": {
        "code": "SUSPENDED",
        "name_vi": "Bảo lưu",
        "cypher_condition": "st.status = 'SUSPENDED' AND st.effective_to IS NULL",
        "description": "Sinh viên đang trong thời gian tạm hoãn/bảo lưu học tập."
    },
    "DROPPED": {
        "code": "DROPPED",
        "name_vi": "Thôi học",
        "cypher_condition": "st.status = 'DROPPED'",
        "description": "Sinh viên đã thôi học hoặc bị buộc thôi học."
    },
    "GRADUATED": {
        "code": "GRADUATED",
        "name_vi": "Đã tốt nghiệp",
        "cypher_condition": "st.status = 'GRADUATED'",
        "description": "Sinh viên đã hoàn thành toàn bộ chương trình và được cấp bằng tốt nghiệp."
    }
}


class SemanticLayer:
    """Lớp giao tiếp và tra cứu tri thức ngữ nghĩa."""

    def __init__(self):
        # Tạo chỉ mục tìm kiếm nhanh cho Major theo từ đồng nghĩa chuẩn hóa
        self._major_synonym_index: Dict[str, str] = {}
        for code, data in MAJORS_GLOSSARY.items():
            self._major_synonym_index[normalize_str(code)] = code
            self._major_synonym_index[normalize_str(data["major_name_vi"])] = code
            self._major_synonym_index[normalize_str(data["major_name_en"])] = code
            for syn in data.get("synonyms", []):
                self._major_synonym_index[normalize_str(syn)] = code

        # Chỉ mục tìm kiếm cho Campus
        self._campus_synonym_index: Dict[str, str] = {}
        for code, data in CAMPUS_GLOSSARY.items():
            self._campus_synonym_index[normalize_str(code)] = code
            self._campus_synonym_index[normalize_str(data["org_name"])] = code
            for syn in data.get("synonyms", []):
                self._campus_synonym_index[normalize_str(syn)] = code

    def resolve_major(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Nhận vào chuỗi văn bản (ví dụ: 'ngành kỹ thuật phần mềm', 'an ninh mạng', 'SE')
        và trả về thông tin chuẩn của ngành học từ từ điển.
        """
        if not text:
            return None
        clean_text = normalize_str(text)

        # 1. Khớp chính xác
        if clean_text in self._major_synonym_index:
            code = self._major_synonym_index[clean_text]
            return MAJORS_GLOSSARY.get(code)

        # 2. Khớp chuỗi con (nếu trong câu hỏi có chứa từ đồng nghĩa ngành)
        for syn, code in self._major_synonym_index.items():
            # Chỉ xét từ đồng nghĩa có độ dài từ 2 ký tự trở lên để tránh nhầm từ đơn
            if len(syn) >= 3 and syn in clean_text:
                return MAJORS_GLOSSARY.get(code)
            elif len(syn) == 2 and f" {syn} " in f" {clean_text} ":
                return MAJORS_GLOSSARY.get(code)

        return None

    def resolve_campus(self, text: str) -> Optional[Dict[str, Any]]:
        """Nhận diện cơ sở đào tạo từ câu hỏi."""
        if not text:
            return None
        clean_text = normalize_str(text)

        for syn, code in self._campus_synonym_index.items():
            if len(syn) >= 3 and syn in clean_text:
                return CAMPUS_GLOSSARY.get(code)
            elif len(syn) == 2 and f" {syn} " in f" {clean_text} ":
                return CAMPUS_GLOSSARY.get(code)

        return None

    def explain_concept(self, query: str) -> Optional[str]:
        """
        Giải thích khái niệm/mã học vụ trực tiếp từ Business Glossary
        (Dùng cho các câu hỏi tri thức dạng: 'mã SE là ngành gì', 'FPTU-HN là ở đâu').
        """
        major = self.resolve_major(query)
        if major:
            return (
                f"**Mã ngành `{major['major_code']}`** là chuyên ngành **{major['major_name_vi']}** "
                f"(*{major['major_name_en']}*), thuộc {major['faculty']}. "
                f"Văn bằng tốt nghiệp: {major['degree']}.\n\n"
                f"📌 *Mô tả chuyên ngành:* {major['description']}"
            )

        campus = self.resolve_campus(query)
        if campus:
            return (
                f"**Mã đơn vị `{campus['org_code']}`** là **{campus['org_name']}**.\n"
                f"📍 *Địa chỉ / Vị trí:* {campus['location']}."
            )

        return None

    def get_semantic_context_for_prompt(self) -> str:
        """Sinh khối ngữ cảnh Semantic gọn nhẹ để nạp vào Cypher Prompt."""
        majors_summary = ", ".join([f"{k}: {v['major_name_vi']}" for k, v in MAJORS_GLOSSARY.items()])
        campus_summary = ", ".join([f"{k}: {v['org_name']}" for k, v in CAMPUS_GLOSSARY.items()])
        return f"""[BẢN ĐỒ NGỮ NGHĨA NGHIỆP VỤ (SEMANTIC LAYER)]:
- Mã ngành học (Major Codes): {majors_summary}
  -> Tra cứu thông tin ngành: MATCH (m:Major {{major_code: 'SE'}}) RETURN m.major_code AS ma_nganh, m.major_name AS ten_nganh, m.major_name_en AS ten_tieng_anh
  -> Tìm sinh viên theo ngành: MATCH (p:Person)-[:HAS_ROLE]->(s:Student) WHERE s.program_code = 'SE' (hoặc MATCH (s)-[:MAJORS_IN]->(m:Major {{major_code: 'SE'}}))
- Mã cơ sở đào tạo (Campus Codes): {campus_summary}
- Trạng thái học vụ:
  + Đang học (ACTIVE): s.is_active = true
  + Đang bảo lưu (SUSPENDED): st.status = 'SUSPENDED' AND st.effective_to IS NULL
  + Thôi học (DROPPED): st.status = 'DROPPED'
"""


semantic_layer = SemanticLayer()
