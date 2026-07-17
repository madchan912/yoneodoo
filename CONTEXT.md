# 요너두(YoNeoDoo) — 프로젝트 컨텍스트

맥북·데스크톱 등 **여러 환경에서 동일한 사실**을 맞추기 위한 문서입니다. 아키텍처나 규칙이 바뀌면 이 파일도 함께 수정하세요.

## 제품

- **요너두**: 냉장고 재료 기반으로 유튜브 요리를 찾아주는 AI 보조 서비스. 재료 매칭, 영상 노출, 단순한「내 냉장고」UX.
- **라이브**: https://yoneodoo.com (2026-07-07 도메인/HTTPS 적용 완료)
- **구 인프라(삭제 완료)**: Vercel(프론트), Render(백엔드), Neon(DB) — 2026-06-22 삭제 완료.

## 레포 구성 (멀티 레포 / MSA 스타일)

| 폴더 | 역할 | 스택(요약) |
|------|------|-------------|
| `yoneodoo-web` | 사용자 UI | React 19, Vite 8, axios |
| `yoneodoo-api` | REST API, 저장소, 비즈니스 로직 | Spring Boot, Gradle에서 Java 21 툴체인, Spring Data JPA, PostgreSQL(JSONB) |
| `yoneodoo-data` | 크롤링·자막·LLM → API로 레시피 적재 (v2.0 FastAPI 서버 전환 완료) | Python, FastAPI, Gemini Flash, youtube-transcript, scrapetube, yt-dlp, requests |
| 루트 `README.md` | 제품·아키텍처 개요 | — |

**데이터 흐름:** `yoneodoo-data`가 유튜브 수집 → LLM으로 정규화 → **`yoneodoo-api`에 POST** → `yoneodoo-web`이 레시피·재료 검색을 **GET**으로 조회.

## Git 동기화

- **세션 시작 시 네 레포 pull 필수:** 에이전트를 새로 켜거나 프로젝트를 처음 연 뒤·다른 머신으로 옮긴 직후 작업을 시작하기 전에, **`yoneodoo-web`**, **`yoneodoo-api`**, **`yoneodoo-data`**, **멀티레포 루트(`02_Yoneodoo`)** 각각에서 `git pull`(또는 `git pull --rebase`)으로 원격과 맞출 것.

## 개발 가이드 (브랜치·배포)

- **AWS EC2**에 직접 배포하는 방식 (2026-06-17 전환 완료). Render/Vercel 자동 배포는 더 이상 사용하지 않는다.
  - **프론트엔드**: EC2 위 Nginx가 `yoneodoo-web` 빌드 산출물(`dist/`)을 서빙.
  - **백엔드**: EC2 위 Docker 컨테이너로 Spring Boot 실행.
  - **DB**: AWS RDS PostgreSQL (`yoneodoo-db`, `ap-northeast-2`).
- **CI/CD**: GitHub Actions — `main` 브랜치 push 시 자동 배포 (2026-06-22 구축 완료).
  - API: SSH → git pull → docker build → docker run (port 8080)
  - Data: SSH → git pull → docker build → docker run (port 8000)
  - Web: npm build → SCP dist → nginx reload
- **일상 개발은 `develop`**, 기능 작업은 **`feature/*`** 에서 진행. **배포는 `main` 머지로 자동 트리거**.

## API 표면 (현재)

- `GET /api/v1/recipes` — 레시피 목록 (`RecipeResponse` DTO, `status=SUCCESS & displayStatus=ACTIVE` 필터, 재료명 master_name 변환)
- `GET /api/v1/recipes/search?q=` — 요리명 키워드 서버사이드 검색 (JPQL ILIKE, 동일 필터 적용)
- `POST /api/v1/recipes` — 크롤러가 레시피 페이로드 생성·저장 (`RecipeCreateRequest`)
- `GET /api/v1/ingredients/search?keyword=` — 기동 시 `ingredient_mapping.master_name` 기준 인메모리 캐시 검색 (초성·자모 지원)
- `GET /health` — 간단한 생존 확인 문자열
- `/api/v1/fridge` — 유저 기반 냉장고 API. 웹 v1은 localStorage로 처리하므로 현재 UX에서 선택 사항.
- **FastAPI (`yoneodoo-data`, port 8000)** — 크롤링·LLM 파이프라인 서버. 주요 엔드포인트:
  - `POST /crawl` — 채널 크롤링 시작 (job_id 반환, threading.Thread 백그라운드 실행)
  - `GET /status/{job_id}` — 크롤링 진행 상태 조회
  - `GET /channel-info?channel_url=` — 채널 전체 숏츠 수 조회
  - `GET /health` — 생존 확인
  - **스케줄러**: 매일 03:00 active 유튜버 순차 크롤링 → 07:00 Discord 리포트
- `POST /api/v1/search/meal-plan` — RAG 식단 플래너 (공개). `{ "query": "자연어" }` → Gemini 조건 추출 → pgvector 유사도 검색(coverage_pct≥50) → Gemini 식단 조합. `{ meal_plan, recipes, conditions }` 반환.
- **Admin (`/api/v1/admin/**`)** — 헤더 `X-Admin-Secret` 인증 필수. 주요 엔드포인트:
  - `GET /api/v1/admin/dashboard/stats` — 대시보드 집계
  - `GET /api/v1/admin/recipes`, `GET /api/v1/admin/recipes/{id}`, `PUT /api/v1/admin/recipes/{id}` — 레시피 CRUD
  - `GET /api/v1/admin/ingredients/unclassified` — 미분류 재료 목록
  - `POST /api/v1/admin/ingredients/mapping` — 재료 매핑 저장
  - `GET /api/v1/admin/ingredients/mapped-names` — 매핑된 재료 raw_name 전체 목록 (`List<String>`, RecipeEditModal 미매핑 표기용)
  - `POST /api/v1/admin/ingredients/suggest` — Gemini AI 단건 마스터명 추천
  - `POST /api/v1/admin/ingredients/bulk-grouping` — Gemini AI 전체 미분류 그룹핑 (청크 50개씩)
  - `POST /api/v1/admin/ingredients/bulk-map` — AI 그룹핑 결과 일괄 매핑 저장
  - `POST /api/v1/admin/crawl` — FastAPI 크롤링 트리거 (job_id 반환)
  - `GET /api/v1/admin/crawl/status/{jobId}` — 크롤링 진행 상태 조회
  - `GET /api/v1/admin/crawl/history` — 크롤링 이력 목록 (최신순, `crawl_history` 테이블)
  - `GET /api/v1/admin/youtubers` — 등록된 유튜버 목록 (레시피 수 포함)
  - `POST /api/v1/admin/youtubers` — 유튜버 등록 (`channelUrl`, `youtuberName`)
  - `DELETE /api/v1/admin/youtubers/{id}` — 유튜버 삭제 (이력 유지)
  - `PATCH /api/v1/admin/youtubers/{id}/toggle` — 유튜버 활성/비활성 토글
  - `GET /api/v1/admin/nutrition/stats` — 영양성분 전체/완료/미완료 카운트
  - `GET /api/v1/admin/nutrition/unmatched` — 수동 입력 필요 재료 목록 (source='manual_needed')
  - `GET /api/v1/admin/nutrition/matched` — 완료 재료 목록 (source != 'manual_needed', 이름순)
  - `GET /api/v1/admin/nutrition/search?keyword=` — 식품성분표(food_nutrition_master) 키워드 검색 (최대 20건)
  - `PUT /api/v1/admin/nutrition/{masterName}` — 재료 영양 값 저장
- **`ingredient_mapping` 테이블** — `raw_name`(유니크) → `master_name`: 레시피 JSON `ingredients[].name`과 매칭. 미분류 = 매핑에 없는 raw_name.

## 웹 라우팅

- `/` — 사용자 앱 (`App.jsx`) — 재료 검색 / 요리명 검색 토글, 냉장고 관리. `?beta=true` 파라미터 시 🤖 AI 식단 플래너 버튼(우측 하단 플로팅) 노출 → `MealPlannerModal` 오픈
- `/admin`, `/admin/recipes`, `/admin/ingredients`, `/admin/youtubers`, `/admin/nutrition` — **MVP 관리자 UI** (React Router). 로그인 시크릿은 **sessionStorage** + `adminClient`가 `X-Admin-Secret`으로 전송.

## 저장 모델 (현재)

- **Recipe**: JPA 엔티티, `ingredients`는 JSON 리스트(`RecipeIngredientData`: `name`, `amount`), `videoId`, `status`, `displayStatus`(Soft Delete), `transcript`, `youtuberName`, `createdAt`, `updatedAt`(`@UpdateTimestamp` 자동 갱신) 등. **사용자 응답은 `RecipeResponse` DTO로 분리** (`status`/`displayStatus`/`transcript` 미포함, `updatedAt` 포함). **상태값**: `NEEDS_REVIEW` (재료 추출됐지만 amount null인 불확실 데이터, `checkAndUpdateRecipeStatus`가 종료 상태로 처리).
- **User**: 소셜 필드 + `fridgeIngredients` JSON 문자열 리스트 (향후 계정·냉장고 동기화).
- **IngredientMapping**: `raw_name`(유니크), `master_name` — 재료 정규화 핵심 테이블.
- **WatchedYoutuber**: `watched_youtubers` 테이블 — `channel_url`, `youtuber_name`, `is_active`(배치 크롤링 포함 여부), `last_crawled_at`, `created_at`. `ddl-auto: update`로 자동 생성.
- **CrawlHistory**: `crawl_history` 테이블 — `youtuber_name`, `channel_url`, `job_id`(FastAPI UUID), `start_idx`, `end_idx`, `status`(running/done/failed), `result_summary`(TEXT, JSON), `triggered_by`(manual/batch), `started_at`, `finished_at`. `ddl-auto: update`로 자동 생성.
- **IngredientNutrition**: `ingredient_nutrition` 테이블 — `master_name`(UNIQUE, `ingredient_mapping.master_name`과 1:1), 영양성분 7개 필드(calories/protein/fat/saturated_fat/carbohydrate/sugar/sodium, NUMERIC(7,2)), `serving_size`=100, `serving_unit`="g", `source`(foodsafety_kr/manual/gemini_est/manual_needed). 식품성분표 자동 매칭 125건 + Gemini 추정 19건(gemini_est) + 수동 필요 15건(manual_needed, 캡사이신 1건 null 유지). 모든 값은 100g 기준.
- **FoodNutritionMaster**: `food_nutrition_master` 테이블 — 식품성분표(10개정판) 전 5개 시트 16,535건. `food_name`, `food_group`, 영양성분 7개, `source_ver`(10.0~10.4). 어드민 영양성분 검색 원천 데이터. `food_name` ILIKE 검색 시 DISTINCT ON으로 중복 제거.
- **RecipeNutrition**: `recipe_nutrition` 테이블 — `recipe_id`(BIGINT UNIQUE), 영양성분 7개(NUMERIC(7,2)), `coverage_pct`(NUMERIC(5,2)). coverage_pct = 계산된 재료수 / 전체 재료수 × 100 (신뢰도 지표). 194건 적재, 평균 coverage 83.1%. scripts/calc_recipe_nutrition.py로 재계산 가능(한글 단위 전체 지원: 스푼=15g, 큰술=15g, 작은술=5g, 컵=200g, 꼬집=1g, 주먹/줌=50g 등).

## 설정·환경

- API: `application.yaml`에서 기본 프로필 `local`; DB는 `application-local.yaml` / `application-prod.yaml`. 운영은 `DB_URL`, `DB_USER`, `DB_PASSWORD`. **어드민**은 환경변수 `ADMIN_SECRET`. **FastAPI 서버 URL**은 `YONEODOO_DATA_URL` (기본값: `http://localhost:8000`).
- Data: `yoneodoo-data/.env` (Git 제외). 주요 환경변수: `GEMINI_API_KEY`, `API_BASE_URL`(Spring recipes 엔드포인트), `SPRING_API_BASE_URL`(Spring 루트, 기본 `http://localhost:8080`), `ADMIN_SECRET`(Spring 어드민 인증), `DISCORD_WEBHOOK_URL`(배치 리포트 웹훅, 없으면 알림 스킵).
- 웹은 **`VITE_API_BASE_URL`** 로 API 오리진 설정 (Vite).
- **CORS**: `CorsConfig.java`에서 전역 관리. 허용 오리진: `http://localhost:5173`, `http://43.201.95.155`, `https://yoneodoo.com`, `https://www.yoneodoo.com`.
- **환경 파일:** `yoneodoo-web`은 `.env` / `.env.*`를 Git에서 제외. `scripts/.env.sync`도 Git 제외(비밀).
- **DB**: AWS RDS PostgreSQL (`yoneodoo-db`, `yoneodoo-db.cvgskwe4mv95.ap-northeast-2.rds.amazonaws.com`, db.t3.micro). Neon에서 이전 완료(2026-06-17).
- **DB 동기화(수동):** `yoneodoo-api/scripts/sync_prod_to_local_db.py` — Docker 기반으로 운영(RDS) `pg_dump` → 로컬 `pg_restore`. pg_dump/pg_restore는 `SYNC_PG_IMAGE`(기본 `postgres:16`) Docker 컨테이너 안에서 실행하므로 로컬에 PostgreSQL 바이너리 불필요. 접속 정보는 `scripts/.env.sync`(Git 제외, `SYNC_DOCKER_CONTAINER`, `SYNC_PG_IMAGE` 포함).

## 환경 이전 시 수동 복사 필요 파일 (Git 미추적)

| 파일 | 이유 |
|------|------|
| `yoneodoo-api/scripts/.env.sync` | RDS 접속 정보 + Docker 컨테이너명. 없으면 DB 동기화 스크립트 실행 불가 |
| `yoneodoo-api/src/main/resources/application-local.yaml` | 로컬 DB 접속 정보 + ADMIN_SECRET. 없으면 API 로컬 실행 불가 |
| `yoneodoo-web/.env` | VITE_API_BASE_URL. 없으면 API 호출 엔드포인트 빈값 |
| `yoneodoo-data/.env` | GEMINI_API_KEY, API_BASE_URL, SPRING_API_BASE_URL, ADMIN_SECRET, DISCORD_WEBHOOK_URL |
| `yoneodoo-data/.env.data.prod` | EC2 운영용 — `test_discord.py` 실행 시 웹훅 URL 로드에 사용 |
| `02_Yoneodoo/scripts/calc_recipe_nutrition.py` | RDS 직접 접속 — recipe_nutrition 재계산 스크립트 (환경변수 없이 하드코딩, .gitignore 제외 아님이나 민감정보 포함) |
| `02_Yoneodoo/scripts/fill_nutrition_gemini.py` | GEMINI_API_KEY + RDS 직접 접속 — manual_needed 항목 Gemini 추정값 채우기 |
| `02_Yoneodoo/scripts/insert_nutrition.py` | RDS 직접 접속 — ingredient_nutrition 초기 적재 (재실행 시 사용) |

## 인프라 현황 (2026-07-07 기준)

| 구성 요소 | 서비스 | 세부 정보 |
|-----------|--------|-----------|
| EC2 | AWS ap-northeast-2 | `yoneodoo-api`(8080) + `yoneodoo-data`(8000, v2.0 배포 예정), t3.micro, Ubuntu — 백엔드(Docker) + 프론트(Nginx) 통합 |
| RDS | AWS ap-northeast-2 | `yoneodoo-db`, PostgreSQL, db.t3.micro |
| IAM | AWS | `yoneodoo-admin` 사용자, 최소 권한 |
| 보안 그룹 | AWS | `yoneodoo-ec2-sg`(HTTP/SSH), `yoneodoo-rds-sg`(EC2 → RDS 5432) |
| pem 키 | 로컬 | `C:\Users\madchan\Desktop\yoneodoo-key.pem` (Git 제외) |
| GitHub Actions | CI/CD | main 브랜치 push → EC2 자동 배포 |
| 서비스 URL | — | https://yoneodoo.com (2026-07-07 정식 적용) |
| 도메인 | 가비아 | yoneodoo.com, www.yoneodoo.com (DNS A레코드 → EC2) |
| HTTPS | Let's Encrypt / Certbot | 자동 갱신 설정 완료, 443 보안그룹 추가 |
| Render | 삭제 완료 | 2026-06-22 |
| Neon | 삭제 완료 | 2026-06-22 |
| Vercel | 삭제 완료 | 2026-06-22 |

## 알려진 기술 부채 (v2.0 대상)

1. **거대 단일 UI**: 로직 대부분이 `App.jsx`에 집중 → 컴포넌트 분리 필요.
2. **캐시 갱신 연동 부분 미완**: 레시피 저장 후 `IngredientSearchService.initCache()` 자동 갱신 연동 확인 필요.
3. **검증·에러**: Bean Validation 최소; 계약 안정화 시 `@ControllerAdvice` 고도화 검토.

## 보안·운영 (v1 수준)

- 쓰기 엔드포인트(`POST /recipes`)는 규모 커지기 전에 토큰·IP 허용·내부 전용 등으로 보호 검토.
- `System.out` 대신 구조화 로깅(slf4j) 적용 중.

## 코드 찾을 위치

- 웹: `yoneodoo-web/src/App.jsx`, `src/pages/admin/`, `package.json` scripts.
- API: `yoneodoo-api/.../controller/`, `service/`, `admin/`, `config/`.
- 데이터 파이프라인: `yoneodoo-data/main.py`, `requirements.txt`.

---

*내부 논의 기준으로 정리됨: v1.5/v1.9 완료(2026-07-07). v2.0 완료(2026-07-15~17): FastAPI 전환, 다중 소스 수집, Gemini Flash, NEEDS_REVIEW, 유튜버 관리 UI, 채널 영상 수 조회, 배치 스케줄러(03:00), Discord 알림(07:00), IP 차단 감지·중단, 크롤링 안정성 강화, 영양성분 파이프라인(ingredient_nutrition 159건·recipe_nutrition 194건·coverage 83.1%), RAG 식단 플래너(POST /api/v1/search/meal-plan, recipe_embeddings 214건, ?beta=true 조건 노출). v2.0 잔여: recipe_nutrition API 연동, 이상 레시피 보정, 롱폼 영상 지원.*
