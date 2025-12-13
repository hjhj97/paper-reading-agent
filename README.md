# 📄 Paper Reading Agent

AI 기반 학술 논문 자동 요약 및 Q&A 시스템

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)](https://openai.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

</div>

---

## 🎯 개요

Paper Reading Agent는 **GPT-4o-mini**와 **RAG(Retrieval-Augmented Generation)** 기술을 활용하여 학술 논문을 자동으로 분석하고 요약하는 웹 애플리케이션입니다.

**주요 기능:**

- 📤 PDF 업로드 → 자동 텍스트 추출 및 메타데이터 파싱
- 📝 구조화된 논문 요약 (연구 목적, 방법론, 결과, 결론)
- 💬 RAG 기반 실시간 Q&A (스트리밍 응답)
- 📊 논문 스토리라인 분석 (문제 제기 → 방법론 → 결과)
- 🖼️ 네이티브 PDF 뷰어 (LaTeX 수식 렌더링)
- 🌍 다국어 지원 (한국어/영어)

---

## 🔄 시스템 플로우

![System Flow Chart](./docs/flow-chart.png)

_PDF 업로드부터 AI 요약 및 Q&A까지의 전체 워크플로우_

---

## 🚀 빠른 시작

### Prerequisites

- Docker & Docker Compose
- OpenAI API Key
- Pinecone API Key (벡터 DB, dimension=1536)

### 1. 환경 설정

```bash
# 저장소 클론
git clone <your-repo-url>
cd paper-reading-agent

# 환경 변수 설정
cp .env.example .env
nano .env  # API 키 입력
```

**.env 예시:**

```bash
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=paper-reading-agent
```

### 2. 실행

```bash
# Docker Compose로 실행
docker compose up -d --build

# 로그 확인
docker compose logs -f
```

### 3. 접속

- **프론트엔드**: http://localhost:3000
- **백엔드 API 문서**: http://localhost:8000/docs

---

## 🛠️ 기술 스택

| 분류         | 기술                                   |
| ------------ | -------------------------------------- |
| **Backend**  | FastAPI, Python 3.12, Uvicorn          |
| **LLM**      | OpenAI GPT-4o-mini, Langfuse (로깅)    |
| **RAG**      | LangChain, Pinecone, OpenAI Embeddings |
| **Frontend** | Next.js 14, TypeScript, React          |
| **UI**       | Tailwind CSS, shadcn/ui, KaTeX         |
| **PDF**      | PyPDF2, react-pdf-viewer               |
| **Deploy**   | Docker, Nginx, AWS                     |

---

## 📡 API 엔드포인트

| Method | Endpoint                | 설명                      |
| ------ | ----------------------- | ------------------------- |
| `POST` | `/api/upload`           | PDF 업로드 및 임베딩 생성 |
| `POST` | `/api/summarize`        | 논문 요약 생성            |
| `POST` | `/api/storyline`        | 스토리라인 분석           |
| `POST` | `/api/ask/stream`       | RAG 기반 Q&A (스트리밍)   |
| `POST` | `/api/rate`             | 요약 품질 평가            |
| `GET`  | `/api/models`           | 사용 가능한 LLM 모델 목록 |
| `GET`  | `/api/sessions`         | 세션 히스토리 조회        |
| `GET`  | `/api/session/{id}`     | 특정 세션 상세 정보       |
| `GET`  | `/api/session/{id}/pdf` | PDF 파일 조회             |

**Swagger UI**: http://localhost:8000/docs

---

## 💡 사용 방법

### 1. 논문 업로드

- 메인 페이지에서 **모델**(GPT-4o-mini) 및 **언어**(한국어/영어) 선택
- PDF 파일을 드래그앤드롭 또는 클릭하여 업로드

### 2. 자동 처리

- 텍스트 추출 및 메타데이터(제목, 저자, 연도) 파싱
- 벡터 임베딩 생성 및 Pinecone 저장
- 자동으로 요약 페이지로 이동

### 3. 결과 확인

- **PDF 뷰어**: 원본 논문 보기
- **스토리라인**: 약 600자 핵심 요약
- **상세 요약**: 구조화된 상세 요약 (400-600단어)
- **Q&A**: 논문에 대한 질문-답변 (실시간 스트리밍)

---

## 📁 프로젝트 구조

```
paper-reading-agent/
├── backend/           # FastAPI 백엔드
│   ├── app/
│   │   ├── api/       # API 라우터
│   │   ├── services/  # 비즈니스 로직
│   │   ├── models/    # Pydantic 스키마
│   │   └── main.py
│   └── requirements.txt
├── frontend/          # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/       # 페이지
│   │   ├── components/# UI 컴포넌트
│   │   └── lib/       # API 클라이언트
│   └── package.json
├── docs/              # 문서 및 이미지
├── docker-compose.yml # Docker 오케스트레이션
└── nginx.conf         # 리버스 프록시 설정
```

---

## 🔧 로컬 개발

### 백엔드

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 프론트엔드

```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

---

## 📚 상세 문서

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - AWS 배포 가이드 (EC2, ECS, Lightsail)
- **[QUICKSTART.md](./QUICKSTART.md)** - 로컬 개발 상세 가이드
- **[REPORT.md](./REPORT.md)** - 프로젝트 상세 보고서
- **[LANGFUSE_SCORES_GUIDE.md](./LANGFUSE_SCORES_GUIDE.md)** - Langfuse 통합 가이드

---

## 🎯 주요 특징

### RAG (Retrieval-Augmented Generation)

- **하이브리드 검색**: 시맨틱 검색 + 메타데이터 부스팅
- **Context-aware**: 제목/저자 질문 시 논문 첫 페이지 우선 검색
- **실시간 스트리밍**: Server-Sent Events로 답변 생성 과정 표시

### 프롬프트 엔지니어링

- 학술 논문에 최적화된 시스템 프롬프트
- 구조화된 출력 (Overview, Methodology, Findings, Conclusions)
- LaTeX 수식 자동 변환 (`$$...$$` 형식)

### 관찰성 (Observability)

- **Langfuse 통합**: 모든 LLM 호출 자동 로깅
- **비용 추적**: 토큰 사용량 및 예상 비용 계산
- **사용자 피드백**: 요약 평가 데이터 수집

---

## ⚠️ 한계점

- **데이터 영속성**: 메모리 기반 세션 (재시작 시 데이터 손실)
- **인증**: 사용자 인증 시스템 없음
- **확장성**: 단일 인스턴스 배포 (수평 확장 제한)
- **PDF 처리**: 복잡한 레이아웃 및 수식 오인식 가능

> 💡 **프로덕션 배포 시**: PostgreSQL/MongoDB, Redis, S3, 인증 시스템 추가 필요

---

## 향후 계획

- [ ] 세션 기반 -> 데이터베이스 통합
- [ ] 사용자 인증 (소셜로그인)
- [ ] 연/추천관 논문 검색
- [ ] 인용 논문 하이퍼링크
- [ ] 다른사람과 요약된 논문 공유
- [ ] 관리자 페이지에서 실시간로그 모니터링
