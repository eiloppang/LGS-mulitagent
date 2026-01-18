# A100 GPU를 위한 추천 모델 및 사용법

## 🎯 A100 40GB 최적 설정

### 최종 추천: qwen2.5:32b

**이유:**
- ✅ 한국어 성능 최고
- ✅ A100 VRAM의 50% 사용 (여유 있음)
- ✅ 빠른 응답 속도 (70B의 2배)
- ✅ 품질도 우수

## 📥 모델 다운로드

```bash
# 1. 메인 모델 (한국어 최적)
ollama pull qwen2.5:32b

# 2. 임베딩 모델 (필수)
ollama pull nomic-embed-text

# 다운로드 확인
ollama list
```

## ⚙️ 환경 설정

`.env` 파일:
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:32b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

## 🚀 실행

```bash
# 가상환경 활성화
source envs/bin/activate

# 실행
python main.py
```

## 📊 성능 예상

| 작업 | 예상 시간 |
|------|-----------|
| 첫 모델 로딩 | 10-15초 |
| 질문 → 답변 | 30-60초 |
| 검증 + 재시도 | 추가 30초 |

## 💡 다른 모델 옵션

### 옵션 1: 최고 품질 (느림)
```bash
ollama pull llama3.1:70b
# .env에서 OLLAMA_MODEL=llama3.1:70b
```

### 옵션 2: 가장 빠름 (품질 약간 낮음)
```bash
ollama pull qwen2.5:7b
# .env에서 OLLAMA_MODEL=qwen2.5:7b
```

### 옵션 3: 균형 (기본)
```bash
ollama pull llama3.1:8b
# .env에서 OLLAMA_MODEL=llama3.1:8b
```
