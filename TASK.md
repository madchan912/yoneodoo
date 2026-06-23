# 요너두(YoNeoDoo) — 할 일 목록 (Action Items)

`CONTEXT.md`, `PLAN.md`에서 뽑은 **실행 가능한 체크리스트**입니다.
가장 위에 있는 항목이 '지금 당장' 해야 할 최우선 과제입니다.

---

## 🚨 최우선 과제: 재료 정규화 마무리 (v1.5)

- [ ] **재료 정규화 완료 (약 87개 잔여)**:
  - `ingredient_mapping` 미매핑 raw_name 영상 확인 후 마스터명 확정.
  - 어드민 AI 그룹핑(`/bulk-grouping`) + 수동 확인 병행.
- [x] **PENDING 로직 구현**:
  - `RecipeService.checkAndUpdateRecipeStatus(Recipe)` 공통 메서드 추출.
  - Trigger A: 크롤러 적재 (`RecipeService.saveRecipe`) 후 자동 평가.
  - Trigger B: 어드민 레시피 수정 (`AdminService.updateRecipe`) 후 자동 평가.
  - Trigger C: 재료 매핑 저장 (`saveIngredientMappings` / `bulkSaveIngredientMappings`) 후 관련 레시피 재평가.
  - 종료 상태(NO_SUBTITLES·FAILED·SKIP)는 덮어쓰지 않음.
  - 미리보기 모달 각 레시피 카드에 [✏️ 수정] 버튼 추가 — RecipeEditModal을 zIndex=11000으로 열고, 저장 후 미리보기 목록 자동 재조회.
- [ ] **데스크탑 `.env.sync` RDS 정보로 업데이트**:
  - `SYNC_SOURCE_HOST=yoneodoo-db.cvgskwe4mv95.ap-northeast-2.rds.amazonaws.com` 반영.
  - (맥북은 이미 완료, 데스크탑만 잔여)

---

## ✅ 완료된 작업 (v1.5)

### 인프라 & CI/CD
- [x] **AWS 인프라 구축 (2026-06-17)**: EC2(t3.micro, Ubuntu) + RDS PostgreSQL(`yoneodoo-db`, ap-northeast-2) 전환.
- [x] **GitHub Actions CI/CD (2026-06-22)**: main 브랜치 push → API Docker rebuild + Web Nginx 자동 배포.
- [x] **구 인프라 삭제 완료 (2026-06-22)**: Render(백엔드), Neon(DB), Vercel(프론트) 전부 삭제.
- [x] **로컬 DB 동기화 스크립트**: `scripts/sync_prod_to_local_db.py` + `.env.sync` (RDS 정보 반영).

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

### 사용자 검색
- [x] **요리명 검색 API**: `GET /api/v1/recipes/search?q=` (JPQL ILIKE, status/displayStatus 필터 적용).
- [x] **재료/요리명 토글 UI**: `searchMode` 상태, 300ms 디바운스, 빈 쿼리 시 전체 목록 표시.
- [x] **재료 마스터명 변환**: `IngredientSearchService` 캐시 원천을 `ingredient_mapping.master_name` 기준으로 변경 + 레시피 응답 재료명 master_name 치환.

### 기술 부채 & 기타
- [x] **CORS 전역 통합**: `CorsConfig.java` 신규, 4개 컨트롤러 `@CrossOrigin` 제거. 허용 오리진: localhost:5173, 43.201.95.155.
- [x] **RecipeResponse DTO 도입**: `status`/`displayStatus`/`transcript` 미노출, 재료명 master_name 변환 통합.
- [x] **전역 예외처리**: `GlobalExceptionHandler.java` — `ResponseStatusException` / `IllegalArgumentException` / `RuntimeException` / catch-all 처리.
- [x] **카피라이트 추가**: `© 2026 요너두. All rights reserved.` (App.jsx footer).
- [x] **CLAUDE.md 에이전틱 검증 기준 추가**: `./gradlew compileJava` + `npm run build` 완료 후 보고 규칙.
- [x] **웹/API 베이스 URL 환경변수 통일**: `VITE_API_BASE_URL`.

---

## 🏗️ v1.9 대기열

- [ ] **커스텀 도메인 구매**: `yoneodoo.kr` 또는 `yoneodoo.com`.
- [ ] **HTTPS 인증서**: Let's Encrypt / Certbot (도메인 연결 후 진행).
- [ ] **초기 데이터 벌크 적재**: 로컬 파이썬 크롤러로 레시피 2,000~3,000개 수집 → 운영 DB.

---

## 🔮 넥스트 백로그 (v2.0 ~ v4.0)
*세부 태스크는 v1.5 완료 후 브레이크다운합니다.*
- [ ] **v2.0**: 소셜 로그인, 클라우드 냉장고 DB 저장, GA4 통계, 후원하기.
- [ ] **v3.0**: 백엔드 자동 크롤링 배치 스케줄러 + Gemini 파이프라인 완전 이식.
- [ ] **v4.0**: RAG 기반 AI 식단 플래너 & 쿠팡/컬리 장바구니 연동.
