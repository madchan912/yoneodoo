# 🍳 요너두 (YoNeoDoo) : 내 손안의 AI 냉장고 파먹기 가이드

> "대 1인 가구 시대, 방치된 식재료로 시작하는 가장 쉬운 요리 입문"
>
> **🔗 [요너두 라이브 서비스 보러가기](https://yoneodoo.com)**

<br>

## 💡 기획 의도 (Why YoNeoDoo?)

요리에 갓 입문한 1인 가구의 가장 큰 고민은 무엇일까요?  
레시피 하나를 따라 하려다 무더기로 사버린 재료들, 매번 같은 요리만 해 먹다 질려서 결국 버려지는 식재료들입니다.  
**남은 재료를 처리하는 것 자체가 요리의 가장 큰 진입장벽**이 되어버리는 것이 현실입니다.

'요너두'는 이런 고민에서 출발했습니다.  
냉장고에 남은 재료를 입력하면, 지금 당장 만들어 먹을 수 있는 유튜브 요리 영상을 추천해 드립니다.

<br>

## 🚀 서비스 로드맵

**✅ v1.5 (완료)**
- 🔍 **AI 데이터 파이프라인**: 유튜브 자막 → 로컬 LLM(Llama 3.1)으로 재료 자동 추출 → DB 적재
- 🧊 **재료/요리명 검색**: 냉장고 재료 기반 레시피 매칭 + 요리명 직접 검색 토글
- 🤖 **AI 재료 정규화 시스템 (Human-in-the-Loop)**: Gemini API로 미분류 재료 자동 그룹핑·추천 → 어드민 검토 후 승인
- ⚙️ **어드민 시스템**: 레시피 CRUD, 재료 정규화 UI, PENDING 로직 (미정규화 레시피 자동 비노출 → 정규화 완료 시 자동 노출)
- 🏗️ **인프라**: AWS EC2 + RDS PostgreSQL + GitHub Actions CI/CD

**✅ v1.9 (완료)**
- 🌐 **커스텀 도메인 + HTTPS**: yoneodoo.com 연결 및 Let's Encrypt 인증서 적용 (2026-07-07)
- 🖥️ **UI 개선**: 브라우저 탭 타이틀, og 메타태그, 수동 배포 트리거 추가

**🔄 v2.0 (예정)**
- 📦 **데이터 벌크 적재**: 레시피 2,000~3,000개 수준으로 확장
- 🐍 **yoneodoo-ai FastAPI 서버 신설**: 로컬 크롤링 파이프라인을 서버 API로 이식, RAG 기초 (임베딩·유사도 검색)

**👤 v3.0 (예정)**
- **소셜 로그인**: 구글/카카오 연동
- **클라우드 냉장고**: 기기간 동기화 (localStorage → DB 저장)
- **GA4 통계**: DAU, 레시피 클릭/재생 트래킹
- **후원하기**: 커피 한 잔 후원 창구

**👑 v4.0 (예정)**
- **배치 스케줄러**: 매일 새벽 지정 유튜버 신규 영상 자동 수집·적재 (yoneodoo-ai Cron)
- **RAG 고도화**: LangChain + 자체 DB 기반 1주일 식단 자동 큐레이션, 장바구니 차분 계산
- **커머스 어필리에이트**: 쿠팡/마켓컬리 장바구니 링크 연결 → 구매 수수료 수익 모델

<br>

## 🏗️ 시스템 아키텍처

프론트엔드, 백엔드 API, AI 크롤링 파이프라인을 분리한 멀티레포 구조입니다.

```
유튜브 → [yoneodoo-data] 크롤링/자막/LLM → POST → [yoneodoo-api] → GET → [yoneodoo-web]
                ↕ (v2.0 예정)
         [yoneodoo-ai] FastAPI 서버 (파이프라인 서버화, RAG)
```

### 1. 🌐 [Frontend (yoneodoo-web)](https://github.com/madchan912/yoneodoo-web)
- **역할**: 사용자 UI/UX, 어드민 관리 페이지
- **기술 스택**: React 19, Vite, axios
- **배포**: AWS EC2 + Nginx + GitHub Actions CI/CD

### 2. ⚙️ [Backend API (yoneodoo-api)](https://github.com/madchan912/yoneodoo-api)
- **역할**: 레시피/재료 검색 API, 정규화 비즈니스 로직, 어드민 API
- **기술 스택**: Java 21, Spring Boot 4.x, Spring Data JPA
- **데이터베이스**: AWS RDS PostgreSQL (JSONB 재료 저장)
- **배포**: AWS EC2 Docker + GitHub Actions CI/CD

### 3. 🤖 [AI Data Pipeline (yoneodoo-data)](https://github.com/madchan912/yoneodoo-data)
- **역할**: 유튜브 크롤링, 자막 추출, LLM 재료 추출, 운영 DB 적재
- **기술 스택**: Python, Llama 3.1 8B (Ollama), Gemini API, youtube-transcript, scrapetube

### 4. 🐍 yoneodoo-ai (v2.0 예정)
- **역할**: 크롤링·LLM 파이프라인 서버 API화, RAG 기반 레시피 임베딩·유사도 검색
- **기술 스택**: Python, FastAPI, Gemini API, LangChain (예정)

<br>

## 🛠️ Tech Stack

| 영역 | 기술 |
|------|------|
| Frontend | React 19, Vite 8 |
| Backend | Spring Boot 4.x, Java 21, Spring Data JPA |
| Database | AWS RDS PostgreSQL |
| AI / Data | Python, Llama 3.1 (Ollama), Gemini API (gemini-2.5-flash), FastAPI (v2.0 예정) |
| DevOps & Infra | AWS EC2, Docker, Nginx, GitHub Actions CI/CD |

<br>

## 📫 Contact
- **Email**: [madchan912@gmail.com](mailto:madchan912@gmail.com)
- **GitHub**: [https://github.com/madchan912](https://github.com/madchan912)
