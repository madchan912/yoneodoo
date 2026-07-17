"""
미매칭(manual_needed) 재료의 영양성분을 Gemini API로 추정해 ingredient_nutrition에 채우는 스크립트.

실행:
  python scripts/fill_nutrition_gemini.py

환경:
  GEMINI_API_KEY — yoneodoo-data/.env에서 자동 로드
  RDS 접속 정보 — 스크립트 내 하드코딩(Git 비추적 스크립트)
"""

import sys
import os
import json
import re
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ── 환경변수: yoneodoo-data/.env 로드 ─────────────────────────────────────────
env_path = Path(__file__).parent.parent / "yoneodoo-data" / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY 미설정")
    sys.exit(1)

# ── DB 접속 ───────────────────────────────────────────────────────────────────
import psycopg2

DB = dict(
    host="yoneodoo-db.cvgskwe4mv95.ap-northeast-2.rds.amazonaws.com",
    port=5432, dbname="yoneodoo", user="yoneodoo",
    password="dysjen912", sslmode="require",
)
conn = psycopg2.connect(**DB)
cur = conn.cursor()

# ── 1단계: 미매칭 목록 조회 ───────────────────────────────────────────────────
cur.execute("""
    SELECT master_name FROM ingredient_nutrition
    WHERE source = 'manual_needed'
    ORDER BY master_name;
""")
rows = cur.fetchall()
master_names = [r[0] for r in rows]
print(f"미매칭 재료 {len(master_names)}개 조회 완료\n")

if not master_names:
    print("✅ 미매칭 재료 없음")
    conn.close()
    sys.exit(0)

# ── 2단계: Gemini REST API 설정 ──────────────────────────────────────────────
import urllib.request

MODEL = "gemini-2.5-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    f"?key={GEMINI_API_KEY}"
)

PROMPT_TEMPLATE = """\
다음 식재료의 100g 기준 영양성분을 JSON으로 알려줘.
재료명: {name}
형식: {{"calories": 숫자, "protein": 숫자, "fat": 숫자, "saturated_fat": 숫자, "carbohydrate": 숫자, "sugar": 숫자, "sodium": 숫자}}
숫자만 반환. 단위 제외. 모르면 null. JSON만 출력하고 다른 텍스트 절대 금지.\
"""

def ask_gemini(name: str) -> dict | None:
    """Gemini REST API로 영양성분 JSON을 요청한다. 실패 시 None 반환."""
    prompt = PROMPT_TEMPLATE.format(name=name)
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1},
    }).encode("utf-8")
    req = urllib.request.Request(
        GEMINI_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw_resp = json.loads(resp.read().decode("utf-8"))
        text = raw_resp["candidates"][0]["content"]["parts"][0]["text"]
        match = re.search(r"\{[\s\S]*?\}", text)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"  ❌ Gemini 오류: {type(e).__name__} - {e}")
    return None

def to_dec(v) -> Decimal | None:
    """값을 Decimal로 변환. 변환 불가 시 None."""
    if v is None:
        return None
    try:
        d = Decimal(str(v))
        return d if d >= 0 else None
    except InvalidOperation:
        return None

# ── 3단계: Gemini 추정 + RDS UPDATE ──────────────────────────────────────────
UPDATE_SQL = """
UPDATE ingredient_nutrition SET
    calories      = %s,
    protein       = %s,
    fat           = %s,
    saturated_fat = %s,
    carbohydrate  = %s,
    sugar         = %s,
    sodium        = %s,
    serving_size  = 100,
    serving_unit  = 'g',
    source        = 'gemini_est',
    updated_at    = NOW()
WHERE master_name = %s;
"""

results = []   # (master_name, data, success)
failed = []

print(f"{'재료명':<18} {'칼로리':>7} {'단백질':>7} {'지방':>7} {'나트륨':>9}  결과")
print("-" * 65)

for i, name in enumerate(master_names):
    data = ask_gemini(name)
    if data is None:
        print(f"  {name:<16} —  Gemini 응답 없음")
        failed.append(name)
        time.sleep(2)
        continue

    cal  = to_dec(data.get("calories"))
    prot = to_dec(data.get("protein"))
    fat  = to_dec(data.get("fat"))
    sfat = to_dec(data.get("saturated_fat"))
    carb = to_dec(data.get("carbohydrate"))
    sug  = to_dec(data.get("sugar"))
    sod  = to_dec(data.get("sodium"))

    cur.execute(UPDATE_SQL, (cal, prot, fat, sfat, carb, sug, sod, name))
    conn.commit()

    cal_str = f"{cal}kcal" if cal is not None else "null"
    prot_str = f"{prot}g" if prot is not None else "null"
    fat_str  = f"{fat}g"  if fat  is not None else "null"
    sod_str  = f"{sod}mg" if sod  is not None else "null"
    print(f"  {name:<16} {cal_str:>9} {prot_str:>8} {fat_str:>7} {sod_str:>10}  ✅")
    results.append((name, cal, prot, fat, sod))

    # Gemini 과부하 방지
    time.sleep(1.5)

# ── 4단계: 결과 요약 ──────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print(f"완료: {len(results)}건 업데이트  /  실패: {len(failed)}건")
if failed:
    print(f"실패 목록: {', '.join(failed)}")

cur.execute("SELECT COUNT(*) FROM ingredient_nutrition WHERE source = 'gemini_est';")
count = cur.fetchone()[0]
print(f"현재 gemini_est 총 행 수: {count}")

conn.close()
