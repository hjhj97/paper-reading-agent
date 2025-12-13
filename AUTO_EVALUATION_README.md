# 🤖 자동 품질 평가 시스템

논문 요약 시 **자동으로 품질을 평가**하고 **Langfuse에 로그**를 남기는 시스템입니다.

## ⚡ 핵심 기능

### 완전 자동화된 평가

```
사용자: PDF 업로드 + 요약 요청
   ↓
백엔드: 요약 생성 + 자동 평가 + Langfuse 로깅 (모두 자동!)
   ↓
Langfuse: 요약과 평가 이력을 session_id로 추적
```

**사용자는 아무것도 안 해도 모든 요약의 품질이 자동으로 기록됩니다!**

## 📊 평가 기준 (5가지 차원, 각 1-10점)

| 기준 | 설명 |
|------|------|
| **Faithfulness** (충실성) | 원문과의 정확한 일치도 |
| **Completeness** (완전성) | 핵심 내용 포함 여부 |
| **Conciseness** (간결성) | 불필요한 내용 없이 간결한지 |
| **Coherence** (일관성) | 논리적 흐름과 구조 |
| **Clarity** (명료성) | 이해하기 쉬운지 |

## 🚀 사용 방법

### 1. 백엔드 시작

```bash
cd backend
uvicorn app.main:app --reload
```

### 2. 요약 요청 (자동 평가 포함!)

```bash
# PDF 업로드
curl -X POST http://localhost:8000/api/upload \
  -F "file=@your_paper.pdf"
# Response: {"session_id": "abc123", ...}

# 요약 생성 (자동으로 평가도 실행됨!)
curl -X POST http://localhost:8000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123"}'
```

### 3. 백엔드 로그 확인

```
✅ Summary evaluated - Overall Score: 8.6/10
   Scores: F=9, C=8, Co=9, Ch=8, Cl=9
```

### 4. Langfuse 대시보드에서 확인

https://cloud.langfuse.com 에서:

- **Traces** → 요약 생성 trace 확인
- **Traces** → 평가 trace 확인 (`evaluate_summary_{session_id}`)
- **Scores** → 평가 점수 확인 (6개 점수: overall_quality + 5개 차원)
- 두 trace 모두 동일한 session_id로 연결됨

## 📁 파일 구조

```
backend/
├── app/
│   ├── services/
│   │   └── llm_service.py           # evaluate_summary() 메서드
│   ├── api/
│   │   └── routes.py                # /summarize에 자동 평가 추가
│   └── models/
│       └── schemas.py               # EvaluateRequest/Response
├── test_evaluation.py               # 기본 평가 테스트
├── test_auto_evaluation.py          # 자동 평가 통합 테스트
├── test_api_auto_evaluation.sh      # API 테스트 스크립트
├── EVALUATION_GUIDE.md              # 상세 가이드
└── AUTO_EVALUATION_README.md        # 이 파일
```

## 🧪 테스트

### Python 통합 테스트

```bash
cd backend
python test_auto_evaluation.py
```

**출력 예시:**
```
📝 Step 1: Generating summary...
✅ Summary generated successfully!

🔍 Step 2: Automatically evaluating summary...
✅ Evaluation completed!

Evaluation Results:
  Overall Score: 8.8/10

  Detailed Scores:
    - Faithfulness:  9/10
    - Completeness:  9/10
    - Conciseness:   8/10
    - Coherence:     9/10
    - Clarity:       9/10

📊 Check Langfuse Dashboard:
   You should see TWO traces for this test:
   1. Summary generation
   2. Summary evaluation
```

### API 테스트

```bash
cd backend
./test_api_auto_evaluation.sh
```

## 🔍 Langfuse에서 확인하는 방법

### 1. Traces 보기

https://cloud.langfuse.com → **Traces** 메뉴

- **Name**: `evaluate_summary_` 로 검색
- **Metadata**: `evaluation_type: summary_quality`
- **Session ID**: 특정 세션으로 필터

각 평가 trace에서:

```json
{
  "name": "evaluate_summary_abc123",
  "metadata": {
    "session_id": "abc123",
    "evaluation_type": "summary_quality",
    "model_used": "gpt-5-mini"
  },
  "input": {
    "original_text": "...",
    "summary": "..."
  },
  "output": {
    "faithfulness": 9,
    "completeness": 8,
    "conciseness": 9,
    "coherence": 8,
    "clarity": 9,
    "overall_score": 8.6,
    "reasoning": "...",
    "strengths": [...],
    "weaknesses": [...]
  }
}
```

### 2. Scores 탭에서 점수 확인 ⭐

https://cloud.langfuse.com → **Scores** 메뉴

각 요약마다 **6개의 점수**가 자동으로 기록됩니다:

| Score Name | 설명 | 범위 |
|------------|------|------|
| `overall_quality` | 전체 품질 점수 | 0-1 (8.6/10 = 0.86) |
| `faithfulness` | 충실성 | 0-1 (9/10 = 0.9) |
| `completeness` | 완전성 | 0-1 (8/10 = 0.8) |
| `conciseness` | 간결성 | 0-1 (9/10 = 0.9) |
| `coherence` | 일관성 | 0-1 (8/10 = 0.8) |
| `clarity` | 명료성 | 0-1 (9/10 = 0.9) |

**점수 활용:**
- 시간별 품질 추이 분석
- 모델별 성능 비교
- 프롬프트 최적화
- 품질 임계값 설정

### 3. Scores 필터링

- **Trace ID**: 특정 요약의 점수만 보기
- **Score Name**: `overall_quality`, `faithfulness` 등으로 필터
- **Time Range**: 특정 기간의 점수 추이 확인

## 📈 활용 예시

### 1. 요약 품질 모니터링

Langfuse에서 시간 경과에 따른 평균 점수 추이 확인:
- 어떤 논문 타입이 높은 점수를 받는가?
- 어떤 모델이 더 나은 요약을 생성하는가?

### 2. A/B 테스트

다른 프롬프트나 모델 비교:

```python
# 방식 A
summary_a = await llm_service.summarize_paper(
    paper_text=text,
    custom_prompt="Summarize in 300 words"
)

# 방식 B (기본)
summary_b = await llm_service.summarize_paper(
    paper_text=text
)

# 각각 자동으로 평가되어 Langfuse에 기록됨
# Langfuse에서 점수 비교
```

### 3. 품질 임계값 설정

```python
evaluation = await llm_service.evaluate_summary(...)

if evaluation['overall_score'] < 7.0:
    print("⚠️  Low quality summary - consider regenerating")
    # 다른 모델이나 프롬프트로 재시도
```

## 🛠️ 환경 설정

### 필수 환경 변수 (.env)

```env
# OpenAI
OPENAI_API_KEY=sk-proj-...

# Langfuse (평가 로깅용)
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

Langfuse 키가 없으면:
- 평가는 실행되지만
- Langfuse에 로그가 남지 않음

## 💡 주요 특징

### 1. 비간섭적 (Non-intrusive)
- 평가 실패 시에도 요약은 정상 반환
- 사용자 경험에 영향 없음

### 2. 일관성 있는 평가
- Temperature 0.3으로 안정적 평가
- 구조화된 JSON 응답

### 3. 상세한 피드백
```json
{
  "overall_score": 8.6,
  "reasoning": "평가 근거...",
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["약점1", "약점2"]
}
```

### 4. 비용 효율적
- GPT-5-mini 사용 (저렴)
- 원문은 10,000자로 제한
- 평가당 약 $0.001-0.002

## 📚 더 알아보기

- **상세 가이드**: [EVALUATION_GUIDE.md](EVALUATION_GUIDE.md)
- **LLM 서비스 코드**: [app/services/llm_service.py](app/services/llm_service.py)
- **API 라우트**: [app/api/routes.py](app/api/routes.py)

## 🤝 기여

개선 사항이나 버그 발견 시:
1. Issue 생성
2. PR 제출
3. 테스트 추가

## 📄 라이선스

프로젝트 메인 라이선스와 동일
