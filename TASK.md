# 요너두 — 할 일 목록 (지금 당장)

`CONTEXT.md`, `PLAN.md`에서 뽑은 **실행 가능한 체크리스트**입니다. 완료 시 체크하고, 필요하면 날짜·담당을 적으세요.

## 기반 작업 (v1.5 기능과 병행·선행)

- [ ] **웹: API 베이스 URL을 env로** — `yoneodoo-web/src/App.jsx`의 Render 하드코딩을 `import.meta.env.VITE_API_BASE_URL`(또는 팀 합의 이름)으로 교체; `yoneodoo-web/README.md`에 문서화.
- [ ] **데이터: API 베이스 URL을 env로** — `yoneodoo-data/main.py`가 `.env`의 `API_BASE_URL`을 우선 사용하도록 정리; 운영 URL 하드코딩 제거 또는 기본값 가드.
- [ ] **웹 README 정합** — 스크립트: `npm run dev` / `npm run build`; Vite용 `VITE_*`; 구식 `REACT_APP_*`·`npm start` 언급 수정·삭제.
- [ ] **API: CORS** — `WebMvcConfigurer` + 프로퍼티 등 **한곳**에서 dev/prod 허용 오리진 관리; 동등 동작 확인 후 컨트롤러별 `@CrossOrigin` 제거.
- [ ] **API: 재료 캐시 갱신** — `RecipeService.saveRecipe` 이후 `IngredientSearchService` 재구축(또는 공통 `rebuildCache`)을 호출해, 재시작 없이 신규 레시피가 검색에 반영되게.

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

- [ ] **DTO 레이어** — 공개 GET은 JPA 엔티티가 아닌 DTO 반환.
- [ ] **전역 예외 처리** — `RuntimeException` 직투 대신 HTTP 친화적 에러.
- [ ] **Bean Validation** — `RecipeCreateRequest`, `FridgeAddRequest` 등.
- [ ] **레시피 쓰기 보호** — 크롤러→API 인증 또는 공유 시크릿.
- [ ] **`crawling` 패키지 감사** — `CrawlingData` / `CrawlingController` 유지 여부.

---

*v1.5 범위를 줄이면 순서를 바꿔도 됨. 맥북·데스크톱·배포 혼선을 줄이려면「기반 작업」을 앞에 두는 것을 권장.*
