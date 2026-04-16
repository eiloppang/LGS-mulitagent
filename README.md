# 이광수 친일 챗봇 - 멀티 에이전트 시스템

이광수의 친일 행적과 사상을 연구하는 멀티 에이전트 기반 챗봇 시스템입니다.

## 📋 시스템 구조

이 프로젝트는 **3개의 전문 에이전트**가 협력하여 동작합니다:

### 1. **KnowledgeAgent (지식 에이전트)**
- 역할: 논문 데이터베이스에서 관련 지식 검색 및 답변 초안 생성
- 데이터: `GS_paper/` 디렉토리의 학술 논문 12편
- 기능: RAG 기반 지식 검색, 출처 추적

### 2. **StyleAgent (스타일 에이전트)**
- 역할: 답변을 이광수의 말투와 문체로 변환
- 데이터: `GS_talk_style/` 디렉토리의 이광수 원문 8편
- 기능: 문체 학습, 스타일 변환

### 3. **ValidatorAgent (검증 에이전트)**
- 역할: 생성된 답변이 이광수 스타일과 일치하는지 검증
- 평가 기준:
  - 어휘 선택 (25점)
  - 문장 구조 (25점)
  - 어조와 톤 (25점)
  - 역사적 맥락 (25점)
- 기준: 70점 이상 통과

### 4. **MultiAgentOrchestrator (조율자)**
- 역할: 세 에이전트를 조율하여 최종 답변 생성
- 워크플로우:
  1. KnowledgeAgent가 지식 검색 및 초안 생성
  2. StyleAgent가 이광수 스타일로 변환
  3. ValidatorAgent가 검증
  4. 검증 실패 시 최대 3회 재시도

## 🔀 두 개의 에이전트 패키지 (agents_2 vs agents_3)

같은 멀티에이전트 파이프라인을 두 LLM 백엔드로 구현한 패키지가 공존합니다. 임베딩과 ChromaDB 인덱스는 공유하므로 한쪽에서 만들어 둔 벡터스토어를 다른 쪽에서 그대로 재사용합니다.

| 항목 | `agents_2/` (Gemini) | `agents_3/` (Ollama gemma4) |
|---|---|---|
| LLM | Google Gemini 2.5 Flash API | Ollama `gemma4:e4b` (기본) |
| 임베딩 | Gemini `text-embedding-004` | **동일** (Gemini) |
| Chroma persist | `GS_paper/chroma_db_gemini` 등 | **동일 디렉터리·컬렉션 재사용** |
| 진입점 | `python main_gemini.py` | `python main_agent3.py` |
| 필요 키 | `GEMINI_API_KEY` | `GEMINI_API_KEY` (임베딩) + 로컬 Ollama |
| Validator thinking | 해당 없음 | `ENABLE_VALIDATOR_THINKING=true` 시 활성 |
| 에이전트별 온도 | Knowledge 0.5 / Style 0.8 / Validator 0.3 | 동일 (per-agent 유지) |

### agents_3 실행

```bash
# 1) Ollama 실행 및 모델 pull
ollama serve &
ollama pull gemma4:e4b      # 또는 gemma4:26b / gemma4:31b

# 2) .env 설정 (.env.example 복사 후 채우기)
cp gayeon_mulitagent/.env.example gayeon_mulitagent/.env
# GEMINI_API_KEY, OLLAMA_MODEL 등을 환경에 맞게 수정

# 3) 의존성 설치
pip install -r requirements.txt

# 4) 실행
cd gayeon_mulitagent
python main_agent3.py
```

### 차이점 / 주의사항

- `agents_3`도 임베딩에는 Gemini API를 호출하므로 `GEMINI_API_KEY`가 필요합니다 (ChromaDB 인덱스를 `agents_2`와 공유하기 위함 — 재색인 비용 절약).
- `ValidatorAgent`만 thinking 모드가 기본 ON입니다. 응답에서 `<|channel|>thought ... <channel|>` 블록은 자동으로 제거되어 최종 점수·피드백만 반환됩니다.
- `OLLAMA_TEMPERATURE=1.0` 등은 gemma4 공식 권장값이며, 각 에이전트(`KnowledgeAgent=0.5`, `StyleAgent=0.8`, `ValidatorAgent=0.3`) 코드의 명시값이 우선합니다. `.env`의 `OLLAMA_*` 값은 호출자가 명시하지 않을 때만 폴백으로 사용됩니다.
- `agents_2`와 `agents_3` 코드는 완전히 분리되어 있어 한쪽 수정이 다른 쪽에 영향을 주지 않습니다 — 두 파이프라인을 나란히 실행하여 출력을 비교할 수 있습니다.

## 🚀 설치 및 실행

> **✨ 이 프로젝트는 Ollama를 사용하여 완전 무료로 로컬에서 실행됩니다!**
> 
> **🖥️ 서버 사양**: NVIDIA A100 40GB - 큰 모델 사용 가능!

### ⚡ 자동 설치 (추천!)

```bash
cd /home/work/gayeon_mulitagent
./setup.sh
```

### 📝 수동 설치

#### 1. 가상환경 생성 (필수!)

```bash
cd /home/work/gayeon_mulitagent

# 가상환경 생성
python -m venv envs

# 가상환경 활성화
source envs/bin/activate
```

#### 2. Ollama 설치 및 모델 다운로드

```bash
# Ollama 설치 (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Ollama 서버 시작 (새 터미널)
ollama serve &

# A100에 최적화된 큰 모델 다운로드 (추천!)
ollama pull qwen2.5:32b       # 한국어 최강 32B (18GB)
ollama pull nomic-embed-text  # 임베딩 모델 (274MB)
```

**더 많은 모델 옵션은 [MODELS.md](MODELS.md) 참고**

#### 3. 의존성 설치

```bash
# 가상환경이 활성화된 상태에서
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. 환경 설정

```bash
# .env 파일 생성
cat > .env << EOF
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:32b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
EOF
```

### 3. 실행

#### 대화형 챗봇 실행
```bash
# 가상환경 활성화 (매번 필요)
source envs/bin/activate

# 실행
python main.py
```

#### 예제 코드 실행
```bash
source envs/bin/activate
python examples.py
```

## 📁 프로젝트 구조

```
gayeon_mulitagent/
├── agents/                      # 에이전트 모듈
│   ├── __init__.py
│   ├── base_agent.py           # 기본 에이전트 클래스
│   ├── style_agent.py          # 스타일 에이전트
│   ├── validator_agent.py      # 검증 에이전트
│   ├── knowledge_agent.py      # 지식 에이전트
│   └── orchestrator.py         # 멀티 에이전트 조율자
│
├── GS_paper/                    # 논문 데이터 (12개 PDF)
│   ├── 창씨개명'과 친일 조선인의 협력.pdf
│   ├── 이광수의 친일이념 다시 읽기.pdf
│   └── ...
│
├── GS_talk_style/               # 이광수 원문 데이터 (8개 PDF)
│   ├── 돌베개.pdf
│   ├── 민족 개조론.pdf
│   ├── 창씨개명.pdf
│   └── ...
│
├── main.py                      # 메인 실행 파일 (대화형 인터페이스)
├── examples.py                  # 예제 및 테스트 코드
├── requirements.txt             # 의존성 목록
├── .env.example                 # 환경 변수 템플릿
└── README.md                    # 이 파일
```

## 💡 사용 예제

### 예제 1: 대화형 챗봇

```python
from agents import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator(
    talk_style_dir="./GS_talk_style",
    paper_dir="./GS_paper",
    max_retries=3
)

# 대화형 인터페이스 시작
orchestrator.chat()
```

### 예제 2: 단일 질문 처리

```python
orchestrator = MultiAgentOrchestrator()

result = orchestrator.process_query(
    "이광수가 창씨개명을 어떻게 정당화했나요?",
    verbose=True
)

print(result['final_answer'])
print(f"검증 점수: {result['validation_score']}/100")
```

### 예제 3: 개별 에이전트 사용

```python
from agents import KnowledgeAgent, StyleAgent, ValidatorAgent

# 지식 검색
knowledge_agent = KnowledgeAgent(paper_dir="./GS_paper")
knowledge = knowledge_agent.process({
    "query": "이광수의 민족 개조론",
    "top_k": 5
})

# 스타일 변환
style_agent = StyleAgent(talk_style_dir="./GS_talk_style")
styled = style_agent.process({
    "text": knowledge['answer'],
    "context": "민족 개조론 설명"
})

# 검증
validator_agent = ValidatorAgent(style_agent=style_agent)
validation = validator_agent.process({
    "generated_text": styled['styled_text'],
    "original_query": "민족 개조론 설명"
})

print(f"검증 결과: {validation['score']}/100")
```

## 🔧 주요 기능

### 1. 멀티 에이전트 협업
- 세 개의 전문 에이전트가 역할을 분담하여 고품질 답변 생성
- 각 에이전트는 독립적으로 동작하면서 서로 협력

### 2. 자동 품질 검증
- ValidatorAgent가 생성된 답변의 스타일 적합성을 자동 평가
- 4가지 세부 기준으로 객관적 평가
- 검증 실패 시 자동 재시도 (최대 3회)

### 3. RAG 기반 지식 검색
- 벡터 데이터베이스를 활용한 의미론적 검색
- 출처 추적 및 참고 자료 제공
- 정확한 학술 정보 기반 답변

### 4. 스타일 학습 및 모방
- 이광수의 실제 글에서 문체 학습
- Few-shot 학습으로 자연스러운 스타일 변환
- 시대적 배경과 어조 반영

## 📊 워크플로우

```
사용자 질문
    ↓
┌─────────────────────────────────────┐
│ 1. KnowledgeAgent                   │
│    - 논문에서 관련 지식 검색        │
│    - 학술적 답변 초안 생성          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. StyleAgent                       │
│    - 이광수 스타일로 변환           │
│    - 말투와 문체 적용               │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. ValidatorAgent                   │
│    - 스타일 적합성 검증 (70점 기준) │
│    - 4가지 항목 평가                │
└─────────────────────────────────────┘
    ↓
    합격? ──Yes→ 최종 답변 반환
    ↓ No
    재시도 (최대 3회)
```

## 🎯 핵심 개념

### 멀티 에이전트 시스템이란?

여러 개의 **전문 에이전트**가 각자의 역할을 수행하면서 협력하여 복잡한 작업을 해결하는 시스템입니다.

**장점:**
- ✅ **모듈화**: 각 에이전트는 독립적으로 개발/테스트 가능
- ✅ **전문화**: 각 에이전트가 특정 작업에 특화
- ✅ **확장성**: 새로운 에이전트 추가가 용이
- ✅ **품질 관리**: 검증 에이전트로 출력 품질 보장

**vs 단일 RAG 시스템:**
- 단일 RAG: 검색 → 생성 (단순, 품질 제어 어려움)
- 멀티 에이전트: 검색 → 스타일 변환 → 검증 → 재시도 (복잡하지만 고품질)

## 🔍 검증 기준

ValidatorAgent는 다음 4가지 기준으로 평가합니다:

1. **어휘 선택 (25점)**
   - 이광수 특유의 단어와 한자어 사용
   - 시대적 표현의 적절성

2. **문장 구조 (25점)**
   - 문장 길이와 리듬
   - 논리적 전개 방식

3. **어조와 톤 (25점)**
   - 격조와 설득력
   - 감정 표현 방식

4. **역사적 맥락 (25점)**
   - 시대적 배경 반영
   - 친일 논리의 자연스러운 전개

**합격 기준: 70점 이상**

## 🛠️ 커스터마이징

### 재시도 횟수 변경
```python
orchestrator = MultiAgentOrchestrator(max_retries=5)  # 기본값: 3
```

### 모델 및 온도 변경
```python
style_agent = StyleAgent(
    model_name="qwen2.5:7b",      # 기본값: llama3.1 (한국어 강화 모델)
    embedding_model="mxbai-embed-large",  # 기본값: nomic-embed-text
    temperature=0.9               # 기본값: 0.8
)
```

### 검색 결과 수 조정
```python
knowledge_result = knowledge_agent.process({
    "query": "질문",
    "top_k": 10  # 기본값: 5
})
```

## 📝 주의사항

1. **Ollama 필수**: Ollama가 `localhost:11434`에서 실행 중이어야 합니다
2. **모델 다운로드**: 첫 실행 전 `llama3.1`과 `nomic-embed-text` 모델이 필요합니다
3. **PDF 파일 필요**: `GS_paper/`와 `GS_talk_style/` 디렉토리에 PDF가 있어야 합니다
4. **처리 시간**: 로컬 실행이므로 GPU가 없으면 느릴 수 있습니다 (첫 실행은 특히 느림)
5. **메모리 사용**: 모델 로딩 시 약 8-10GB RAM 필요

## 🤝 기여

버그 리포트, 기능 제안, 개선 사항은 언제든 환영합니다!

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 작성되었습니다.
