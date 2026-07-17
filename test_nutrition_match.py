"""
식품성분표(10개정판) ↔ ingredient_mapping.master_name 매칭 테스트

매칭 우선순위:
  1. 정확 일치  : master_name == 식품명 (또는 그 앞부분 — 쉼표 전)
  2. 포함 일치  : master_name이 식품명 안에 포함 ("닭가슴살" in "닭고기(가슴, 생것)")
  3. 역방향 포함: 식품명(단순화)이 master_name 안에 포함 ("가슴" in "닭가슴살")

실행:
  python test_nutrition_match.py
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

import openpyxl

# ── 1. master_name 목록 ─────────────────────────────────────────────────────
MASTER_NAMES = [
    "김", "깨", "물", "밤", "밥", "빵",
    "가지", "간장", "감자", "계란", "고추", "김치", "깻잎", "당근", "대파",
    "된장", "두부", "두유", "딸기", "라면", "마늘", "맛술", "면수", "명란",
    "바질", "버섯", "버터", "부추", "상추", "새우", "설탕", "소금", "소면",
    "소스", "숙주", "스팸", "스프", "식빵", "식초", "쌈무", "야채", "양파",
    "어묵", "얼음", "오이", "우유", "유부", "육수", "전분", "쪽파", "참외",
    "참치", "채소", "치즈", "케첩", "후추",
    "건미역", "견과류", "고구마", "고추장", "골뱅이", "굴소스", "김가루",
    "누룽지", "다짐육", "단백질", "두유면", "들기름", "또띠아", "레몬즙",
    "매실액", "메밀면", "바나나", "베리류", "베이글", "베이컨", "삼겹살",
    "소고기", "소시지", "순두부", "시금치", "시리얼", "알배추", "애호박",
    "양배추", "양상추", "오트밀", "와사비", "요거트", "우삼겹", "참기름",
    "참치액", "콩나물", "크래미", "탄산수", "토마토", "파슬리", "핫소스",
    "현미떡", "호박씨",
    "감태버터", "고춧가루", "김밥용김", "녹차티백", "닭가슴살", "대패목살",
    "돼지고기", "들깨가루", "땅콩가루", "땅콩버터", "마라소스", "마요네즈",
    "머스터드", "멸치액젓", "밀가루면", "병아리콩", "분말스프", "불닭소스",
    "블루베리", "사골곰탕", "스리라차", "스위트콘", "아보카도", "알룰로스",
    "오리고기", "올리브유", "위트빅스", "유성스프", "청양고추", "체다치즈",
    "치킨스톡", "카다이프", "카레가루", "캡사이신", "코인육수", "파스타면",
    "파프리카", "팽이버섯", "표고버섯", "후레이크",
    "가쓰오부시", "다시마버터", "다크초콜릿", "메이플시럽", "바닐라시럽",
    "바베큐소스", "바질페스토", "새송이버섯", "시나몬가루", "양송이버섯",
    "올리브오일", "콘킹소세지", "토마토소스", "페페론치노",
    "단백질쉐이크", "라이스페이퍼", "아몬드브리즈",
    "무가당코코아가루", "피스타치오스프레드",
]

# ── 2. 식품성분표 식품명 수집 (10.0 ~ 10.4 전체, 중복 제거) ─────────────────
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

food_names: set[str] = set()
for sname in SHEET_NAMES:
    ws = wb[sname]
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i < 3:
            continue  # 헤더 2행 + 빈 행 스킵
        val = row[3]  # D열 = 식품명
        if val and isinstance(val, str):
            food_names.add(val.strip())

wb.close()
print(f"  → 고유 식품명 {len(food_names):,}개 로드 완료\n")

# ── 3. 식품명 단순화 헬퍼 ──────────────────────────────────────────────────
def simplify(name: str) -> str:
    """쉼표 앞 부분만 추출하고 공백 제거. 예: '감자, 생것' → '감자'"""
    return name.split(",")[0].strip()

simplified_foods = {simplify(f) for f in food_names}

# ── 4. 매칭 ────────────────────────────────────────────────────────────────
exact: dict[str, list[str]] = {}       # master → [일치한 식품명들]
contains: dict[str, list[str]] = {}    # master → [포함된 식품명들]
reverse: dict[str, list[str]] = {}     # master → [역방향 포함 식품명들]
unmatched: list[str] = []

for master in MASTER_NAMES:
    m_lower = master.lower()

    # 1) 정확 일치 (단순화된 식품명과 비교)
    exact_hits = [f for f in food_names if simplify(f) == master]
    if exact_hits:
        exact[master] = sorted(exact_hits)
        continue

    # 2) 포함 일치: master가 식품명 안에 포함
    contains_hits = [f for f in food_names if master in f]
    if contains_hits:
        contains[master] = sorted(contains_hits)
        continue

    # 3) 역방향 포함: 식품명 단순화가 master 안에 포함 (단 1글자 제외)
    rev_hits = [
        f for f in food_names
        if len(simplify(f)) >= 2 and simplify(f) in master
    ]
    if rev_hits:
        reverse[master] = sorted(rev_hits)
        continue

    unmatched.append(master)

# ── 5. 결과 출력 ────────────────────────────────────────────────────────────
print("=" * 60)
print("=== 매칭 결과 ===")
print("=" * 60)

print(f"\n[정확 일치] {len(exact)}건")
for master, foods in sorted(exact.items()):
    preview = foods[0]
    extra = f" 외 {len(foods)-1}건" if len(foods) > 1 else ""
    print(f"  {master} → {preview}{extra}")

print(f"\n[포함 일치] {len(contains)}건")
for master, foods in sorted(contains.items()):
    preview = foods[0]
    extra = f" 외 {len(foods)-1}건" if len(foods) > 1 else ""
    print(f"  {master} → {preview}{extra}")

print(f"\n[역방향 포함] {len(reverse)}건")
for master, foods in sorted(reverse.items()):
    preview = foods[0]
    extra = f" 외 {len(foods)-1}건" if len(foods) > 1 else ""
    print(f"  {master} → {preview}{extra}")

print(f"\n[미매칭] {len(unmatched)}건")
print("  " + ", ".join(unmatched))

matched = len(exact) + len(contains) + len(reverse)
total = len(MASTER_NAMES)
print("\n" + "=" * 60)
print(f"전체 매칭률: {matched}/{total} ({matched/total*100:.0f}%)")
print(f"  정확 일치: {len(exact)}건  |  포함 일치: {len(contains)}건  |  역방향: {len(reverse)}건  |  미매칭: {len(unmatched)}건")
print("=" * 60)
