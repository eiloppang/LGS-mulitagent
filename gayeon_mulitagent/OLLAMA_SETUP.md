# Ollama 설치 및 사용 가이드

이 프로젝트를 Ollama로 실행하는 방법입니다. **무료**로 로컬에서 실행할 수 있습니다!

## 📦 1단계: Ollama 설치

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### macOS
```bash
brew install ollama
```

### Windows
https://ollama.com/download 에서 다운로드

## 🚀 2단계: Ollama 실행

```bash
# Ollama 서버 시작 (백그라운드)
ollama serve
```

새 터미널을 열고 계속 진행하세요.

## 📥 3단계: 필요한 모델 다운로드

```bash
# 메인 모델 (LLM) - 약 4.7GB
ollama pull llama3.1

# 임베딩 모델 (벡터 검색용) - 약 274MB
ollama pull nomic-embed-text
```

### 추천 모델 (선택사항)

더 나은 성능이 필요하면 다른 모델을 사용할 수 있습니다:

```bash
# 한국어에 강한 모델들
ollama pull qwen2.5:7b          # 약 4.7GB, 한국어 우수
ollama pull gemma2:9b           # 약 5.5GB, 성능 우수
ollama pull mistral             # 약 4.1GB, 빠르고 효율적

# 큰 모델 (더 좋은 품질, 더 느림)
ollama pull llama3.1:70b        # 약 40GB (GPU 필수)
```

## 🛠️ 4단계: 프로젝트 설정

```bash
cd /home/work/gayeon_mulitagent

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (선택사항)
cp .env.example .env
```

`.env` 파일 (기본값으로도 동작):
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

## ▶️ 5단계: 실행

```bash
# 대화형 챗봇 실행
python main.py

# 또는 예제 실행
python examples.py
```

## 🎯 모델 선택 가이드

### LLM 모델 (답변 생성용)

| 모델 | 크기 | 속도 | 품질 | 한국어 | 추천 |
|------|------|------|------|--------|------|
| `llama3.1` | 4.7GB | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ 기본 |
| `qwen2.5:7b` | 4.7GB | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🇰🇷 한국어 최고 |
| `mistral` | 4.1GB | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 🚀 빠름 |
| `gemma2:9b` | 5.5GB | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 💎 품질 최고 |

### 임베딩 모델 (벡터 검색용)

| 모델 | 크기 | 속도 | 품질 | 추천 |
|------|------|------|------|------|
| `nomic-embed-text` | 274MB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ 기본 |
| `mxbai-embed-large` | 669MB | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 💎 품질 최고 |

## 🔧 다른 모델 사용하기

### 방법 1: 환경 변수로 변경

`.env` 파일 수정:
```bash
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large
```

### 방법 2: 코드에서 직접 변경

```python
from agents import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator(
    talk_style_dir="./GS_talk_style",
    paper_dir="./GS_paper",
    max_retries=3
)

# 개별 에이전트 커스터마이징
from agents import KnowledgeAgent, StyleAgent, ValidatorAgent

knowledge = KnowledgeAgent(
    model_name="qwen2.5:7b",          # 한국어 강화
    embedding_model="mxbai-embed-large"  # 품질 향상
)

style = StyleAgent(
    model_name="gemma2:9b",           # 높은 품질
    temperature=0.9                    # 더 창의적
)

validator = ValidatorAgent(
    model_name="llama3.1",
    temperature=0.2                    # 일관된 평가
)
```

## 💡 성능 최적화 팁

### 1. GPU 사용 (NVIDIA)
```bash
# GPU가 있으면 자동으로 사용됩니다
nvidia-smi  # GPU 상태 확인
```

### 2. 메모리 절약
작은 모델 사용:
```bash
ollama pull llama3.1:8b    # 기본 (4.7GB)
ollama pull mistral        # 더 작음 (4.1GB)
ollama pull phi3           # 매우 작음 (2.3GB)
```

### 3. 속도 향상
```python
# chunk_size 줄이기 (메모리 절약)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,   # 기본 1000
    chunk_overlap=50  # 기본 100
)

# 검색 결과 수 줄이기
result = knowledge_agent.process({
    "query": "질문",
    "top_k": 3  # 기본 5
})
```

## 🐛 문제 해결

### Ollama가 실행되지 않음
```bash
# 서비스 상태 확인
systemctl status ollama

# 재시작
systemctl restart ollama

# 수동 실행
ollama serve
```

### 모델을 찾을 수 없음
```bash
# 설치된 모델 목록 확인
ollama list

# 모델 다시 다운로드
ollama pull llama3.1
```

### 메모리 부족
- 더 작은 모델 사용 (phi3, mistral)
- chunk_size 줄이기
- 한 번에 하나의 에이전트만 초기화

### 너무 느림
- GPU 드라이버 확인
- 더 빠른 모델 사용 (mistral)
- top_k 값 줄이기

## 📊 성능 비교

### OpenAI API vs Ollama

| 항목 | OpenAI | Ollama |
|------|--------|--------|
| 비용 | 💰 유료 ($$$) | 🆓 무료 |
| 속도 | 🚀 매우 빠름 | ⚡ 빠름 (GPU 필요) |
| 품질 | 💎 최고 | ⭐ 우수 |
| 프라이버시 | ☁️ 클라우드 | 🔒 로컬 |
| 인터넷 | 📡 필수 | 📴 불필요 |
| 설정 | ✅ 간단 | 🔧 약간 복잡 |

## 🎓 추가 학습 자료

- Ollama 공식 문서: https://ollama.com/docs
- 모델 라이브러리: https://ollama.com/library
- Langchain + Ollama: https://python.langchain.com/docs/integrations/llms/ollama

## ⚡ 빠른 시작 (요약)

```bash
# 1. Ollama 설치
curl -fsSL https://ollama.com/install.sh | sh

# 2. 서버 시작
ollama serve &

# 3. 모델 다운로드
ollama pull llama3.1
ollama pull nomic-embed-text

# 4. 의존성 설치
cd /home/work/gayeon_mulitagent
pip install -r requirements.txt

# 5. 실행!
python main.py
```

끝! 🎉
