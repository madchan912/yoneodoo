# 요너두(YoNeoDoo) — 할 일 목록 (Action Items)

`CONTEXT.md`, `PLAN.md`에서 뽑은 **실행 가능한 체크리스트**입니다.
가장 위에 있는 항목이 '지금 당장' 해야 할 최우선 과제입니다.

---

## ✅ v1.5 완료 / ✅ v1.9 완료 — 다음 목표: v2.0 (FastAPI 서버 + 데이터 벌크 적재)

---

## ✅ 완료된 작업 (v1.5)

### 인프라 & CI/CD
- [x] **AWS 인프라 구축 (2026-06-17)**: EC2(t3.micro, Ubuntu) + RDS PostgreSQL(`yoneodoo-db`, ap-northeast-2) 전환.
- [x] **GitHub Actions CI/CD (2026-06-22)**: main 브랜치 push → API Docker rebuild + Web Nginx 자동 배포.
- [x] **구 인프라 삭제 완료 (2026-06-22)**: Render(백엔드), Neon(DB), Vercel(프론트) 전부 삭제.
- [x] **로컬 DB 동기화 스크립트 Docker 지원**: `scripts/sync_prod_to_local_db.py` Docker 기반 재작성 — pg_dump/pg_restore를 `SYNC_PG_IMAGE` 컨테이너에서 실행, `--network container:<name>` 방식으로 버전 불일치 해결.

### 어드민 고도화
- [x] **어드민 로그인 & 기본 UI**: 시크릿 기반 인증, 대시보드, 미분류 재료 목록.
- [x] **재료 정규화 UI 고도화**: 아코디언, 검색 필터, JSON 그룹핑 붙여넣기, 승인 모달 개선, 레시피 미리보기 패널.
- [x] **Gemini AI 연동**:
  - 단건 AI 추천 (`POST /api/v1/admin/ingredients/suggest`, `gemini-2.5-flash`).
  - 전체 미분류 AI 그룹핑 (`POST /api/v1/admin/ingredients/bulk-grouping`, 청크 50개씩).
  - Gemini 응답 파싱 오류 수정 (`body(JsonNode.class)` → `body(String.class)` + `readTree()`).
- [x] **어드민 레시피 관리 개선**: 검색, status 연동, status 드롭다운/승급 버튼, 로드맵 탭 제거.
- [x] **레시피 Soft Delete**: `displayStatus` 컬럼(`ACTIVE`/`HIDDEN`) 추가, 어드민 토글 UI.
- [x] **미분류 재료 포함 레시피 75개 HIDDEN 처리 (2026-06-22)**.
- [x] **태스크 보드 가독성 개선**: 마크다운 렌더링, 체크박스 라이트 컬러스킴.
- [x] **PENDING 로직 구현**:
  - `RecipeService.checkAndUpdateRecipeStatus(Recipe)` 공통 메서드 추출.
  - Trigger A: 크롤러 적재(`RecipeService.saveRecipe`) 후 자동 평가.
  - Trigger B: 어드민 레시피 수정(`AdminService.updateRecipe`) 후 자동 평가.
  - Trigger C: 재료 매핑 저장(`saveIngredientMappings` / `bulkSaveIngredientMappings`) 후 관련 레시피 재평가.
  - 종료 상태(NO_SUBTITLES·FAILED·SKIP)는 덮어쓰지 않음.
  - 미리보기 모달 각 레시피 카드에 [✏️ 수정] 버튼 추가 — RecipeEditModal을 zIndex=11000으로 열고, 저장 후 미리보기 목록 자동 재조회.
- [x] **RecipeEditModal 좌우 분할 레이아웃**:
  - 모달 너비 1100px, 좌측=자막(읽기전용 `<pre>`, 독립 스크롤), 우측=재료 편집(독립 스크롤).
  - 상단 헤더 필드(제목/상태/URL) + 하단 저장/취소 버튼 고정 풀너비.
- [x] **RecipeEditModal 미매핑 재료 표기**:
  - `GET /api/v1/admin/ingredients/mapped-names` API 추가.
  - 모달 오픈 시 `Promise.all`로 레시피+매핑목록 동시 조회.
  - 미매핑 재료: 빨간 테두리 + ⚠ 텍스트 + 패널 헤더 배지 "⚠ 미매핑 N개".
- [x] **RecipeManagePage 정렬·필터**:
  - 클라이언트 정렬: ID/노출상태/파이프라인/유튜버 (컬럼 헤더 클릭, ↑↓ 아이콘).
  - 필터: 노출상태 셀렉트, 파이프라인 상태 셀렉트, 유튜버명 텍스트 입력, × 초기화 버튼.
- [x] **IngredientNormalizePage 저장 후 미분류 목록 자동 갱신**:
  - RecipeEditModal `onSaved` 콜백에서 `load()` 호출 → 해소된 항목 즉시 사라짐.
- [x] **재료 정규화 완료 (2026-06-26)**: `ingredient_mapping` 미매핑 raw_name 전체 매핑 완료.
- [x] **운영 RDS `updated_at` 마이그레이션 실행 (2026-06-26)**: `migrate_add_updated_at.sql` 운영 RDS 적용 완료.
- [x] **맥북 `.env.sync` 접속 정보 업데이트 (2026-06-26)**: `SYNC_SOURCE_HOST` 등 AWS RDS 정보 맥북 환경에도 동기화 완료.

### 사용자 검색
- [x] **요리명 검색 API**: `GET /api/v1/recipes/search?q=` (JPQL ILIKE, status/displayStatus 필터 적용).
- [x] **재료/요리명 토글 UI**: `searchMode` 상태, 300ms 디바운스, 빈 쿼리 시 전체 목록 표시.
- [x] **재료 마스터명 변환**: `IngredientSearchService` 캐시 원천을 `ingredient_mapping.master_name` 기준으로 변경 + 레시피 응답 재료명 master_name 치환.

### 기술 부채 & 기타
- [x] **CORS 전역 통합**: `CorsConfig.java` 신규, 4개 컨트롤러 `@CrossOrigin` 제거. 허용 오리진: localhost:5173, 43.201.95.155.
- [x] **RecipeResponse DTO 도입**: `status`/`displayStatus`/`transcript` 미노출, `updatedAt` 포함, 재료명 master_name 변환 통합.
- [x] **전역 예외처리**: `GlobalExceptionHandler.java` — `ResponseStatusException` / `IllegalArgumentException` / `RuntimeException` / catch-all 처리.
- [x] **카피라이트 추가**: `© 2026 요너두. All rights reserved.` (App.jsx footer).
- [x] **CLAUDE.md 에이전틱 검증 기준 추가**: `./gradlew compileJava` + `npm run build` 완료 후 보고 규칙.
- [x] **웹/API 베이스 URL 환경변수 통일**: `VITE_API_BASE_URL`.
- [x] **recipes `updated_at` 컬럼 추가**: `@UpdateTimestamp` 자동 갱신, `RecipeResponse` DTO 포함, 운영 RDS 마이그레이션 스크립트(`migrate_add_updated_at.sql`) 작성.
- [x] **yoneodoo-api `.gitignore` Python 캐시 추가**: `__pycache__/`, `*.pyc`, `*.pyo`.

---

## ✅ 완료된 작업 (v1.9)

- [x] **커스텀 도메인 구매 (2026-07-07)**: 가비아 `yoneodoo.com` 구매, DNS A레코드 → EC2, Nginx server_name 설정.
- [x] **HTTPS 인증서 (2026-07-07)**: Let's Encrypt / Certbot 발급, Nginx 자동 설정, 자동 갱신 구성, AWS 보안그룹 443 추가.
- [x] **VITE_API_BASE_URL 도메인으로 변경**: GitHub Secrets `https://yoneodoo.com` 업데이트.
- [x] **CORS 도메인 추가**: `https://yoneodoo.com`, `https://www.yoneodoo.com`.
- [x] **GitHub Actions `workflow_dispatch` 트리거 추가**: yoneodoo-web, yoneodoo-api 수동 배포 가능.
- [x] **브라우저 탭 타이틀 및 og 메타태그 수정**: title "요너두", og:title/og:description 추가, `lang="ko"`.
- [x] **CLAUDE.md 문서 동기화 규칙 강화**: API/CORS/인프라 변경 시 CONTEXT.md 동기화 의무화.

---

## ✅ 완료된 작업 (v2.0)

- [x] **`yoneodoo-data` FastAPI 서버 전환** (기존 레포 재구성):
  - 로컬 스크립트 → FastAPI 엔드포인트로 리팩토링 완료.
  - 다중 소스 수집: 유튜브 자막(subtitle) + 더보기(description) + 댓글 병행.
  - LLM: Gemini Flash — 재료 추출 + amount null → NEEDS_REVIEW 상태.
  - 신규 상태값 `NEEDS_REVIEW` 추가 (`checkAndUpdateRecipeStatus` 종료 상태로 처리).
- [x] **채널 전체 영상 수 조회 UI** (`GET /channel-info`):
  - FastAPI `GET /channel-info?channel_url=` → scrapetube로 전체 숏츠 수 반환.
  - Spring Boot AdminController 프록시 추가 → 프론트에서 조회.
  - `YoutuberManagePage.jsx`: 크롤링 트리거 클릭 시 "전체 영상: N개" 표시, end 인덱스 자동 설정.
- [x] **채널 전체 영상 수 + Gemini 일일 한도 체크**:
  - `get_channel_videos` → `(slice, total)` 튜플 반환.
  - `GEMINI_DAILY_LIMIT=1400` (여유치 100), 초과 시 크롤링 자동 중단.
- [x] **유튜버 관리 + 크롤링 이력** (`watched_youtubers`, `crawl_history` 테이블):
  - 유튜버 CRUD (등록/삭제/활성 토글) + 레시피 수 실시간 집계.
  - 크롤링 트리거 → RUNNING 이력 INSERT → done/failed 시 UPDATE + `last_crawled_at` 갱신.
  - `CrawlProxyService` RestTemplate 전환 (RestClient 빈 등록 오류 해결).
- [x] **어드민 유튜버 관리 페이지** (`YoutuberManagePage.jsx`):
  - 유튜버 등록/목록/토글/삭제 UI.
  - 크롤링 트리거 + 3초 폴링으로 실시간 진행 상태 표시.
  - 크롤링 이력 테이블 (KST 변환, result_summary 파싱).
- [x] **크롤링 안정성 개선** (2026-07-15):
  - `transcript.py` / `description.py` / `comment.py`: IP 차단 감지 시 상위로 re-raise.
  - `pipeline.py`: RequestBlocked 감지 시 즉시 `blocked` 상태로 크롤링 전체 중단.
  - `pipeline.py`: 자막 실패 시 더보기+댓글로 Gemini 재시도, 셋 다 없을 때만 NO_SUBTITLES.
  - `pipeline.py`: 영상 간 딜레이 20~40초 → 30~60초 강화.
  - `crawl.py`: `BackgroundTasks` → `threading.Thread(daemon=True)` 교체 — 프론트 연결 끊겨도 크롤링 계속 실행.
  - `YoutuberService.java`: `finishCrawlHistory` 조건 `"running".equals(status)` → `!"done".equals(status)` — failed→done 덮어쓰기 허용.
- [x] **동시 배포 충돌 방지** (2026-07-15):
  - `yoneodoo-api` GitHub Actions `deploy.yml`에 `sleep 300` (5분) 대기 추가 — yoneodoo-data가 먼저 기동된 후 API 배포.
- [x] **자동 배치 크롤링 + Discord 알림** (2026-07-15):
  - `scheduler.py`: 매일 03:00 `GET /api/v1/admin/youtubers`로 active 유튜버 순차 크롤링. IP 차단 시 즉시 배치 전체 중단. 유튜버별 결과 수집.
  - `scheduler.py`: 07:00 Discord 리포트 — 배치 이력 없으면 스킵.
  - `discord.py`: 배치 결과 임베드 전송 (차단=빨강/실패=주황/정상=초록). 유튜버별 결과 상세 포함.
  - 환경변수 추가: `DISCORD_WEBHOOK_URL`, `SPRING_API_BASE_URL`, `ADMIN_SECRET`.
  - `test_discord.py`: 웹훅 테스트 스크립트 (`.env.data.prod`에서 URL 로드).
- [x] **식품성분표 기반 영양성분 DB 구축 + 어드민 관리 페이지** (2026-07-15):
  - `food_nutrition_master` 테이블: 식품성분표(10개정판) 전 5개 시트 16,535건 적재 (`scripts/insert_food_master.py`).
  - `ingredient_nutrition` 테이블: `ingredient_mapping.master_name` 기준 159건 — 자동 매칭 125건(foodsafety_kr) + 수동 필요 34건(manual_needed) (`scripts/insert_nutrition.py`).
  - `NutritionAdminController`: 5개 어드민 엔드포인트 (`GET /stats`, `GET /unmatched`, `GET /matched`, `GET /search`, `PUT /{masterName}`).
  - `NutritionManagePage.jsx`: 좌우 분할 UI — 좌측 미매칭/완료 탭·통계, 우측 식품성분표 검색·영양값 폼·저장. `/admin/nutrition` 라우트 추가.
  - Gemini API로 `manual_needed` 19건 추정값 채우기 (`scripts/fill_nutrition_gemini.py`, source=`gemini_est`). 캡사이신 1건 null 유지.
  - 완료 탭: source별 배지(식품DB=초록/AI=주황/수동=파랑), 클릭 시 기존 값 폼 자동 채움·수정 가능.

- [x] **레시피 칼로리 계산 파이프라인 구축** (2026-07-16):
  - `recipe_nutrition` 테이블 RDS 생성 (coverage_pct 신뢰도 지표 포함).
  - `scripts/calc_recipe_nutrition.py`: SUCCESS+ACTIVE 레시피 194건 칼로리·영양성분 계산 후 일괄 적재.
  - 한글 단위 전체 지원: 큰술=15g, 작은술=5g, 컵=200g, **스푼=15g**, 숟가락=15g, 꼬집=1g, 주먹/줌=50g, kg, 반개/반모, 한글 수사(한/두/세...) 등.
  - 단위 파싱 개선으로 평균 coverage 30% → **83.1%** (+53.1%p), 신뢰도낮음(<50%) 141건 → **14건** (-127건).
  - 평균 칼로리 599kcal (194건), 분포: 0~200(29건) / 201~400(54건) / 401~600(48건) / 601~(62건).
  - 이상 레시피 분석 완료: 과대(5046kcal 컵누들 — `스푼 숫자` 역순 파싱 버그), 과소(63kcal 비빔밥 — 주재료 밥 누락).

- [x] **AI 식단 플래너 UI 구현** (2026-07-17):
  - `MealPlannerModal.jsx`: 자연어 입력 → `POST /api/v1/search/meal-plan` 연동. 로딩 스피너, 결과 표시(** 마크다운 제거), 참고 레시피 유튜브 링크.
  - `App.jsx`: `?beta=true` URL 파라미터일 때만 `🤖 AI 식단` 플로팅 버튼 노출 (냉장고 버튼 위). 일반 URL에서는 숨김.
  - EC2 Nginx `index.html` no-cache 설정 추가 → 배포 후 새로고침 없이 즉시 반영.

- [x] **RAG 식단 플래너 기초 구현** (2026-07-17):
  - `recipe_embeddings` 테이블: `recipe_id`, `embedding vector(768)`, `updated_at`. pgvector `<=>` 코사인 유사도.
  - `GeminiApiService.embedContent()`: `gemini-embedding-001` 모델, `outputDimensionality: 768`.
  - `RecipeEmbeddingService.embedAndSave()`: 레시피 저장 시 자동 임베딩 + 백필 API (`POST /api/v1/admin/embeddings/backfill`).
  - `RecipeEmbeddingRepository`: `CAST(:embedding AS vector)` named parameter (`?2::vector` → Hibernate ParameterLabelException 수정).
  - `RecipeSearchService`: 4단계 RAG 파이프라인 — ①Gemini 조건 추출(JSON) ②조건 텍스트 벡터화 ③pgvector 유사도 검색(coverage_pct≥50) ④Gemini 식단 조합.
  - `POST /api/v1/search/meal-plan` 공개 API (`RecipeSearchController`). `{ meal_plan, recipes, conditions }` 반환.

- [x] **EC2 IP 변경 + Elastic IP 고정** (2026-07-17):
  - 기존 EC2(43.201.95.155) → 신규 EC2(3.37.238.221) 이전.
  - Elastic IP 할당 — 재시작해도 IP 변경 없음.
  - `CorsConfig.java` 허용 오리진 업데이트, Nginx server_name 수정, CONTEXT.md 반영.

- [x] **Gemini API 유료 전환** (2026-07-17):
  - 선불 크레딧 충전, 새 API 키 발급.
  - EC2 `~/.env.data.prod`, 로컬 `yoneodoo-data/.env` 키 교체 완료.

- [x] **유지만 외 레시피 삭제 + 시퀀스 리셋** (2026-07-17):
  - 1mincook(1), 1mindiet(5), 이름없음(1) 총 7건 삭제.
  - `recipe_embeddings` 7건, `recipe_nutrition` 1건 연쇄 삭제.
  - 시퀀스 리셋: `recipes_2_id_seq`=208, `recipe_embeddings_id_seq`=208, `recipe_nutrition_id_seq`=358.
  - 현재 RDS 레시피: 유지만 208건.

## 🔮 넥스트 백로그 (v2.0 잔여 ~ v4.0)

### v2.0 잔여
- [x] **임베딩 백필 완료** (2026-07-17): 214건 전체 백필 완료. `success:214, failed:0`. EC2 localhost 직접 호출로 nginx 타임아웃 우회.
- [ ] **recipe_nutrition API 연동**: `GET /api/v1/recipes` 응답에 칼로리 포함. coverage_pct 50% 미만은 칼로리 미표시 처리.
- [ ] **이상 레시피 보정**: 5046kcal 컵누들(`스푼 숫자` 역순 파서 버그), 63kcal 비빔밥(밥 누락), `없음`/`대용량` amount 입력 레시피 수동 보정.
- [ ] **롱폼 영상 지원**: 숏츠 외 일반 영상(long-form)도 크롤링·레시피 추출 가능하도록 파이프라인 확장. scrapetube `content_type` 파라미터 및 API 범위 조정 필요.

### v3.0 — 유저 경험 고도화 & 리텐션
- [ ] **소셜 로그인**: 구글/카카오 연동.
- [ ] **클라우드 냉장고**: localStorage → DB 저장 (기기간 동기화).
- [ ] **GA4 통계**: DAU, 레시피 클릭/재생 트래킹.
- [ ] **후원하기**: 커피 한 잔 후원 창구 신설.

### v4.0 — 운영 자동화 & 커머스
- [ ] **배치 스케줄러 자동화**: 매일 새벽 지정 유튜버 신규 영상 자동 수집·적재.
- [ ] **RAG 고도화**: LangChain + 자체 DB 기반 1주일 식단 자동 큐레이션, 장바구니 차분 계산.
- [ ] **커머스 어필리에이트**: 쿠팡/마켓컬리 장바구니 링크 연결 → 구매 수수료 수익 모델.
