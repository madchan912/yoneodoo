# 요너두 — 할 일 목록 (지금 당장)

`CONTEXT.md`, `PLAN.md`에서 뽑은 **실행 가능한 체크리스트**입니다. 완료 시 체크하고, 필요하면 날짜·담당을 적으세요.

현재 사용자용 **요리명·재료 검색** 구현은 브랜치 **`feature/recipe-search`** 에서 진행한다 (`develop`에서 분기).

## feature/recipe-search — 요리명·재료 통합 검색 (사용자 API/UI)

- [ ] **API 계약** — 검색 모드(`dish` | `ingredient` | `combined` 등)와 쿼리 파라미터 확정, 응답 DTO(썸네일·해시태그용 재료 목록 등).
- [ ] **요리명 검색** — `recipes.title` 기준 `ILIKE` 또는 PostgreSQL 전문 검색(`tsvector`); 데이터량 커지면 인덱스·`pg_trgm` 검토.
- [ ] **재료 검색 + `ingredient_mapping`** — 사용자 키워드로 `master_name` / `raw_name` 매핑 행 조회 → 동일 마스터에 묶인 **모든 `raw_name`** 집합을 확장 → 레시피 JSON `ingredients[].name`(정규화 규칙 동일)이 그 집합과 교집합이면 매칭.
- [ ] **동시 검색** — 요리명 조건과 재료 조건을 AND로 결합하는 API(또는 단일 엔드포인트에 `titleQuery` + `ingredientQuery` 옵션).
- [ ] **Web** — `PLAN.md` 토글 UX(재료로 찾기 / 요리명으로 찾기) 및 신규 API 연동, 기존 필터·냉장고 플로우와 충돌 없게.
- [ ] **통합·배포** — 기능 완료 후 `feature/recipe-search` → `develop` PR, 검증 뒤 `develop` → `main` 으로만 운영 반영.

## 기반 작업 (v1.5 기능과 병행·선행)

- [x] **웹: API 베이스 URL을 env로** — `yoneodoo-web/src/App.jsx`의 Render 하드코딩을 `import.meta.env.VITE_API_BASE_URL`(또는 팀 합의 이름)으로 교체; `yoneodoo-web/README.md`에 문서화.
- [x] **데이터: API 베이스 URL을 env로** — `yoneodoo-data/main.py`가 `.env`의 `API_BASE_URL`을 우선 사용하도록 정리; 운영 URL 하드코딩 제거 또는 기본값 가드.
- [ ] **웹 README 정합** — 스크립트: `npm run dev` / `npm run build`; Vite용 `VITE_*`; 구식 `REACT_APP_*`·`npm start` 언급 수정·삭제.
- [ ] **API: CORS** — `WebMvcConfigurer` + 프로퍼티 등 **한곳**에서 dev/prod 허용 오리진 관리; 동등 동작 확인 후 컨트롤러별 `@CrossOrigin` 제거.
- [ ] **API: 재료 캐시 갱신** — `RecipeService.saveRecipe` 이후 `IngredientSearchService` 재구축(또는 공통 `rebuildCache`)을 호출해, 재시작 없이 신규 레시피가 검색에 반영되게.

## MVP Admin (시크릿 기반 수동 운영)

- [x] **API** — `ADMIN_SECRET` / `yoneodoo.admin.secret`, `AdminSecretAuthFilter`(`X-Admin-Secret`), `AdminController` 대시보드·레시피 목록·미분류(빈) API 뼈대.
- [x] **Web** — `react-router-dom`, `/admin` 로그인(sessionStorage), `adminClient`, 사이드바·레시피 테이블·재료 매핑 UI 껍데기.
- [ ] **운영 시크릿** — Render에 `ADMIN_SECRET` 설정, 주기적 로테이션 절차 문서화.
- [x] **미분류 재료** — `IngredientMapping` 엔티티, GET 미분류 / POST 매핑 API, Admin UI(체크박스·마스터명·저장 후 새로고침), 저장 후 `IngredientSearchService` 캐시 갱신.

## v1.5 — 요리명 검색 (UX + API)

- [ ] **기획**: 토글 카피·동작(재료 vs 요리명), 빈 상태, 모바일 레이아웃 메모 확정.
- [ ] **API**: 제목/요리명 검색용 `GET`(또는 풀텍스트면 `POST`) 설계 — 쿼리 파라미터, 페이지네이션 선택, **해시태그용** 재료 부분집합을 담은 응답 DTO 필드.
- [ ] **웹**: 토글 UI 구현, 신규 엔드포인트 연동,「재료 모드」일 때 기존 필터 플로우 유지.
- [ ] **테스트**: 신규 검색 API 테스트 1개 이상 + 웹 얕은 테스트 또는 PR에 수동 체크리스트.

## v1.5 — 재료 마스터 + 승인 (카테고리 우선보다 권장)

- [ ] **모델**: 정규 재료 레코드(id, 정규명, `aliases[]`, 상태) 정의 — 테이블 또는 JSON 전략; 현재 `RecipeIngredientData`(`name`, `amount`만)에서의 마이그레이션 경로.
- [ ] **적재**: 크롤/API 저장 시 마스터로 이름 해석; 미지 → `PENDING` 큐(테이블 또는 전용 엔티티)에 원문 문자열 + 레시피 참조.
- [ ] **검토 플로우**: 최소 경로 — export 쿼리·스크립트·아주 작은 관리용 API로 별칭 승인 → 대기 레시피 재연결.
- [ ] **검색/매칭**: 해석된 정규명으로 냉장고 매칭·필터;「유사」는 초기에는 **별칭 범위**만(퍼지 확장은 사전 충분해진 뒤).

## 나중 (v1.5 이후 또는 막힐 때)

- [x] **운영→로컬 DB 동기화 스크립트** — `yoneodoo-api/scripts/sync_prod_to_local_db.py` (+ `.sh` 래퍼), `.env.sync`로 접속 정보만 주입, 확인 프롬프트로 역방향 실수 방지. (`scripts/README.md`, `.env.sync.example` 참고)
- [ ] **DTO 레이어** — 공개 GET은 JPA 엔티티가 아닌 DTO 반환.
- [ ] **전역 예외 처리** — `RuntimeException` 직투 대신 HTTP 친화적 에러.
- [ ] **Bean Validation** — `RecipeCreateRequest`, `FridgeAddRequest` 등.
- [ ] **레시피 쓰기 보호** — 크롤러→API 인증 또는 공유 시크릿.
- [ ] **`crawling` 패키지 감사** — `CrawlingData` / `CrawlingController` 유지 여부.

---

*v1.5 범위를 줄이면 순서를 바꿔도 됨. 맥북·데스크톱·배포 혼선을 줄이려면「기반 작업」을 앞에 두는 것을 권장.*
