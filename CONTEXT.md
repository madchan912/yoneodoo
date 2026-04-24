# 요너두(YoNeoDoo) — 프로젝트 컨텍스트

맥북·데스크톱 등 **여러 환경에서 동일한 사실**을 맞추기 위한 문서입니다. 아키텍처나 규칙이 바뀌면 이 파일도 함께 수정하세요.

## 제품

- **요너두**: 냉장고 재료 기반으로 유튜브 요리를 찾아주는 AI 보조 서비스. 재료 매칭, 영상 노출, 단순한「내 냉장고」UX.
- **라이브**: [yoneodoo.vercel.app](https://yoneodoo.vercel.app/) (기획·로드맵 서사는 루트 `README.md` 참고)

## 레포 구성 (멀티 레포 / MSA 스타일)

| 폴더 | 역할 | 스택(요약) |
|------|------|-------------|
| `yoneodoo-web` | 사용자 UI | React 19, Vite 8, axios |
| `yoneodoo-api` | REST API, 저장소, 비즈니스 로직 | Spring Boot, Gradle에서 Java 21 툴체인, Spring Data JPA, PostgreSQL(JSONB) |
| `yoneodoo-data` | 크롤링·자막·LLM → API로 레시피 적재 | Python, Ollama 호환 OpenAI 클라이언트, youtube-transcript, scrapetube, requests |
| 루트 `README.md` | 제품·아키텍처 개요 | — |

**데이터 흐름:** `yoneodoo-data`가 유튜브 수집 → LLM으로 정규화 → **`yoneodoo-api`에 POST** → `yoneodoo-web`이 레시피·재료 검색을 **GET**으로 조회.

## Git 동기화

- **세션 시작 시 네 레포 pull 필수:** 에이전트를 새로 켜거나 프로젝트를 처음 연 뒤·다른 머신으로 옮긴 직후 작업을 시작하기 전에, **`yoneodoo-web`**, **`yoneodoo-api`**, **`yoneodoo-data`**, **멀티레포 루트(`02_Yoneodoo`)** 각각에서 `git pull`(또는 `git pull --rebase`)으로 원격과 맞출 것. 일괄 실행용 bash 예시는 `.cursorrules`를 참고한다.

## 개발 가이드 (브랜치·배포)

- **Render / Vercel**은 원격 **`main`** 브랜치를 감시해 **자동 배포**된다. 개발 중 코드가 바로 올라가면 운영이 불안정해질 수 있으므로, **일상 개발은 `develop`**, 기능 작업은 **`feature/*`**(예: `feature/recipe-search`)에서 진행한다. **배포가 필요할 때만** `develop` → `main`(또는 릴리스 PR)으로 합친다.
- 네 레포(`yoneodoo-web`, `yoneodoo-api`, `yoneodoo-data`, 메타 루트) 모두 **동일한 브랜치 이름**을 맞추는 것을 권장한다. GitHub 저장소의 **기본 브랜치(default branch)**를 `develop`으로 바꾸는 것은 선택이며, 팀 합의 후 설정한다.

## API 표면 (현재)

- `GET /api/v1/recipes` — 레시피 목록 (현재는 엔티티 그대로 노출되는 구간 있음)
- `POST /api/v1/recipes` — 크롤러가 레시피 페이로드 생성·저장 (`RecipeCreateRequest`)
- `GET /api/v1/ingredients/search?keyword=` — 기동 시 레시피 JSON에서 뽑은 재료 **인메모리 캐시** 기반 검색
- `GET /health` — 간단한 생존 확인 문자열
- `/api/v1/fridge` — 유저 기반 냉장고 API 존재. **웹 v1**은「내 냉장고」를 **localStorage**로 처리하므로, 서버 냉장고는 현재 UX에서 선택 사항.
- **Admin (`/api/v1/admin/**`)** — 헤더 `X-Admin-Secret`이 설정된 `ADMIN_SECRET`(Spring: `yoneodoo.admin.secret`)과 일치해야 통과. 예: `GET /api/v1/admin/dashboard/stats`, `GET /api/v1/admin/recipes?filter=`, `GET /api/v1/admin/ingredients/unclassified`, `POST /api/v1/admin/ingredients/mapping`. 미설정 시 해당 경로는 503.
- **`ingredient_mapping` 테이블** — `raw_name`(유니크), `master_name`: 레시피 JSON `ingredients[].name`에서 공백 제거한 키와 매칭. 미분류 = 레시피에 등장하는 정규화 이름 중 매핑에 없는 것.

## 웹 라우팅

- `/` — 기존 사용자 앱 (`App.jsx`)
- `/admin`, `/admin/recipes`, `/admin/ingredients` — **MVP 관리자 UI** (React Router). 로그인 시크릿은 **sessionStorage** + `adminClient`가 `X-Admin-Secret`으로 전송.

## 저장 모델 (현재)

- **Recipe**: JPA 엔티티, `ingredients`는 JSON 리스트 (`RecipeIngredientData`: `name`, `amount`), `videoId`, `status`, `transcript`, `youtuberName` 등.
- **User**: 소셜 필드 + `fridgeIngredients` JSON 문자열 리스트 (향후 계정·냉장고 동기화).
- **CrawlingData**: `com.yoneodoo.api.crawling` 패키지의 레거시/단순 테이블 — `Recipe` 파이프라인과 병행 필요 여부 검토 대상.

## 설정·환경

- API: `application.yaml`에서 기본 프로필 `local`; DB는 `application-local.yaml` / `application-prod.yaml`. 운영은 `DB_URL`, `DB_USER`, `DB_PASSWORD`. **어드민**은 환경변수 `ADMIN_SECRET`(YAML `yoneodoo.admin.secret`) — 로컬 기본값은 `application-local.yaml` 참고.
- 웹은 **`VITE_API_BASE_URL`** 로 API 오리진 설정 (Vite).
- **환경 파일:** `yoneodoo-web`은 `.env` / `.env.*`를 Git에서 제외하고 **`.env.example`만** 추적한다. `yoneodoo-data`도 `.gitignore`에 `.env`가 있다.
- **DB 동기화(수동):** `yoneodoo-api/scripts/sync_prod_to_local_db.py` — 운영(SOURCE) `pg_dump` → 로컬(TARGET) `pg_restore`. 접속 정보는 `scripts/.env.sync`(비밀·Git 제외) 또는 `--env-file`.

## 알려진 기술 부채 (v1)

1. **CORS**가 컨트롤러별 (`*` vs `localhost:5173`) — 한곳에서 환경별로 통합하는 편이 안전.
2. **거대 단일 UI** — 로직 대부분이 `App.jsx`에 집중 → v1.5 토글·검색 모드 확장이 어려움.
3. **재료 검색 캐시** — `@PostConstruct`에서 1회 구축 → 새 레시피 저장 후에도 재기동 전까지 검색 반영 안 될 수 있음 (별도 갱신 연동 필요).
4. **일부 API가 JPA 엔티티 직접 반환** — 클라이언트와 결합도 큼; 큰 변경 전에는 **응답 DTO** 권장.
5. **검증·에러** — Bean Validation 최소; 서비스의 `RuntimeException` → HTTP 응답 일관성 부족; 계약 안정화 시 `@ControllerAdvice` 도입 검토.
6. **문서 드리프트** — README·스크립트·환경변수명이 코드와 어긋나지 않게 주기 점검.

## 보안·운영 (v1 수준)

- 쓰기 엔드포인트(`POST /recipes`)는 규모 커지기 전에 토큰·IP 허용·내부 전용 등으로 보호 검토.
- 수정하는 구간은 `System.out` 대신 구조화 로깅(sl4fj 등) 권장.

## 코드 찾을 위치

- 웹: `yoneodoo-web/src/App.jsx`, `package.json` scripts.
- API: `yoneodoo-api/.../YoneodooApiApplication.java`, `controller/`, `service/`.
- 데이터 파이프라인: `yoneodoo-data/main.py`, `requirements.txt`, 코드에서 참조하는 `config.json`(선택).

---

*내부 논의 기준으로 정리됨: 리팩토링 우선순위, v1.5 백로그(요리명 검색 + 재료 지능화),「마스터 재료 + 승인」vs「카테고리 우선」전략.*
