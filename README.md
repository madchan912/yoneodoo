# 🍳 요너두 (YoNeoDoo) : 내 재료로 AI 냉장고 파먹기 가이드

> "1인 가구 시대, 방치된 식재료로 요리하는 가장 쉬운 요리 입문"
>
> **🔗 [요너두 라이브 서비스 보러가기](https://yoneodoo.com)**

<br>

## 💡 기획 의도 (Why YoNeoDoo?)

요리에 갓 입문한 1인 가구의 가장 큰 고민은 무엇일까요?
한 레시피 하나를 따라 하려다 무너기로 사버린 재료들, 매번 같은 요리만 해 먹다 지려서 결국 버려지는 식재료들이었습니다.
**남은 재료를 처리하는 것 자체가 요리의 가장 큰 진입장벽**이 되어버리는 것이 현실이었습니다.

'요너두'는 이런 고민에서 출발하였습니다.
냉장고의 남은 재료를 입력하면, 지금 바로 만들어 먹을 수 있는 유튜브 요리 영상을 추천하고, AI가 개인 맞춤 식단까지 짜드립니다.

<br>

## 📅 서비스 로드맵

**✅ v1.5 (완료)**
- 🤖 **AI 데이터 파이프라인**: 유튜브 자막 → Llama 3.1(로컬 LLM)으로 재료 자동 추출 → DB 적재
  - 초기 API 비용 절감을 위해 로컬 LLM(Ollama)으로 시작, 메타 프롬프팅으로 JSON 출력 안정화
  - 이후 Gemini Flash의 비용 효율성 확인 후 안정성·품질 향상을 위해 전환
- 🔍 **재료/요리명 검색**: 냉장고 재료 기반 레시피 매칭 + 요리명 직접 검색 토글
- 🤝 **AI 재료 정규화 시스템 (Human-in-the-Loop)**: Gemini API로 미분류 재료 자동 그룹핑·추천 → 어드민 검토 후 승인
- ⚙️ **어드민 시스템**: 레시피 CRUD, 재료 정규화 UI, 상태 자동 전환 로직
- 🏗️ **인프라**: AWS EC2 + RDS PostgreSQL + GitHub Actions CI/CD

**✅ v1.9 (완료)**
- 🌐 **커스텀 도메인 + HTTPS**: yoneodoo.com 연결 및 Let's Encrypt 인증서 적용

**✅ v2.0 (완료)**
- 🚀 **FastAPI 데이터 서버**: 로컬 크롤링 파이프라인을 EC2 위에 FastAPI 서버로 이전
- 📦 **다중 소스 수집**: 유튜브 자막 + 더보기(description) + 첫번째 댓글 병행 추출
- ⏰ **자동 배치 크롤링**: 매일 03:00 active 유튜버 순차 크롤링 + Discord 알림
- 📊 **영양성분 파이프라인**: 식품성분표 DB 기반 재료 영양성분 구축 + 레시피 칼로리 자동 계산
- 🧠 **RAG 식단 플래너**: pgvector + Gemini Embedding 기반 의미론적 검색 + AI 식단 조합
- 👨‍💼 **어드민 고도화**: 유튜버 관리, 크롤링 이력, 영양성분 관리 UI

**🔮 v3.0 (예정)**
- **소셜 로그인**: 구글/카카오 연동
- **클라우드 냉장고**: 기기간 동기화 (localStorage → DB 저장)
- **GA4 통계**: DAU, 레시피 클릭/재생 트래킹
- **유료화**: 식단 플래너 주 N회 제한 + 구독 모델

**🔮 v4.0 (예정)**
- **RAG 고도화**: 1주일 식단 플래닝, 장바구니 차분 계산
- **커머스 어필리에이트**: 쿠팡/마켓컬리 장바구니 링크 연결

<br>

## 🏗️ 시스템 아키텍처

프론트엔드, 백엔드 API, AI 크롤링 파이프라인을 분리한 멀티레포 구조입니다.

```
유튜브 채널 
    ↓
[yoneodoo-data] FastAPI (EC2 port 8000)
크롤링 → 자막/더보기/댓글 수집 → Gemini로 재료 추출
→ 영양성분 자동 계산 → 임베딩 생성
    ↓ POST /api/v1/recipes
[yoneodoo-api] Spring Boot (EC2 port 8080)
레시피 저장 → 정규화 체크 → 상태 자동 전환
pgvector 유사도 검색 → Gemini 식단 조합
    ↓ GET /api/v1/recipes
[yoneodoo-web] React + Nginx (EC2 port 80/443)
재료/요리명 검색 UI → 레시피 카드 → AI 식단 플래너
```

### 주요 설계 결정 (Why?)

**왜 로컬 LLM(Llama 3.1)에서 Gemini API로 전환했나요?**
초기에는 API 호출 비용 부담으로 Ollama 기반 로컬 LLM을 선택했습니다.
운영하면서 출력 포맷 불안정과 환각 현상을 메타 프롬프팅으로 제어했지만,
Gemini Flash의 토큰 비용이 충분히 낮아진 시점에 안정성과 품질을 위해 전환했습니다.
두 환경을 모두 운영해보며 로컬 LLM의 한계와 클라우드 API의 장단점을 실무적으로 체감했습니다.

**왜 FastAPI와 Spring Boot를 분리하나요?**
데이터 수집·가공(크롤링, LLM 호출, 영양성분 계산)은 Python 생태계가 압도적으로 유리합니다. Spring Boot는 안정적인 REST API 서빙과 JPA 기반 비즈니스 로직에 집중하고, FastAPI는 데이터 파이프라인과 AI 연동에 집중하는 역할 분리 구조를 선택하였습니다.

**왜 pgvector를 선택하나요?**
이미 운영 중인 AWS RDS PostgreSQL에 확장 플러그인(`CREATE EXTENSION vector`)으로 벡터 검색을 추가할 수 있습니다. 별도 벡터 DB(Pinecone, Weaviate 등)를 도입하면 인프라 복잡도와 비용이 증가하는 반면, pgvector는 기존 SQL 쿼리와 벡터 검색을 JOIN으로 조합할 수 있어 칼로리 필터 + 의미론적 검색을 단일 쿼리로 처리할 수 있습니다.

**왜 Gemini Embedding(768차원)을 선택하나요?**
한국어 레시피 도메인에서 더 높은 차원(1536차원)이 반드시 더 높은 성능을 보장하지 않습니다. 768차원은 한국어 의미 표현에 충분하면서 인덱스 크기와 검색 속도 면에서 효율적입니다.

**왜 Human-in-the-Loop 정규화를 선택하나요?**
"닭가슴살"과 "닭 가슴살 한 조각"이 같은 재료임을 AI가 자동 판단하더라도, 최종 데이터 품질은 사람이 검토해야 신뢰할 수 있습니다. Gemini가 그룹핑을 추천하고 어드민이 승인하는 구조로 자동화의 효율성과 신뢰도를 동시에 확보하였습니다.

<br>

## 🛠️ Tech Stack

| 영역 | 기술 |
|------|------|
| Frontend | React 19, Vite 8, Axios |
| Backend API | Spring Boot 4.x, Java 21, Spring Data JPA |
| Database | AWS RDS PostgreSQL + pgvector (벡터 검색) |
| AI / Pipeline | Python, FastAPI, Gemini 2.5 Flash, Gemini text-embedding-004 |
| 영양성분 | 식품의약품안전처 식품영양성분 DB + Gemini 추정 |
| DevOps | AWS EC2, Docker, Nginx, Let's Encrypt, GitHub Actions CI/CD |

<br>

## 📊 데이터 파이프라인 상세

```
① 크롤링
   scrapetube → 유튜브 채널 쇼츠 목록 수집
   youtube-transcript → 자막 추출
   yt-dlp → 더보기(description) + 첫번째 댓글 수집

② AI 재료 추출 (Gemini 2.5 Flash)
   자막 + 더보기 + 댓글 → 재료명/양 JSON 추출
   양이 없는 재료 → INCOMPLETE 상태로 저장

③ 재료 정규화
   ingredient_mapping 테이블로 raw_name → master_name 변환
   미매핑 재료 → Gemini AI 그룹핑 추천 → 어드민 승인

④ 영양성분 자동 계산
   ingredient_nutrition 조회 → 없는 재료는 Gemini 추정
   단위 변환 (큰술=15g, 컵=200g 등) → recipe_nutrition 저장

⑤ 임베딩 생성
   레시피명 + 재료 목록 → Gemini text-embedding-004 (768차원)
   → recipe_embeddings (pgvector) 저장
```

<br>

## 🤖 RAG 식단 플래너

자연어 입력으로 AI 맞춤 식단을 제공하는 핵심 기능입니다.

```
사용자: "닭가슴살 지겨워요, 다이어트 식단 일주일 짜줘"
    ↓
① Gemini → 조건 추출
   { exclude: ["닭가슴살"], goal: "diet", days: 7 }
    ↓
② Gemini Embedding → 사용자 입력 벡터화
    ↓
③ pgvector 코사인 유사도 검색
   칼로리 필터 + 재료 제외 + 의미적 유사도 상위 20개
    ↓
④ Gemini → 20개 레시피로 7일 식단 조합
    ↓
"아침: 두부 스테이크 (280kcal)
 점심: 야채 샐러드 (210kcal) ..."
```

> 현재 beta 기능으로 운영 중 (`?beta=true` 파라미터로 접근)

<br>

## ⚙️ 어드민 시스템

| 기능 | 설명 |
|------|------|
| 레시피 관리 | CRUD, 상태 관리, Soft Delete, 정렬/필터 |
| 재료 정규화 | 미분류 재료 목록, Gemini AI 그룹핑 추천, 일괄 승인 |
| 영양성분 관리 | 식품성분표 DB 검색 매핑, Gemini 추정, 확인필요 목록 |
| 유튜버 관리 | 채널 등록/삭제/활성화, 크롤링 트리거, 이력 조회 |
| 크롤링 이력 | job_id 기반 실시간 진행 상황, 결과 요약 |

<br>

## 📫 Contact
- **Email**: [madchan912@gmail.com](mailto:madchan912@gmail.com)
- **GitHub**: [https://github.com/madchan912](https://github.com/madchan912)
