"""
식품성분표(10개정판) → ingredient_nutrition 테이블 적재 스크립트

- ingredient_mapping에서 DISTINCT master_name 조회
- alias 적용 후 식품성분표와 매칭 (정확일치 → 포함일치(생것 우선) → 역방향포함)
- 매칭 성공: 영양성분 포함해서 INSERT
- 매칭 실패: source='manual_needed'로 master_name만 INSERT

실행:
  python scripts/insert_nutrition.py
"""

import sys
import psycopg2
import openpyxl
from decimal import Decimal, InvalidOperation

sys.stdout.reconfigure(encoding="utf-8")

# ── DB 접속 ─────────────────────────────────────────────────────────────────
DB = dict(
    host="yoneodoo-db.cvgskwe4mv95.ap-northeast-2.rds.amazonaws.com",
    port=5432, dbname="yoneodoo", user="yoneodoo",
    password="dysjen912", sslmode="require",
)
conn = psycopg2.connect(**DB)
cur = conn.cursor()

# ── 1. master_name 목록 조회 ────────────────────────────────────────────────
cur.execute("SELECT DISTINCT master_name FROM ingredient_mapping ORDER BY master_name;")
master_names = [r[0] for r in cur.fetchall()]
print(f"master_name {len(master_names)}개 조회 완료\n")

# ── 2. alias 적용 ────────────────────────────────────────────────────────────
ALIASES = {
    "계란":    "달걀",
    "야채":    "채소",
    "스위트콘": "옥수수",
    "크래미":  "게맛살",
    "카레가루": "커리",
}

# ── 3. 식품성분표 파싱 ────────────────────────────────────────────────────────
# 컬럼 인덱스 (헤더 행 기준으로 확인된 값)
COL = {
    "name":         3,
    "calories":     5,
    "protein":      7,
    "fat":          8,
    "saturated_fat": 90,
    "carbohydrate": 10,
    "sugar":        11,
    "sodium":       26,
}

XLSX_PATH = r"C:\MADCHAN\Workspace\10_Projects\02_Yoneodoo\식품성분표(10개정판).xlsx"
SHEET_NAMES = [
    "국가표준식품성분 Database 10.0",
    "국가표준식품성분 Database 10.1",
    "국가표준식품성분 Database 10.2",
    "국가표준식품성분 Database 10.3",
    "국가표준식품성분 Database 10.4",
]

print("📂 식품성분표 로딩 중...")
wb = openpyxl.load_workbook(XLSX_PATH, read_only=True, data_only=True)

# 식품명 → 영양성분 dict (최신 시트가 나중에 덮어씀)
food_db: dict[str, dict] = {}
for sname in SHEET_NAMES:
    ws = wb[sname]
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i < 3:
            continue
        name = row[COL["name"]]
        if not name or not isinstance(name, str):
            continue
        name = name.strip()

        def to_num(v):
            if v is None or v == "" or v == "-":
                return None
            try:
                return Decimal(str(v))
            except InvalidOperation:
                return None

        food_db[name] = {
            "calories":      to_num(row[COL["calories"]]),
            "protein":       to_num(row[COL["protein"]]),
            "fat":           to_num(row[COL["fat"]]),
            "saturated_fat": to_num(row[COL["saturated_fat"]]),
            "carbohydrate":  to_num(row[COL["carbohydrate"]]),
            "sugar":         to_num(row[COL["sugar"]]),
            "sodium":        to_num(row[COL["sodium"]]),
        }

wb.close()
print(f"  → 고유 식품명 {len(food_db):,}개 로드 완료\n")


# ── 4. 매칭 함수 ──────────────────────────────────────────────────────────────
def simplify(name: str) -> str:
    return name.split(",")[0].strip()

def find_best(keyword: str) -> tuple[str | None, dict | None]:
    """식품성분표에서 keyword에 가장 잘 맞는 항목 반환 (food_name, nutrition)."""
    # 1) 정확 일치
    if keyword in food_db:
        return keyword, food_db[keyword]
    for fname in food_db:
        if simplify(fname) == keyword:
            return fname, food_db[fname]

    # 2) 포함 일치: keyword가 식품명 안에 포함 — "생것" 포함 항목 우선
    hits = [f for f in food_db if keyword in f]
    if hits:
        raw_first = sorted(hits, key=lambda f: (0 if "생것" in f else 1, f))
        return raw_first[0], food_db[raw_first[0]]

    # 3) 역방향 포함: 단순화된 식품명이 keyword 안에 포함 (2글자 이상)
    rev_hits = [
        f for f in food_db
        if len(simplify(f)) >= 2 and simplify(f) in keyword
    ]
    if rev_hits:
        best = sorted(rev_hits, key=lambda f: (0 if "생것" in f else 1, -len(simplify(f)), f))
        return best[0], food_db[best[0]]

    return None, None


# ── 5. INSERT ─────────────────────────────────────────────────────────────────
matched = []
unmatched = []

INSERT_SQL = """
INSERT INTO ingredient_nutrition
    (master_name, calories, protein, fat, saturated_fat,
     carbohydrate, sugar, sodium, serving_size, serving_unit, source)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (master_name) DO UPDATE SET
    calories      = EXCLUDED.calories,
    protein       = EXCLUDED.protein,
    fat           = EXCLUDED.fat,
    saturated_fat = EXCLUDED.saturated_fat,
    carbohydrate  = EXCLUDED.carbohydrate,
    sugar         = EXCLUDED.sugar,
    sodium        = EXCLUDED.sodium,
    serving_size  = EXCLUDED.serving_size,
    serving_unit  = EXCLUDED.serving_unit,
    source        = EXCLUDED.source,
    updated_at    = NOW();
"""

print("🔍 매칭 및 INSERT 시작...\n")
for master in master_names:
    keyword = ALIASES.get(master, master)
    fname, nutrition = find_best(keyword)

    if nutrition:
        cur.execute(INSERT_SQL, (
            master,
            nutrition["calories"],
            nutrition["protein"],
            nutrition["fat"],
            nutrition["saturated_fat"],
            nutrition["carbohydrate"],
            nutrition["sugar"],
            nutrition["sodium"],
            Decimal("100"),
            "g",
            "foodsafety_kr",
        ))
        matched.append((master, fname))
    else:
        # 미매칭: master_name만 적재
        cur.execute(INSERT_SQL, (
            master, None, None, None, None, None, None, None,
            None, None, "manual_needed",
        ))
        unmatched.append(master)

conn.commit()

# ── 6. 결과 출력 ──────────────────────────────────────────────────────────────
print("=" * 60)
print("=== INSERT 결과 ===")
print("=" * 60)
print(f"\n[매칭 성공] {len(matched)}건")
for master, fname in matched:
    alias_note = f" (alias: {ALIASES[master]})" if master in ALIASES else ""
    print(f"  {master}{alias_note} → {fname}")

print(f"\n[미매칭 — manual_needed] {len(unmatched)}건")
print("  " + ", ".join(unmatched))

cur.execute("SELECT COUNT(*) FROM ingredient_nutrition;")
total = cur.fetchone()[0]
print(f"\n총 INSERT: {total}건 (매칭 {len(matched)} + 미매칭 {len(unmatched)})")
print(f"매칭률: {len(matched)}/{len(master_names)} ({len(matched)/len(master_names)*100:.0f}%)")
print("=" * 60)

conn.close()
