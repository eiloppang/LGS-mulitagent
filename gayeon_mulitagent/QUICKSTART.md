# 🚀 빠른 시작 가이드 (Ollama)

## 완전히 처음부터 시작하기

### 1️⃣ Ollama 설치

```bash
# Linux/WSL
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Windows: https://ollama.com/download 에서 다운로드
```

### 2️⃣ Ollama 서버 실행

**새 터미널을 열고:**
```bash
ollama serve
```

> 💡 이 터미널은 계속 열어두세요! 백그라운드에서 실행됩니다.

### 3️⃣ 모델 다운로드

**또 다른 새 터미널을 열고:**
```bash
# LLM 모델 (답변 생성용)
ollama pull llama3.1

# 임베딩 모델 (검색용)
ollama pull nomic-embed-text
```

다운로드 시간:
- `llama3.1`: 약 5-10분 (4.7GB)
- `nomic-embed-text`: 약 1분 (274MB)

### 4️⃣ 모델 설치 확인

```bash
ollama list
```

다음과 같이 보여야 합니다:
```
NAME                    ID              SIZE    MODIFIED
llama3.1:latest         42182419e950    4.7 GB  2 minutes ago
nomic-embed-text:latest 0a109f422b47    274 MB  1 minute ago
```

### 5️⃣ Python 패키지 설치

```bash
cd /home/work/gayeon_mulitagent
pip install -r requirements.txt
```

설치되는 주요 패키지:
- `langchain`: LLM 프레임워크
- `langchain-community`: Ollama 연동
- `chromadb`: 벡터 DB
- `pypdf`: PDF 읽기

### 6️⃣ 실행!

```bash
python main.py
```

## 🎯 사용 예시

### 예제 1: 대화형 챗봇

```bash
python main.py
```

```
질문> 이광수가 창씨개명을 어떻게 정당화했나요?

🔍 Step 1: 지식 검색 중...
   - 참고 자료: 5개
   - 출처: 창씨개명.pdf, 이광수의 친일이념 다시 읽기.pdf

✍️  Step 2: 이광수 스타일로 변환 중...

✅ Step 3: 스타일 검증 중...
   - 검증 점수: 78.5/100
   - 어휘: 20.0
   - 구조: 19.0
   - 어조: 20.5
   - 맥락: 19.0

🎉 검증 통과! (시도 1회)

답변>
조선 민족이 진정으로 일본 제국의 일원이 되고자 한다면...
[이광수 스타일의 답변]

[검증 점수: 78.5/100]
[출처: 창씨개명.pdf, 이광수의 친일이념 다시 읽기.pdf]
```

### 예제 2: Python 코드로 사용

```python
from agents import MultiAgentOrchestrator

# 초기화
orchestrator = MultiAgentOrchestrator(
    talk_style_dir="./GS_talk_style",
    paper_dir="./GS_paper",
    max_retries=3
)

# 질문 처리
result = orchestrator.process_query(
    "이광수의 민족 개조론에 대해 설명해주세요.",
    verbose=True
)

# 결과 확인
print(result['final_answer'])
print(f"점수: {result['validation_score']}/100")
print(f"출처: {result['knowledge_sources']}")
```

### 예제 3: 개별 에이전트 사용

```python
from agents import KnowledgeAgent, StyleAgent, ValidatorAgent

# 1. 지식 검색
knowledge = KnowledgeAgent()
kb_result = knowledge.process({
    "query": "이광수의 징병 관련 글",
    "top_k": 5
})

print(kb_result['answer'])

# 2. 스타일 변환
style = StyleAgent()
styled_result = style.process({
    "text": kb_result['answer'],
    "context": "징병 관련"
})

print(styled_result['styled_text'])

# 3. 검증
validator = ValidatorAgent(style_agent=style)
val_result = validator.process({
    "generated_text": styled_result['styled_text'],
    "original_query": "징병 관련"
})

print(f"검증 점수: {val_result['score']}/100")
```

## 🔧 문제 해결

### ❌ "Connection refused" 오류

**원인**: Ollama 서버가 실행되지 않음

**해결**:
```bash
# 서버 실행
ollama serve
```

### ❌ "model not found" 오류

**원인**: 모델이 다운로드되지 않음

**해결**:
```bash
# 모델 다운로드
ollama pull llama3.1
ollama pull nomic-embed-text

# 설치 확인
ollama list
```

### ❌ "No module named 'langchain_community'"

**원인**: 패키지가 설치되지 않음

**해결**:
```bash
pip install -r requirements.txt
```

### ⚠️ 너무 느려요

**원인**: GPU가 없거나 큰 모델 사용

**해결**:

1. 더 작은 모델 사용:
```bash
ollama pull mistral  # 4.1GB, 더 빠름
```

2. 코드에서 모델 변경:
```python
orchestrator = MultiAgentOrchestrator(
    # ... 
)
# 환경 변수에서 OLLAMA_MODEL=mistral 설정
```

3. GPU 사용 확인:
```bash
nvidia-smi  # NVIDIA GPU 확인
```

### 📊 메모리 부족

**원인**: RAM이 부족함

**해결**:

1. 더 작은 모델:
```bash
ollama pull phi3  # 2.3GB, 가벼움
```

2. chunk_size 줄이기 (코드 수정 필요)

## 💡 팁

### 한국어 성능 향상

```bash
# Qwen 모델 다운로드 (한국어 우수)
ollama pull qwen2.5:7b
```

`.env` 파일:
```
OLLAMA_MODEL=qwen2.5:7b
```

### 품질 향상

```bash
# 더 큰 모델 사용 (GPU 권장)
ollama pull llama3.1:70b  # 40GB, 매우 높은 품질
```

### 속도 향상

```bash
# 빠른 모델 사용
ollama pull mistral
```

## 📚 다음 단계

1. ✅ **기본 실행 완료** → `python main.py`
2. 📖 **예제 실행** → `python examples.py`
3. 🔧 **코드 커스터마이징** → 모델/파라미터 변경
4. 📊 **성능 튜닝** → [OLLAMA_SETUP.md](OLLAMA_SETUP.md) 참고

## ❓ 자주 묻는 질문

### Q: 인터넷 연결이 필요한가요?
A: 모델 다운로드 시에만 필요. 이후 완전 오프라인 가능!

### Q: OpenAI API 키가 필요한가요?
A: 아니요! Ollama는 완전 무료 & 로컬입니다.

### Q: GPU가 필수인가요?
A: 아니요. CPU만으로도 가능하지만 느림. GPU 권장.

### Q: 어떤 GPU가 필요한가요?
A: NVIDIA GPU (CUDA 지원). 최소 8GB VRAM 권장.

### Q: 비용이 드나요?
A: 완전 무료! 전기세만 나갑니다 😄

## 🎉 성공!

이제 무료로 로컬에서 이광수 친일 챗봇을 사용할 수 있습니다!

더 자세한 내용은:
- [README.md](README.md) - 전체 프로젝트 설명
- [OLLAMA_SETUP.md](OLLAMA_SETUP.md) - 상세 Ollama 가이드
