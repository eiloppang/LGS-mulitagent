# Gemini 2.5 Flash API 버전 사용 가이드

## 개요
이 버전은 기존 Ollama 기반 멀티 에이전트 시스템을 Google Gemini 2.5 Flash API를 사용하도록 변환한 버전입니다.

## 주요 변경사항

### 1. 아키텍처
- **기존**: Ollama (로컬 LLM) + LangChain ChatOllama
- **변경**: Google Gemini 2.5 Flash API + `google-genai` 패키지

### 2. 파일 구조
```
gayeon_mulitagent/
├── agents/              # 기존 Ollama 버전
│   ├── base_agent.py
│   ├── knowledge_agent.py
│   ├── style_agent.py
│   ├── validator_agent.py
│   └── orchestrator.py
├── agents_2/            # 신규 Gemini 버전
│   ├── base_agent.py
│   ├── knowledge_agent.py
│   ├── style_agent.py
│   ├── validator_agent.py
│   └── orchestrator.py
├── main.py              # Ollama 버전 실행
└── main_gemini.py       # Gemini 버전 실행
```

## 설치 및 설정

### 1. 필수 패키지 설치
```bash
pip install google-genai
# 또는 전체 requirements 재설치
pip install -r requirements.txt
```

### 2. Gemini API 키 발급
1. [Google AI Studio](https://ai.google.dev/aistudio) 접속
2. "Get API key" 클릭
3. API 키 생성 및 복사

### 3. 환경변수 설정
```bash
# 방법 1: 터미널에서 직접 설정
export GEMINI_API_KEY='your-api-key-here'

# 방법 2: .env 파일 생성
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

### 4. 실행
```bash
python main_gemini.py
```

## API 사용 방식

### 기존 (Ollama)
```python
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOllama(model="gemma3:4b", temperature=0.7)
messages = [
    SystemMessage(content="You are..."),
    HumanMessage(content="질문")
]
response = llm.invoke(messages)
```

### 변경 (Gemini 2.5 Flash)
```python
from google import genai

client = genai.Client()  # GEMINI_API_KEY 자동 로드
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=f"{system_instruction}\n\n{user_message}",
    config={"temperature": 0.7}
)
text = response.text
```

## 주요 차이점

### 1. BaseAgent 클래스
- **기존**: `ChatOllama` 객체 사용
- **변경**: `genai.Client()` 사용, `_generate_content()` 헬퍼 메서드 추가

### 2. 메시지 처리
- **기존**: SystemMessage + HumanMessage 리스트
- **변경**: 단일 문자열로 시스템 프롬프트와 사용자 메시지 결합

### 3. 임베딩
- **변경 없음**: 벡터스토어는 계속 Ollama의 `nomic-embed-text` 사용
- 이유: Gemini는 임베딩 API가 별도이며, 기존 벡터DB 재활용 가능

### 4. 모델 이름
- Ollama: `gemma3:4b`, `llama3.1`, `qwen2.5` 등
- Gemini: `gemini-2.0-flash-exp`, `gemini-2.5-flash` 등

## 비용 및 성능

### Gemini 2.5 Flash
- **무료 할당량**: 1,500 요청/일 (공식 문서 확인 필요)
- **속도**: 매우 빠름 (클라우드 기반)
- **품질**: 높은 품질의 응답

### Ollama (비교)
- **비용**: 무료 (로컬 실행)
- **속도**: GPU 성능에 따라 다름
- **품질**: 모델에 따라 다름

## 테스트 예시

```python
from agents_2.orchestrator import MultiAgentOrchestrator

# 초기화
orchestrator = MultiAgentOrchestrator(
    talk_style_dir="./GS_talk_style",
    paper_dir="./GS_paper",
    max_retries=3,
    model_name="gemini-2.0-flash-exp"
)

# 질문 처리
result = orchestrator.process_query(
    "이광수 선생님, 친일 행위에 대해 어떻게 생각하시나요?",
    verbose=True
)

print(result['final_answer'])
print(f"검증 점수: {result['validation_score']}")
```

## 주의사항

1. **API 키 보안**: `.gitignore`에 `.env` 파일 추가
2. **Rate Limit**: API 호출 제한을 고려하여 사용
3. **네트워크**: 인터넷 연결 필요 (클라우드 API)
4. **호환성**: Python 3.10 이상 권장

## 문제 해결

### 1. API 키 오류
```
Error: API key not valid
```
- 환경변수가 올바르게 설정되었는지 확인
- API 키가 유효한지 Google AI Studio에서 확인

### 2. 모듈 임포트 오류
```
ModuleNotFoundError: No module named 'google.genai'
```
- `pip install google-genai` 실행

### 3. Rate Limit 초과
```
Error: Quota exceeded
```
- 일일 무료 할당량 초과, 시간을 두고 재시도
- 또는 유료 플랜 고려

## 향후 개선 사항

1. **Gemini 임베딩 통합**: Ollama 대신 Gemini 임베딩 API 사용
2. **스트리밍 응답**: 실시간 스트리밍 구현
3. **비용 최적화**: 캐싱 및 배치 처리
4. **다양한 모델**: gemini-pro, gemini-ultra 등 추가 지원

## 참고 자료

- [Google Gemini API 공식 문서](https://ai.google.dev/docs)
- [google-genai Python 패키지](https://pypi.org/project/google-genai/)
- [Gemini 가격 정보](https://ai.google.dev/pricing)
