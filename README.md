# 🍳 요너두 (YoNeoDoo) : 내 손안의 AI 냉장고 파먹기 가이드

> "대 1인 가구 시대, 방치된 식재료로 시작하는 가장 쉬운 요리 입문"
> 
> **🔗 [요너두 라이브 서비스 보러가기](https://yoneodoo.vercel.app/)**

<br>

## 💡 기획 의도 및 프로젝트 목표 (Why YoNeoDoo?)

요리에 갓 입문한 1인 가구 및 소가구의 가장 큰 고민은 무엇일까요?
레시피 하나를 따라 하려다 무더기로 사버린 재료들, 매번 같은 요리만 해 먹다 질려서 결국 버려지는 식재료들입니다. **남은 재료를 처리하는 것 자체가 요리의 가장 큰 진입장벽**이 되어버리는 것이 현실입니다.

'요너두'는 이런 고민에서 출발했습니다. 내 냉장고에 남은 식재료를 입력하면, 지금 당장 만들어 먹을 수 있는 최적의 유튜브 요리 영상을 AI가 분석하여 추천해 드립니다. 

**🎯 본 프로젝트의 특별한 실험: "Vibe Coding (AI-Assisted Development)"**
이 프로젝트는 단순한 서비스 개발을 넘어, **생성형 AI(LLM)를 적극 활용한 '바이브 코딩'의 가능성과 한계를 직접 시험하고 적응해 나가는 풀스택 1인 개발 프로젝트**입니다. 기획부터 아키텍처 설계, AI 파이프라인 구축, 클라우드 배포까지 AI와의 협업을 통해 진행되었습니다.

<br>

## 🚀 서비스 로드맵 및 비즈니스 모델(BM)

**✅ 현재 버전 (v1 - Open Beta)**
- 🔍 **AI 기반 레시피 필터링**: 유튜브 자막을 LLM(Llama 3.1)으로 분석하여 정확한 식재료 및 요리 순서 추출
- 🧊 **임시 '내 냉장고' 기능**: 사용자가 보유한 재료를 기반으로 즉시 요리 가능한 레시피 매칭 및 추천

**🔄 업데이트 예정 (v2 - 유저 생태계 및 데이터 고도화)**
- 👤 **개인화 및 소셜 로그인**: 구글, 카카오 연동을 통한 사용자 계정 도입
- 🤝 **유저 참여형 QA 시스템 (데이터 검수)**: AI 데이터의 한계를 극복하기 위해, 레시피 오류 제보 및 수정 건의 게시판 운영 (기여도에 따른 리워드/포인트 지급)

**🔮 확장 예정 (v3 - 수익화 및 비즈니스 모델)**
- 💎 **프리미엄 멤버십**: 유저 참여 리워드 혹은 월 구독 모델을 통한 '나만의 냉장고' 데이터 영구 저장 및 맞춤형 AI 추천 기능 개방
- 🛒 **식재료 제휴(Affiliate) 연동**: 레시피 확인 후, 부족한 재료를 즉시 구매할 수 있는 쇼핑(쿠팡/컬리 등) 제휴 링크를 통한 수익 창출

<br>

## 🏗️ 시스템 아키텍처 및 레포지토리 (Microservices)

본 프로젝트는 프론트엔드, 백엔드 API, 그리고 AI 크롤링 파이프라인을 명확하게 분리한 MSA(Microservices Architecture) 형태로 구성되어 있습니다. 각 모듈의 상세 코드는 아래 링크에서 확인하실 수 있습니다.

### 1. 🌐 [Frontend (web)](https://github.com/madchan912/yoneodoo-web)
- **역할**: 사용자 대면 UI/UX 및 상태 관리
- **기술 스택**: React, Node.js
- **배포**: Vercel 연동 자동화 배포

### 2. ⚙️ [Backend API (api)](https://github.com/madchan912/yoneodoo-api)
- **역할**: 레시피 데이터 제공, 비즈니스 로직 처리, 클라우드 DB 연동
- **기술 스택**: Java 17, Spring Boot, Spring Data JPA
- **데이터베이스**: PostgreSQL (Neon Serverless DB) / 로컬-운영(Prod) 환경 완벽 분리
- **배포**: Render 클라우드 환경 배포 

### 3. 🤖 [AI Data Pipeline (data)](https://github.com/madchan912/yoneodoo-data)
- **역할**: 유튜브 크롤링, 자막 추출 및 LLM 기반 정형 데이터화, 운영 DB 적재
- **기술 스택**: Python, Llama 3.1 8B (Ollama), YouTube Transcript API

<br>

## 🛠️ Tech Stack 요약
- **Frontend**: React
- **Backend**: Spring Boot, Java 17, JPA(Hibernate)
- **Database**: PostgreSQL (Neon Cloud DB), Docker(Local DB)
- **AI / Data**: Python, Llama 3.1 (Ollama)
- **DevOps & Infra**: Docker, Vercel, Render, GitHub Actions

<br>

## 📫 Contact
- **Email**: [madchan912@gmail.com](mailto:madchan912@gmail.com)
- **GitHub**: [https://github.com/madchan912](https://github.com/madchan912)
