"""
레시피별 영양성분(칼로리 등)을 계산해 recipe_nutrition 테이블에 적재하는 스크립트.

실행:
  python scripts/calc_recipe_nutrition.py

접속 정보:
  yoneodoo-api/scripts/.env.sync 의 SYNC_SOURCE_* 변수 사용
"""

import sys
import re
import json
import os
from decimal import Decimal
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import psycopg2
from psycopg2.extras import RealDictCursor

# ── RDS 접속 정보: yoneodoo-api/scripts/.env.sync 에서 로드 ──────────────────
_env_path = Path(__file__).parent.parent / "yoneodoo-api" / "scripts" / ".env.sync"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

DB = dict(
    host=os.environ["SYNC_SOURCE_HOST"],
    port=int(os.environ.get("SYNC_SOURCE_PORT", 5432)),
    user=os.environ["SYNC_SOURCE_USER"],
    password=os.environ["SYNC_SOURCE_PASSWORD"],
    dbname=os.environ["SYNC_SOURCE_DB"],
    sslmode=os.environ.get("SYNC_SOURCE_SSLMODE", "require"),
)

# ── amount 파싱 ──────────────────────────────────────────────────────────────
SKIP_WORDS = {"약간", "적당히", "조금", "적당량", "조금씩", "소금", "없음", "듬뿍",
              "고소한", "매콤하게", "뿌리기", "왕창", "대용량", "송송", "얇게"}

# 재료별 1개당 기준 중량(g) — serving_size=100 기본값 외 특수 보정
PER_ITEM_G = {
    "두부": 300,    # 1모 기준
    "계란": 50,
    "감자": 150,
    "고구마": 150,
    "양파": 200,
    "대파": 100,
    "당근": 100,
    "오이": 200,
    "애호박": 250,
    "바나나": 120,
    "사과": 200,
    "토마토": 150,
    "레몬": 80,
    "오렌지": 200,
    "마늘": 5,      # 1쪽 기준
    "라임": 60,
}

def _num(s):
    """문자열에서 첫 번째 숫자 추출."""
    m = re.search(r"[\d.]+", s)
    return float(m.group()) if m else None

def parse_amount_g(amount_str, master_name, serving_size_map):
    """재료 amount 문자열 -> gram 환산. 파싱 불가 시 None 반환."""
    if not amount_str:
        return None

    s = str(amount_str).strip()

    for word in SKIP_WORDS:
        if word in s:
            return None

    # ── g / ml / cc ──────────────────────────────────────────────────────────
    m = re.search(r"([\d.]+)\s*(?:g|ml|cc|㎖)", s, re.IGNORECASE)
    if m:
        return float(m.group(1))

    # ── kg ───────────────────────────────────────────────────────────────────
    m = re.search(r"([\d.]+)\s*kg", s, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 1000

    # ── 큰술 / 스푼 / 숟가락 (1=15g) ─────────────────────────────────────────
    m = re.search(r"([\d.]+)\s*(?:큰술|스푼|숟가락|T\b|tbsp)", s, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 15
    # "스푼 숫자" 역순 패턴 (예: "스푼 1")
    m = re.search(r"(?:스푼|숟가락)\s*([\d.]+)", s)
    if m:
        return float(m.group(1)) * 15
    # 숫자 없는 "스푼" 단독 → 1스푼
    if re.fullmatch(r"\s*스푼\s*", s):
        return 15.0
    # "반 스푼" / "반스푼" / "반 스푸"
    if re.search(r"반\s*(?:스푼|스푸|숟가락)", s):
        return 7.5
    # 한글 수사 스푼: "세스푼"
    if "세스푼" in s or "세 스푼" in s:
        return 45.0
    if "두스푼" in s or "두 스푼" in s:
        return 30.0

    # ── 작은술 / tsp (1=5g) ──────────────────────────────────────────────────
    m = re.search(r"([\d.]+)\s*(?:작은술|t\b|tsp)", s, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 5

    # ── 컵 / cup (1=200g) ────────────────────────────────────────────────────
    m = re.search(r"([\d.]+)\s*(?:컵|cup)", s, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 200

    # ── 꼬집 / 두꼬집 (1꼬집=1g) ────────────────────────────────────────────
    if re.search(r"두\s*꼬집", s):
        return 2.0
    m = re.search(r"([\d.]+)\s*꼬집", s)
    if m:
        return float(m.group(1)) * 1.0
    if re.fullmatch(r"\s*꼬집\s*", s):
        return 1.0

    # ── 주먹 / 줌 / 한줌 (1=50g) ────────────────────────────────────────────
    if re.search(r"(?:한\s*주먹|한\s*줌|두\s*손\s*가득)", s):
        return 50.0
    m = re.search(r"([\d.]+)\s*(?:주먹|줌|좀)", s)
    if m:
        return float(m.group(1)) * 50

    # ── 반개 / 반모 / 반 (0.5×기준중량) ────────────────────────────────────
    if re.search(r"반\s*(?:개|모|장|통|판)", s) or re.fullmatch(r"\s*반\s*", s):
        base = PER_ITEM_G.get(master_name) or float(serving_size_map.get(master_name, 100))
        return 0.5 * base

    # ── 조각 (1조각=30g 기준) ────────────────────────────────────────────────
    m = re.search(r"([\d.]+)\s*조각", s)
    if m:
        return float(m.group(1)) * 30

    # ── 개 / 마리 / 장 / 봉 / 팩 / 포 / 쪽 / 줄 ────────────────────────────
    m = re.search(r"([\d.]+)\s*(?:개|마리|봉|팩|포|쪽|줄|알|덩이|꼬지|입)", s)
    if m:
        qty = float(m.group(1))
        base = PER_ITEM_G.get(master_name) or float(serving_size_map.get(master_name, 100))
        return qty * base
    # "개" 단독 (숫자 없음) → 1개
    if re.fullmatch(r"\s*개\s*", s):
        base = PER_ITEM_G.get(master_name) or float(serving_size_map.get(master_name, 100))
        return base
    # 한글 수사 + 개 ("열 마리" 등)
    kor_num = {"한": 1, "두": 2, "세": 3, "네": 4, "다섯": 5,
               "여섯": 6, "일곱": 7, "여덟": 8, "아홉": 9, "열": 10}
    for kor, val in kor_num.items():
        if re.search(rf"{kor}\s*(?:개|마리|알|장)", s):
            base = PER_ITEM_G.get(master_name) or float(serving_size_map.get(master_name, 100))
            return val * base

    return None


def main():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT raw_name, master_name FROM ingredient_mapping")
    raw_to_master = {r["raw_name"]: r["master_name"] for r in cur.fetchall()}

    cur.execute("""
        SELECT master_name, calories, protein, fat, saturated_fat,
               carbohydrate, sugar, sodium, serving_size
        FROM ingredient_nutrition
        WHERE calories IS NOT NULL
    """)
    nutrition_map = {}
    serving_size_map = {}
    for r in cur.fetchall():
        nutrition_map[r["master_name"]] = r
        if r["serving_size"]:
            serving_size_map[r["master_name"]] = r["serving_size"]

    cur.execute("""
        SELECT id, title, ingredients
        FROM recipes
        WHERE status = 'SUCCESS' AND display_status = 'ACTIVE'
        ORDER BY id
    """)
    recipes = cur.fetchall()
    print(f"대상 레시피: {len(recipes)}건")

    results = []

    for recipe in recipes:
        rid = recipe["id"]
        title = recipe["title"] or ""
        ingredients_raw = recipe["ingredients"]

        if isinstance(ingredients_raw, str):
            try:
                ingredients = json.loads(ingredients_raw)
            except Exception:
                ingredients = []
        elif isinstance(ingredients_raw, list):
            ingredients = ingredients_raw
        else:
            ingredients = []

        if not ingredients:
            continue

        total_count = len(ingredients)
        calc_count = 0
        nut = {k: Decimal("0") for k in ("calories", "protein", "fat", "saturated_fat",
                                           "carbohydrate", "sugar", "sodium")}

        for ing in ingredients:
            raw_name = (ing.get("name") or "").strip()
            amount_str = ing.get("amount")

            master_name = raw_to_master.get(raw_name)
            if not master_name:
                continue

            ndata = nutrition_map.get(master_name)
            if not ndata:
                continue

            amount_g = parse_amount_g(amount_str, master_name, serving_size_map)
            if amount_g is None or amount_g <= 0:
                continue

            ratio = Decimal(str(amount_g)) / Decimal("100")
            for key in nut:
                val = ndata[key]
                if val is not None:
                    nut[key] += Decimal(str(val)) * ratio

            calc_count += 1

        if calc_count == 0:
            continue

        coverage = Decimal(str(calc_count)) / Decimal(str(total_count)) * Decimal("100")

        results.append({
            "recipe_id": rid,
            "title": title,
            "calories": round(nut["calories"], 2),
            "protein": round(nut["protein"], 2),
            "fat": round(nut["fat"], 2),
            "saturated_fat": round(nut["saturated_fat"], 2),
            "carbohydrate": round(nut["carbohydrate"], 2),
            "sugar": round(nut["sugar"], 2),
            "sodium": round(nut["sodium"], 2),
            "coverage_pct": round(coverage, 2),
        })

    print(f"계산 완료: {len(results)}건 -> recipe_nutrition에 적재 시작")

    for r in results:
        cur.execute("""
            INSERT INTO recipe_nutrition
                (recipe_id, calories, protein, fat, saturated_fat,
                 carbohydrate, sugar, sodium, coverage_pct, updated_at)
            VALUES
                (%(recipe_id)s, %(calories)s, %(protein)s, %(fat)s, %(saturated_fat)s,
                 %(carbohydrate)s, %(sugar)s, %(sodium)s, %(coverage_pct)s, NOW())
            ON CONFLICT (recipe_id) DO UPDATE SET
                calories      = EXCLUDED.calories,
                protein       = EXCLUDED.protein,
                fat           = EXCLUDED.fat,
                saturated_fat = EXCLUDED.saturated_fat,
                carbohydrate  = EXCLUDED.carbohydrate,
                sugar         = EXCLUDED.sugar,
                sodium        = EXCLUDED.sodium,
                coverage_pct  = EXCLUDED.coverage_pct,
                updated_at    = NOW()
        """, r)

    conn.commit()
    print(f"적재 완료: {len(results)}건\n")

    if not results:
        print("계산된 레시피가 없습니다.")
        cur.close(); conn.close()
        return

    all_cal = [float(r["calories"]) for r in results]
    all_cov = [float(r["coverage_pct"]) for r in results]

    print("=" * 60)
    print("[전체 요약]")
    print(f"  총 계산 레시피 수  : {len(results)}건")
    print(f"  평균 칼로리        : {sum(all_cal)/len(all_cal):.1f} kcal")
    print(f"  coverage_pct 평균  : {sum(all_cov)/len(all_cov):.1f}%")

    high = [r for r in results if float(r["calories"]) > 600]
    print(f"\n[이상 레시피 - 높음] 600kcal 초과 ({len(high)}건)")
    for r in sorted(high, key=lambda x: -float(x["calories"])):
        print(f"  id={r['recipe_id']}  {r['title'][:30]}  "
              f"{float(r['calories']):.0f}kcal  coverage={float(r['coverage_pct']):.0f}%")

    low = [r for r in results if float(r["calories"]) < 100]
    print(f"\n[이상 레시피 - 낮음] 100kcal 미만 ({len(low)}건)")
    for r in sorted(low, key=lambda x: float(x["calories"])):
        print(f"  id={r['recipe_id']}  {r['title'][:30]}  "
              f"{float(r['calories']):.0f}kcal  coverage={float(r['coverage_pct']):.0f}%")

    low_cov = [r for r in results if float(r["coverage_pct"]) < 50]
    print(f"\n[신뢰도 낮음] coverage_pct 50% 미만: {len(low_cov)}건")

    bands = [(0, 200), (201, 400), (401, 600), (601, 99999)]
    labels = ["0~200", "201~400", "401~600", "601~"]
    print("\n[칼로리 분포]")
    for (lo, hi), label in zip(bands, labels):
        cnt = sum(1 for r in results if lo <= float(r["calories"]) <= hi)
        print(f"  {label:>8} kcal : {cnt}건")

    print("=" * 60)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
