# 요너두(YoNeoDoo) — 할 일 목록 (Action Items)

`CONTEXT.md`, `PLAN.md`에서 뽑은 **실행 가능한 체크리스트**입니다. 
가장 위에 있는 항목이 '지금 당장' 해야 할 최우선 과제입니다.

---

## 🚨 최우선 과제: 환경 동기화 & 인프라 정비 (v1.5 ~ v1.9)

- [ ] **로컬 환경 동기화 (Mac ↔ Win)**: 
  - `.gitignore` 처리된 비밀 파일(`application-local.yaml`, `.env` 등) 맥북으로 이식.
  - 프론트 `npm install` 및 백엔드 로컬 DB 구동 확인.
- [ ] **운영 서버 업그레이드 (Render)**:
  - 백엔드 서버를 Starter 플랜($7/월)으로 업그레이드하여 24시간 가동 및 속도 확보.
  - 기존 5분 단위 헬스체크(Ping) 봇 스케줄러 해지.
- [ ] **커스텀 도메인 연결**:
  - 가비아/호스팅케이알 등에서 `.kr` 또는 `.com` 도메인 구매 후 Vercel 연동.

---

## 🤖 어드민 고도화 및 AI 정규화 (v1.5)

- [x] **어드민 로그인 & 미분류 재료 UI**: 시크릿 기반 로그인, 재료 매핑/해제 리스트 UI 및 API 구축.
- [x] **AI 반자동 매핑 (Human-in-the-Loop)**:
  - **API**: `POST /api/v1/admin/ingredients/suggest` 엔드포인트 + `GeminiProperties`/`IngredientSuggestionService` 도입. `gemini-1.5-flash` 호출, JSON 응답 (`{"masterName":"..."}`) 보수적 파싱. 키 미설정 503, 외부 4xx/5xx 502, 타임아웃 504.
  - **Web**: 미분류 목록 상단 [✨ AI 매핑 추천] 버튼 → 체크된 재료들을 보내 추천값을 마스터명 입력창에 자동 입력만 함(저장은 사람이 직접 [매핑 저장] 확정).
- [x] **어드민 레시피 수정 기능 (CRUD)**:
  - API: `GET /api/v1/admin/recipes/{id}`, `PUT /api/v1/admin/recipes/{id}` (요리명·유튜브 URL·재료 배열·displayStatus·**status**(파이프라인 코드 수동 보강) 수정, 저장 후 검색 캐시 자동 갱신).
  - Web: 레시피 관리 표에서 [수정] 버튼 → 모달에서 제목·재료·노출 토글·**status 드롭다운/[✓ SUCCESS 로 승급] 버튼**·유튜브 새창/복사까지 한 화면에서 처리.
- [x] **레시피 Soft Delete (displayStatus 도입)**:
  - DB/Entity: `Recipe.displayStatus` 컬럼(enum `ACTIVE`/`HIDDEN`, 기본값 `ACTIVE`) 추가. 기존 파이프라인 `status`와 의미 분리.
  - API: `PUT /api/v1/admin/recipes/{id}` 에서 `displayStatus` 변경 가능. 사용자용 `GET /api/v1/recipes`, `IngredientSearchService` 캐시는 `ACTIVE` 만 노출. 어드민 목록은 두 상태 모두 표시.
  - Web: `RecipeEditModal` 에 [노출/숨김] 토글 추가 + `youtubeUrl` 읽기 전용 처리. `RecipeManagePage` 행에 노출 상태 뱃지.
- [x] **태스크 보드 가독성 개선**: `TaskBoardPage` 마크다운 본문 대비 강화 + 체크박스 라이트 컬러스킴 강제(`color-scheme: light`)로 다크 톤에서도 또렷하게 보이게.
- [x] **어드민 태스크 보드 (로드맵)**:
  - API: `GET /api/v1/admin/tasks` — 프로젝트 루트의 `TASK.md` 원문을 그대로 반환 (시스템 프로퍼티 `yoneodoo.task.markdownPath` 또는 환경변수 `YONEODOO_TASK_MD_PATH` 로 경로 오버라이드 가능).
  - Web: 사이드바 [대시보드 / 로드맵] 메뉴, `react-markdown` + `remark-gfm` 으로 체크박스·표 포함 렌더.
- [ ] **초기 데이터 벌크 적재**:
  - 맥북/데스크톱 로컬 환경에서 파이썬 크롤러를 구동하여 레시피 2,000~3,000개 수집 후 운영 DB로 다이렉트 이식.

---

## 🔍 사용자 검색 UX (feature/recipe-search)

현재 `develop`에서 분기한 `feature/recipe-search` 브랜치에서 진행.

- [ ] **요리명 검색 API**: `recipes.title` 기준 `ILIKE` 또는 전문 검색(`tsvector`) 구현.
- [ ] **재료 검색 동기화**: 사용자 키워드 -> `ingredient_mapping` 마스터명 조회 -> 묶인 모든 raw_name 교집합으로 레시피 매칭.
- [ ] **Web 검색 UI 토글**: 「재료로 찾기」 vs 「요리명으로 찾기」 토글 UI 구현 및 신규 API 연동.
- [ ] **캐시 갱신 로직**: 레시피 추가/수정 또는 재료 매핑 완료 시 검색 캐시(`IngredientSearchService`) 자동 갱신.

---

## 📦 기반 작업 및 기술 부채 해결 (수시 진행)

- [x] 웹/API 베이스 URL `.env` 환경변수로 통일 완료.
- [x] 운영 -> 로컬 DB 동기화 스크립트 작성 완료.
- [ ] **API CORS 통합**: 컨트롤러별 분산된 `@CrossOrigin`을 제거하고 `WebMvcConfigurer` 한 곳에서 전역 관리.
- [ ] **공개 API DTO 도입**: JPA 엔티티 직접 반환 대신 응답용 DTO(Data Transfer Object) 도입.
- [ ] **전역 예외 처리**: `@ControllerAdvice` 적용하여 HTTP 상태 코드 친화적 에러 응답 구성.

---

## 🔮 넥스트 백로그 (v2.0 ~ v4.0 대기열)
*세부 태스크는 v1.5 완료 후 브레이크다운(Breakdown) 합니다.*
- [ ] **v2.0**: 소셜 로그인, 클라우드 냉장고 DB 저장, GA4 통계, 후원하기.
- [ ] **v3.0**: 백엔드 자동 크롤링 배치 스케줄러.
- [ ] **v4.0**: RAG 기반 AI 식단 플래너 & 쿠팡/컬리 장바구니 연동.