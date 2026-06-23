# YoNeoDoo — CLAUDE.md

Claude Code가 이 프로젝트에서 작동할 때 따르는 규칙입니다.
아키텍처나 규칙이 바뀌면 이 파일도 함께 수정하세요.

---

## 멀티레포 구조

이 워크스페이스는 세 개의 독립된 Git 레포와 메타 루트로 구성됩니다.

| 폴더 | 역할 | 주요 스택 |
|------|------|-----------|
| `yoneodoo-web` | 사용자 UI | React 19, Vite, axios |
| `yoneodoo-api` | REST API / 비즈니스 로직 | Java 21, Spring Boot 4.x, Spring Data JPA, PostgreSQL |
| `yoneodoo-data` | 크롤링·LLM → API 적재 파이프라인 | Python, Ollama/Llama3.1, Gemini API, youtube-transcript |
| 루트 (`02_Yoneodoo`) | 메타 문서 / 공통 설정 | — |

데이터 흐름: `yoneodoo-data` → (POST) → `yoneodoo-api` → (GET) → `yoneodoo-web`

---

## 1. 세션 시작 시 Git 동기화 (필수)

Claude Code 세션을 새로 열거나, 다른 머신으로 옮긴 직후에는
**작업 시작 전** 네 레포 모두에서 `git pull`(또는 `git pull --rebase`)을 실행할 것.

```bash
# 일괄 실행 예시
for dir in . yoneodoo-web yoneodoo-api yoneodoo-data; do
  (cd "$dir" && echo "=== $dir ===" && git pull --rebase)
done
```

---

## 2. 컨텍스트 유지

- 코드를 작성하거나 설계를 제안하기 전, 반드시 `CONTEXT.md` → `PLAN.md` → `TASK.md` 순서로 읽어
  현재 진행 상태·아키텍처를 파악할 것.
- 작업 완료 후 소스 코드나 계획에 변동이 생기면 위 세 파일을 최신화할 것.

---

## 3. Git 커밋 · 푸시 규칙

- **커밋은 사용자가 명시적으로 요청할 때만 수행할 것. 작업 완료 후 자동 커밋 금지.**
- 변경이 있는 각 레포마다 **독립적인 커밋**을 제안할 것.
- 커밋 메시지 형식: `[type]: [description]`
  - TASK.md를 함께 수정했다면 메시지 끝에 `& TASK.md 업데이트`를 붙일 것.
- 사용자가 바로 실행할 수 있도록 `cd → git add → git commit → git push`를 한 흐름으로 제공할 것.

```bash
# 출력 예시
cd yoneodoo-web
git add .
git commit -m "feat: API 베이스 URL 환경변수 처리 & TASK.md 업데이트"
git push
```

---

## 4. 기술 스택 가드레일

- **Web**: React 19 + Vite — 환경변수는 `VITE_` 접두사 사용
- **API**: Java 21 + Spring Boot 4.x + Spring Data JPA
- **DB**: PostgreSQL (로컬은 Docker, 운영은 AWS RDS)
- **Data / AI**: Python 크롤러 + 로컬 Ollama/Llama3.1 (레시피 추출·재료 정규화 메인), Google Gemini API gemini-2.5-flash (추후 자동화 배치용)

---

## 5. 백엔드 도메인 주석 규칙 (yoneodoo-api)

`yoneodoo-api`에서 아래 유형의 파일을 **새로 만들거나** public 메서드·필드의 의미가 바뀌면,
**같은 커밋 안에서** 한글 Javadoc/주석을 추가·수정할 것.

대상 파일 유형:
- **엔티티** (`entity/`) — 테이블·컬럼·JSONB 의미, 다른 테이블과의 관계
- **리포지토리** (`repository/`) — 어떤 조회/집계인지, 기획 관점에서의 용도
- **서비스** (`service/`, `admin/*Service.java`) — 입력 → DB/캐시 처리 → 출력 흐름
- **컨트롤러** (`controller/`, `admin/*Controller.java`, `crawling/*`) — HTTP와 서비스 사이 역할
- **DTO** (`dto/`, `admin/dto/`) — 요청/응답이 화면·파이프라인에서 의미하는 것
- **설정·보안** (`config/`) — 데이터 접근 관문이면 그 연결을 한 줄로

주석 작성 스타일 (초보 기획자도 따라갈 수 있게):
1. **클래스 Javadoc**: 이 클래스가 데이터 파이프라인에서 어디에 서는지(누가 호출하고, DB 어디를 다루는지).
2. **public 메서드**: 처리 단계를 순서대로(①②③). 왜 그렇게 하는지 한두 문장.
3. **중요 필드·상수**: 비즈니스 의미, 다른 모듈과 맞춰야 할 규칙(예: 재료명 정규화와 매핑 테이블 키 일치).

하지 말 것:
- 동작 변경 없이 주석만 덧붙이는 대규모 리팩터
- 프론트엔드 파일 주석 — 별도 요청이 있을 때만

---

## 7. 작업 완료 검증 기준 (필수)

작업 완료 보고 전 직접 실행해서 통과 확인할 것.
- yoneodoo-api: `./gradlew compileJava` 통과 확인
- yoneodoo-web: `npm run build` 빌드 에러 없음 확인

실패하면 원인 분석 후 수정 → 재실행. 에러를 그대로 사람에게 넘기지 말 것.
검증 통과 후 TASK.md 최신화하고 커밋에 포함할 것.

---

## 6. [중요] 보안 및 로컬 환경변수

아래 파일들은 **절대로** `git add` 또는 커밋에 포함하지 말 것:

- `.env`, `.env.local`, `.env.*`
- `application-local.yaml`
- `scripts/.env.sync`

해당 파일을 생성·수정했을 경우, 반드시 사용자에게 아래 내용을 안내할 것:

> "이 파일은 Git에 추적되지 않으므로 다른 환경(맥북, 데스크톱 등)에서 수동으로 복사·동기화해야 합니다."
