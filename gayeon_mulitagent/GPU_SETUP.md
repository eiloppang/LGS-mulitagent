# 가상환경 설정 및 GPU 활용 가이드

## 🖥️ 서버 사양

**GPU**: NVIDIA A100 40GB (최고급!)
- VRAM: 40GB 
- CUDA: 12.8
- 권장: 큰 모델 사용 가능 (70B 모델도 OK!)

---

## 📦 1단계: 가상환경 생성

### 방법 1: venv 사용 (추천)

```bash
cd /home/work/gayeon_mulitagent

# 가상환경 생성
python -m venv envs

# 가상환경 활성화
source envs/bin/activate

# 프롬프트가 (envs)로 바뀝니다
```

### 방법 2: conda 사용 (이미 설치되어 있다면)

```bash
# 가상환경 생성
conda create -n gayeon_multiagent python=3.12 -y

# 활성화
conda activate gayeon_multiagent
```

---

## 📥 2단계: 패키지 설치

```bash
# 가상환경이 활성화된 상태에서
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 3단계: Ollama 설치 및 큰 모델 다운로드

### Ollama 서버 시작 (백그라운드)

```bash
# 새 터미널 (또는 tmux/screen 사용)
ollama serve
```

### A100 40GB에 최적화된 큰 모델 다운로드

```bash
# 70B 모델 - 최고 품질! (A100에 완벽)
ollama pull llama3.1:70b       # 약 40GB

# 또는 한국어 강화 대형 모델
ollama pull qwen2.5:32b        # 약 18GB, 한국어 우수

# 임베딩 모델 (필수)
ollama pull nomic-embed-text   # 274MB
```

---

## ⚙️ 4단계: 환경 변수 설정

```bash
# .env 파일 생성
cat > .env << 'EOF'
# Ollama 설정
OLLAMA_BASE_URL=http://localhost:11434

# 큰 모델 사용 (A100 40GB 활용)
OLLAMA_MODEL=llama3.1:70b

# 임베딩 모델
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
EOF
```

---

## 🎯 5단계: 실행

```bash
# 가상환경 활성화 확인
source envs/bin/activate  # venv
# 또는
# conda activate gayeon_multiagent

# 실행!
python main.py
```

---

## 💡 A100 40GB 추천 모델

### LLM 모델 (답변 생성)

| 모델 | 크기 | VRAM | 품질 | 속도 | 한국어 | 추천 |
|------|------|------|------|------|--------|------|
| `llama3.1:70b` | 40GB | 40GB | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | 🏆 최고 품질 |
| `qwen2.5:32b` | 18GB | 20GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🇰🇷 한국어 최강 |
| `qwen2.5:72b` | 41GB | 42GB | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | 🎯 한국어+품질 |
| `gemma2:27b` | 16GB | 18GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⚡ 빠르고 우수 |
| `llama3.1:8b` | 4.7GB | 6GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 🚀 테스트용 |

### 🎯 **최종 추천**: `qwen2.5:32b` 또는 `llama3.1:70b`

**qwen2.5:32b** (추천!)
- 한국어 성능이 압도적
- A100의 절반만 사용 (여유)
- 빠른 응답 속도

**llama3.1:70b**
- 최고 품질
- A100 VRAM 거의 풀 사용
- 조금 느림

---

## 🔄 모델 전환하기

### 방법 1: 환경 변수로 전환

```bash
# .env 파일 수정
nano .env

# OLLAMA_MODEL=qwen2.5:32b 로 변경
```

### 방법 2: 코드에서 직접 지정

`main.py` 수정:

```python
orchestrator = MultiAgentOrchestrator(
    talk_style_dir="./GS_talk_style",
    paper_dir="./GS_paper",
    max_retries=3
)
```

각 에이전트를 직접 생성:

```python
from agents import KnowledgeAgent, StyleAgent, ValidatorAgent

# 큰 모델 사용
knowledge = KnowledgeAgent(
    model_name="qwen2.5:32b",  # 32B 모델!
    embedding_model="nomic-embed-text"
)

style = StyleAgent(
    model_name="qwen2.5:32b",
    temperature=0.9
)

validator = ValidatorAgent(
    model_name="llama3.1:70b",  # 검증은 최고 품질 모델
    temperature=0.2
)
```

---

## 🚀 고급 설정: 혼합 전략

서로 다른 에이전트에 다른 모델 사용:

```python
# 지식 검색: 빠른 모델
knowledge = KnowledgeAgent(model_name="qwen2.5:7b")

# 스타일 변환: 큰 모델 (중요!)
style = StyleAgent(model_name="qwen2.5:32b", temperature=0.9)

# 검증: 최고 품질 모델
validator = ValidatorAgent(model_name="llama3.1:70b", temperature=0.2)
```

---

## 📊 성능 비교 (A100 기준)

### 응답 시간 예상

| 모델 | 초기 로딩 | 토큰/초 | 전체 응답 |
|------|-----------|---------|-----------|
| llama3.1:8b | 5초 | ~100 | 15-20초 |
| qwen2.5:7b | 5초 | ~100 | 15-20초 |
| qwen2.5:32b | 10초 | ~50 | 30-40초 |
| llama3.1:70b | 15초 | ~25 | 60-90초 |
| qwen2.5:72b | 20초 | ~20 | 90-120초 |

---

## 🔧 가상환경 관리 명령어

### venv

```bash
# 활성화
source envs/bin/activate

# 비활성화
deactivate

# 삭제 (필요시)
rm -rf envs
```

### conda

```bash
# 활성화
conda activate gayeon_multiagent

# 비활성화
conda deactivate

# 삭제 (필요시)
conda env remove -n gayeon_multiagent
```

---

## 📝 전체 설치 스크립트 (복사해서 실행)

```bash
#!/bin/bash

cd /home/work/gayeon_mulitagent

# 1. 가상환경 생성
echo "🔨 가상환경 생성 중..."
python -m venv envs
source envs/bin/activate

# 2. 패키지 설치
echo "📦 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Ollama 모델 다운로드 (다른 터미널에서 ollama serve 실행 필요)
echo "📥 큰 모델 다운로드 중..."
ollama pull qwen2.5:32b        # 한국어 강화 32B
ollama pull nomic-embed-text   # 임베딩

# 4. 환경 변수 설정
echo "⚙️  환경 변수 설정 중..."
cat > .env << 'EOF'
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:32b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
EOF

echo "✅ 설치 완료!"
echo ""
echo "실행 방법:"
echo "1. 새 터미널에서: ollama serve"
echo "2. 이 터미널에서: python main.py"
```

**실행**:
```bash
chmod +x setup.sh
./setup.sh
```

---

## 🎯 빠른 시작 (A100 최적화)

```bash
# 1. 가상환경 생성 & 활성화
cd /home/work/gayeon_mulitagent
python -m venv envs
source envs/bin/activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. Ollama 서버 시작 (새 터미널)
ollama serve &

# 4. 큰 모델 다운로드 (한국어 최적)
ollama pull qwen2.5:32b
ollama pull nomic-embed-text

# 5. 환경 설정
echo "OLLAMA_MODEL=qwen2.5:32b" > .env

# 6. 실행!
python main.py
```

---

## ❓ FAQ

### Q: 가상환경을 왜 만드나요?
A: 프로젝트별 패키지 충돌 방지, 깔끔한 관리

### Q: 70B 모델이 너무 느린데?
A: `qwen2.5:32b` 추천! 한국어도 더 좋고 2배 빠름

### Q: VRAM이 부족하다고 나와요
A: 더 작은 모델 사용 (`qwen2.5:7b`, `llama3.1:8b`)

### Q: 여러 모델을 동시에 사용할 수 있나요?
A: 네! 각 에이전트마다 다른 모델 지정 가능

### Q: 가상환경을 매번 활성화해야 하나요?
A: 네, 새 터미널을 열 때마다 `source envs/bin/activate` 필요

---

## 🎉 완료!

이제 A100 GPU를 활용한 고품질 멀티 에이전트 시스템 사용 가능!
