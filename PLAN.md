# 요너두(YoNeoDoo) 프로덕트 로드맵 (v1.5 ~ v4.0)

**사실 관계**는 `CONTEXT.md`, **바로 할 일**은 `TASK.md`와 함께 읽으세요.

## 📌 핵심 원칙
1. **v1.5 단계에서는 기반 다지기에 집중**: 무리한 리팩토링보다 운영 효율(어드민)과 데이터 품질(정규화)을 우선한다.
2. **Human-in-the-Loop**: AI는 추천하고 기획자는 승인한다. 데이터 신뢰도가 최우선이다.
3. **단계적 인프라 확장**: 트래픽과 데이터 규모에 맞춰 서버 사양과 도메인을 확보한다.
4. **콘텐츠에서 커머스로**: 정보를 제공하는 수준을 넘어 실제 구매와 연결되는 BM(비즈니스 모델)을 지향한다.

---

## 🚀 v1.5 : 데이터 정제 및 어드민 확보 (마무리 단계)
**테마:** "데이터의 질(Quality)을 높이고 사령탑을 구축하라"

* **인프라 & CI/CD** ✅
    * AWS EC2(t3.micro) + RDS PostgreSQL 전환 완료 (2026-06-17).
    * GitHub Actions — main 브랜치 push 시 API(Docker rebuild) + Web(Nginx) 자동 배포 (2026-06-22).
    * 구 인프라(Render/Neon/Vercel) 삭제 완료 (2026-06-22).

* **어드민 고도화** ✅
    * 시크릿 키 기반 어드민 로그인.
    * 레시피 관리 CRUD (검색·status 연동·displayStatus Soft Delete).
    * 재료 정규화 UI: 미분류 재료 목록, 매핑/해제, JSON 그룹핑 일괄 승인 모달.
    * Gemini AI 연동: 단건 AI 추천(`/suggest`) + 전체 미분류 AI 그룹핑(`/bulk-grouping`).
    * PENDING 로직: `RecipeService.checkAndUpdateRecipeStatus()` — 크롤러 적재·어드민 수정·매핑 저장 3곳에서 자동 평가, 종료 상태(NO_SUBTITLES·FAILED·SKIP) 보호.
    * RecipeEditModal 좌우 분할 레이아웃 (자막 읽기전용 좌측, 재료 편집 우측, 1100px).
    * RecipeEditModal 미매핑 재료 표기: `GET /api/v1/admin/ingredients/mapped-names` 연동, 빨간 테두리 + ⚠ 배지.
    * RecipeManagePage 정렬·필터: ID/노출상태/파이프라인/유튜버 정렬, 노출·상태·유튜버 필터 드롭다운.
    * IngredientNormalizePage 저장 후 미분류 목록 자동 갱신.

* **사용자 검색** ✅
    * 요리명 서버사이드 검색 API (`JPQL ILIKE`).
    * 재료/요리명 토글 UI + 300ms 디바운스.
    * 재료 마스터명 변환 — 검색 캐시(`ingredient_mapping` 기반) + 레시피 카드 응답(`RecipeResponse` DTO).

* **기술 부채 정리** ✅
    * CORS 전역 통합 (`CorsConfig.java`).
    * `RecipeResponse` DTO 도입 (`updatedAt` 포함, 엔티티 직접 노출 제거).
    * 전역 예외처리 `GlobalExceptionHandler` 추가.
    * Gemini 응답 파싱 오류 수정 (`body(String.class)` + `readTree()`).
    * `recipes.updated_at` 컬럼 추가 (`@UpdateTimestamp`, 운영 RDS 마이그레이션 스크립트 `migrate_add_updated_at.sql`).
    * `sync_prod_to_local_db.py` Docker 지원 — pg_dump/pg_restore를 Docker 컨테이너 안에서 실행, `--network container:<name>` 방식으로 버전 불일치 해결.
    * `yoneodoo-api/.gitignore` Python 캐시 파일 추가.

* **잔여 작업** ✅
    * 재료 정규화 마무리 완료 (2026-06-26).
    * 운영 RDS `updated_at` 마이그레이션 실행 완료 (2026-06-26).
    * 맥북 `.env.sync` RDS/Docker 접속 정보 업데이트 완료 (2026-06-26).

---

## 🏗️ v1.9 : 브랜드 런칭 준비 (완료)
**테마:** "지인에게 당당하게 공유할 수 있는 '진짜 서비스'의 모습"

* **도메인 연결** ✅: `yoneodoo.com` 가비아 구매(2026-07-07), DNS A레코드 → EC2, Nginx server_name 설정.
* **HTTPS 인증서** ✅: Let's Encrypt / Certbot 발급, Nginx 자동 설정, 자동 갱신 구성, AWS 보안그룹 443 추가.
* **서비스 연동 업데이트** ✅: VITE_API_BASE_URL → `https://yoneodoo.com`, CORS 도메인 추가, GitHub Actions `workflow_dispatch` 트리거 추가.
* **UI 개선** ✅: 브라우저 탭 타이틀 "요너두", og 메타태그 추가, `lang="ko"` 설정.
* **데이터 벌크 적재** → v2.0으로 이동 (FastAPI 서버 구축 후 일괄 적재 예정).

---

## 🐍 v2.0 : 데이터 파이프라인 서버화 & AI 자동화
**테마:** "로컬 의존 파이프라인을 서버로 이식하고 데이터 수집을 자동화한다"

* **`yoneodoo-data` FastAPI 서버 전환** (신규 레포 없음, 기존 레포 재구성):
    * 로컬 스크립트 → FastAPI 엔드포인트로 리팩토링 (크롤링·자막 추출·LLM 재료 추출).
    * **다중 소스 수집**: 유튜브 자막(subtitle) + 더보기(description) 병행 추출.
    * **LLM**: Gemini Flash — 재료 추출 + 관련 없는 영상(요리 아님) 필터링.
    * **신규 상태값 `NEEDS_REVIEW`**: 재료 추출은 됐지만 amount가 null인 불확실한 데이터.
* **어드민 데이터 적재 UI** ✅:
    * 수동 트리거: 어드민 페이지 버튼으로 특정 유튜버 크롤링 즉시 실행.
    * 자동 배치 ✅: 매일 새벽 3시 active 유튜버 순차 크롤링 (`scheduler.py`). IP 차단 시 즉시 중단.
    * **Discord 웹훅 알림** ✅: 매일 오전 7시 전날 배치 결과 요약 리포트. 유튜버별 결과 상세 포함. 배치 이력 없으면 스킵.
* **크롤링 안정성** ✅: IP 차단 감지·즉시 중단, 자막 실패 시 더보기+댓글 폴백, 딜레이 30~60초, threading 백그라운드 실행 보장.
* **인프라**: 기존 EC2 동일 사용. 메모리 부족 시 신규 AWS 계정 Free Tier EC2 활용 검토.
* **영양성분 파이프라인** ✅ (2026-07-16):
    * `ingredient_nutrition`: 159건 영양성분 DB (식품성분표 자동매칭 125 + Gemini 추정 19 + 수동 15).
    * `recipe_nutrition`: 194건 칼로리 계산 적재. 한글 단위 전체 지원, 평균 coverage 83.1%.
    * 어드민 영양성분 관리 페이지 (`/admin/nutrition`) — 미매칭/완료 탭, 식품성분표 검색, 수정.
* **recipe_nutrition API 연동**: 레시피 응답에 칼로리 포함, coverage 50% 미만 미표시 처리.
* **RAG 식단 플래너**: 칼로리 기반 레시피 필터링 + Gemini 1주일 식단 조합 (v2 후반부).

---

## ⭐ v3.0 : 유저 경험 고도화 & 리텐션
**테마:** "데이터 락인(Lock-in)과 유저 소통 시스템 구축"

* **유저 개인화 기능**:
    * **소셜 로그인**: 구글/카카오 연동을 통한 사용자 식별.
    * **클라우드 냉장고**: 브라우저 로컬 스토리지가 아닌 DB에 냉장고 데이터 저장 (기기간 동기화).
* **데이터 분석 및 수익화 테스트**:
    * **통계 도입**: GA4 연동을 통한 DAU 및 레시피 재생/클릭 횟수 트래킹.
    * **후원 및 문의**: '커피 한 잔 후원하기' 및 '기능 제안/문의' 창구 신설.

---

## 👑 v4.0 : 운영 자동화 & 커머스 (수익 모델의 완성)
**테마:** "냉장고 데이터를 가치 있는 지능으로 변환하여 수익 창출"

* **배치 스케줄러 자동화**: 매일 새벽 지정 유튜버 신규 영상 자동 수집·적재 (yoneodoo-ai Cron).
* **RAG 고도화**: LangChain + 요너두 DB 기반 1주일 식단 자동 큐레이션, 장바구니 차분 계산.
* **커머스 어필리에이트**: 쿠팡/마켓컬리 장바구니 링크 연결 → 구매 수수료 수익 모델.

---
*로드맵 수정 시 이 파일을 업데이트하고 버전을 관리하세요.*
