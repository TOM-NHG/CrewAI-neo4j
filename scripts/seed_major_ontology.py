"""
Script khởi tạo và đồng bộ Ontology ngành học (:Major) vào Neo4j.
Tạo các node :Major và liên kết :MAJORS_IN từ :Student sang :Major.
"""

from src.db.neo4j_client import neo4j_client
from src.db.semantic_layer import MAJORS_GLOSSARY

def seed_majors():
    print("Seeding Major Ontology to Neo4j...")
    
    # 1. Tạo node Major cho từng chuyên ngành
    for code, m in MAJORS_GLOSSARY.items():
        cypher = f"""
        MERGE (m:Major {{major_code: '{code}'}})
        SET m.major_name = '{m['major_name_vi']}',
            m.major_name_en = '{m['major_name_en']}',
            m.degree = '{m['degree']}',
            m.faculty = '{m['faculty']}',
            m.description = '{m['description']}'
        RETURN m.major_code AS code
        """
        res = neo4j_client.execute_write(cypher)
        print(f"  + Node Major '{code}': {res.get('success')}")

    # 2. Tạo quan hệ MAJORS_IN giữa Student và Major dựa vào s.program_code
    rel_cypher = """
    MATCH (s:Student)
    WHERE s.program_code IS NOT NULL
    MATCH (m:Major {major_code: s.program_code})
    MERGE (s)-[:MAJORS_IN]->(m)
    RETURN count(s) AS total_linked
    """
    rel_res = neo4j_client.execute_write(rel_cypher)
    print(f"  -> Linked (s:Student)-[:MAJORS_IN]->(m:Major): {rel_res.get('success')}")

    # 3. Kiểm tra kết quả
    verify_cypher = "MATCH (m:Major) RETURN m.major_code"
    check = neo4j_client.execute_read(verify_cypher)
    print(f"Total Major nodes in Neo4j: {check.get('count')}")

if __name__ == "__main__":
    seed_majors()
