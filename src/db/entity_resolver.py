"""
Mô-đun Chuẩn hóa & Ánh xạ Thực thể đối chiếu với Cơ sở dữ liệu (Database-Grounded Entity Resolver).
Giúp hệ thống tự động đoán và khớp đúng tên người, mã sinh viên, cơ sở ngay cả khi:
- Gõ sai dấu thanh (ví dụ: 'lé khắc tiệp' -> 'Lê Khắc Tiệp')
- Gõ không dấu (ví dụ: 'le khac tiep' -> 'Lê Khắc Tiệp')
- Đảo thứ tự họ tên (ví dụ: 'duyên đặng' -> 'Đặng Thị Mỹ Duyên')
- Gõ sai một vài chữ cái (Fuzzy typo matching)
"""

import time
import logging
import unicodedata
import difflib
from typing import Dict, Any, List, Optional, Tuple
from src.db.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)


def remove_vietnamese_accents(text: str) -> str:
    """Loại bỏ dấu tiếng Việt để so sánh ngữ âm thô."""
    if not text:
        return ""
    # Chuyển đổi ký tự Đ/đ riêng vì NFD không tách riêng nét gạch của đ
    s = text.replace("đ", "d").replace("Đ", "D")
    normalized = unicodedata.normalize("NFD", s)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn").lower().strip()


STOP_WORDS = {"hồ", "sơ", "sinh", "viên", "thông", "tin", "tra", "cứu", "tìm", "xem", "của", "ở", "tại", "ngành", "lớp", "học", "bạn", "em"}


class EntityResolver:
    def __init__(self, cache_ttl_seconds: int = 300):
        self.cache_ttl = cache_ttl_seconds
        self._last_loaded = 0.0
        self._persons: List[Dict[str, Any]] = []
        self._classes: List[Dict[str, Any]] = []
        self._organizations: List[Dict[str, Any]] = []

    def _refresh_cache_if_needed(self):
        """Tải trước danh sách thực thể từ Neo4j để đối chiếu trong bộ nhớ siêu nhanh (< 1ms)."""
        now = time.time()
        if now - self._last_loaded < self.cache_ttl and self._persons:
            return

        try:
            # 1. Lấy toàn bộ danh sách Person (kèm vai trò Student/Employee nếu có)
            p_res = neo4j_client.execute_read("""
                MATCH (p:Person)
                OPTIONAL MATCH (p)-[:HAS_ROLE]->(s:Student)
                OPTIONAL MATCH (p)-[:HAS_ROLE]->(e:Employee)
                RETURN p.full_name AS full_name,
                       p.national_id AS national_id,
                       s.student_code AS student_code,
                       s.program_code AS program_code,
                       e.employee_code AS employee_code
            """)
            if p_res["success"]:
                self._persons = []
                for r in p_res["records"]:
                    fn = r.get("full_name") or ""
                    self._persons.append({
                        "full_name": fn,
                        "full_name_clean": remove_vietnamese_accents(fn),
                        "words_clean": set(remove_vietnamese_accents(fn).split()),
                        "student_code": r.get("student_code"),
                        "program_code": r.get("program_code"),
                        "employee_code": r.get("employee_code")
                    })

            # 2. Lấy danh sách Organization
            o_res = neo4j_client.execute_read("""
                MATCH (o:Organization)
                RETURN o.org_code AS org_code, o.org_name AS org_name, o.org_type AS org_type
            """)
            if o_res["success"]:
                self._organizations = []
                for r in o_res["records"]:
                    name = r.get("org_name") or ""
                    code = r.get("org_code") or ""
                    self._organizations.append({
                        "org_code": code,
                        "org_name": name,
                        "name_clean": remove_vietnamese_accents(name),
                        "code_clean": code.lower()
                    })

            self._last_loaded = now
            logger.info("Đã tải Entity Resolver Cache: %d người, %d cơ sở/tổ chức",
                        len(self._persons), len(self._organizations))
        except Exception as e:
            logger.warning("Không thể làm mới Entity Resolver Cache: %s", e)

    def find_best_person_match(self, input_text: str, threshold: float = 0.6) -> Optional[Dict[str, Any]]:
        """
        Tìm kiếm người khớp nhất trong Database dựa trên chuỗi nhập vào (có dấu, sai dấu hoặc không dấu).
        """
        if not input_text or len(input_text.strip()) < 2:
            return None

        self._refresh_cache_if_needed()

        # Loại bỏ stop words để lấy cốt lõi tên
        raw_words = input_text.strip().split()
        meaningful_words = [w for w in raw_words if w.lower() not in STOP_WORDS]
        if not meaningful_words:
            meaningful_words = raw_words
        cleaned_input = " ".join(meaningful_words)

        q_clean = remove_vietnamese_accents(cleaned_input)
        q_words = set(q_clean.split())

        candidates: List[Tuple[float, Dict[str, Any]]] = []

        for p in self._persons:
            cand_name = p["full_name"]
            cand_clean = p["full_name_clean"]
            cand_words = p["words_clean"]

            # Trường hợp 1: Chuỗi không dấu trùng khớp 100%
            if q_clean == cand_clean:
                return p

            # Trường hợp 2: Toàn bộ từ người dùng nhập đều nằm trong tên DB (ví dụ: 'duyen dang' in 'dang thi my duyen')
            if q_words and q_words.issubset(cand_words):
                score = 0.95 + (len(q_words) / len(cand_words)) * 0.04
                candidates.append((score, p))
                continue

            # Trường hợp 3: Chuỗi truy vấn là chuỗi con (substring) của tên trong DB
            if len(q_clean) >= 3 and q_clean in cand_clean:
                candidates.append((0.92, p))
                continue

            # Trường hợp 4: Khớp tên chính (từ cuối cùng) và có thêm từ khác tương đồng
            if q_words and cand_words:
                last_q = q_clean.split()[-1]
                last_cand = cand_clean.split()[-1]
                if last_q == last_cand and len(last_q) >= 2:
                    overlap = len(q_words.intersection(cand_words)) / len(q_words)
                    score = 0.70 + 0.20 * overlap
                    candidates.append((score, p))
                    continue

            # Trường hợp 5: Fuzzy SequenceMatcher (sai chính tả 1-2 ký tự)
            ratio = difflib.SequenceMatcher(None, q_clean, cand_clean).ratio()
            if ratio >= threshold:
                candidates.append((ratio, p))

        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            best_score, best_match = candidates[0]
            if best_score >= threshold:
                logger.info("Entity Resolver: Ghép chuỗi '%s' -> '%s' (Độ tin cậy: %.2f)",
                            input_text, best_match["full_name"], best_score)
                return best_match

        return None

    def resolve_query_context(self, user_question: str, extracted_entities: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Quét toàn bộ câu hỏi hoặc các thực thể trích xuất để tìm đối tượng thực tế trong Neo4j.
        Trả về các thực thể đã được ánh xạ chuẩn xác với Database.
        """
        self._refresh_cache_if_needed()
        resolved = dict(extracted_entities or {})

        # 1. Thử ánh xạ từ student_name nếu Router đã bóc tách
        target_name = resolved.get("student_name")
        if target_name and isinstance(target_name, str) and target_name.strip():
            matched = self.find_best_person_match(target_name.strip())
            if matched:
                resolved["student_name"] = matched["full_name"]
                if matched.get("student_code"):
                    resolved["matched_student_code"] = matched["student_code"]
                if matched.get("program_code"):
                    resolved["matched_program_code"] = matched["program_code"]
                return resolved

        # 2. Nếu Router chưa bắt được hoặc bắt sai, thử quét cả câu hỏi loại bỏ stop words
        matched = self.find_best_person_match(user_question, threshold=0.75)
        if matched:
            resolved["student_name"] = matched["full_name"]
            if matched.get("student_code"):
                resolved["matched_student_code"] = matched["student_code"]
            if matched.get("program_code"):
                resolved["matched_program_code"] = matched["program_code"]
            return resolved

        # 3. Thử quét các n-gram từ độ dài 3 về 2
        words = user_question.strip().split()
        for n in range(min(3, len(words)), 1, -1):
            for i in range(len(words) - n + 1):
                phrase = " ".join(words[i:i+n])
                phrase_clean = remove_vietnamese_accents(phrase)
                if phrase_clean in STOP_WORDS or set(phrase_clean.split()).issubset(STOP_WORDS):
                    continue
                matched = self.find_best_person_match(phrase, threshold=0.8)
                if matched:
                    resolved["student_name"] = matched["full_name"]
                    if matched.get("student_code"):
                        resolved["matched_student_code"] = matched["student_code"]
                    if matched.get("program_code"):
                        resolved["matched_program_code"] = matched["program_code"]
                    return resolved

        return resolved


entity_resolver = EntityResolver()
