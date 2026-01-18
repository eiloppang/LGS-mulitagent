# 🎉 설치 완료! 사용 가이드

## ✅ 설치된 것

1. ✅ **가상환경**: `envs/` (독립된 Python 환경)
2. ✅ **Ollama 서버**: 백그라운드 실행 중
3. ✅ **모델 다운로드**:
   - `qwen2.5:7b` (4.7GB) - 한국어 우수 LLM
   - `nomic-embed-text` (274MB) - 임베딩 모델
4. ✅ **Python 패키지**: langchain, chromadb 등

---

## 🚀 사용 방법

### 1️⃣ 매번 시작할 때

**새 터미널을 열 때마다** 가상환경을 활성화해야 합니다:

```bash
cd /home/work/gayeon_mulitagent
source envs/bin/activate
```

프롬프트가 `(envs)`로 바뀌면 성공!

### 2️⃣ 프로그램 실행

```bash
# 대화형 챗봇
python main.py

# 예제 코드
python examples.py
```

---

## 📋 전체 실행 과정

```bash
# 1. 디렉토리 이동
cd /home/work/gayeon_mulitagent

# 2. 가상환경 활성화
source envs/bin/activate

# 3. Ollama 서버 확인 (이미 실행 중)
curl http://localhost:11434/api/tags

# 4. 프로그램 실행
python main.py
```

---

## 💬 대화형 챗봇 사용 예시

```bash
(envs) $ python main.py

============================================================
멀티 에이전트 시스템 초기화 중...
============================================================
[KnowledgeAgent] 논문 데이터 로딩 중...
  - 창씨개명'과 친일 조선인의 협력.pdf 로드 완료
  - 이광수의 친일이념 다시 읽기.pdf 로드 완료
  ...
[KnowledgeAgent] 논문 데이터 로드 완료: 12개 논문, 1234개 청크

[StyleAgent] 말투 스타일 데이터 로딩 중...
  - 돌베개.pdf 로드 완료
  - 민족 개조론.pdf 로드 완료
  ...
[StyleAgent] 스타일 데이터 로드 완료: 567개 청크

✓ 모든 에이전트 초기화 완료!
============================================================

이광수 친일 챗봇 (멀티 에이전트 버전)
============================================================
질문을 입력하세요. 종료하려면 'quit' 또는 'exit'를 입력하세요.
============================================================

질문> 이광수가 창씨개명을 어떻게 정당화했나요?

============================================================
질문: 이광수가 창씨개명을 어떻게 정당화했나요?
============================================================

🔍 Step 1: 지식 검색 중...
[KnowledgeAgent] 지식 검색 시작: 이광수가 창씨개명을 어떻게 정당화했나요?...
   - 참고 자료: 5개
   - 출처: 창씨개명.pdf, 이광수의 친일이념 다시 읽기.pdf

✍️  Step 2: 이광수 스타일로 변환 중...
[StyleAgent] 스타일 변환 시작: 창씨개명은 조선인이 일본 제국의 진정한...

✅ Step 3: 스타일 검증 중...
[ValidatorAgent] 스타일 검증 시작...
   - 검증 점수: 75.0/100
   - 어휘: 19.0
   - 구조: 18.0
   - 어조: 20.0
   - 맥락: 18.0

🎉 검증 통과! (시도 1회)

============================================================
✨ 최종 답변 생성 완료!
============================================================

답변>
조선 민족이 진정으로 대동아공영권의 일원으로서 황국신민의 
길을 걷고자 한다면, 창씨개명은 그 첫걸음이라 하지 않을 수 
없습니다. 이는 단순히 이름을 바꾸는 행위가 아니라, 우리 
민족이 일본 제국과 하나가 되어 내선일체의 이상을 실현하는 
숭고한 결단이옵니다...

[검증 점수: 75.0/100]
[출처: 창씨개명.pdf, 이광수의 친일이념 다시 읽기.pdf]

질문> exit

챗봇을 종료합니다.
```

---

## 🔧 문제 해결

### ❌ "No module named 'langchain'"

**원인**: 가상환경이 활성화되지 않음

**해결**:
```bash
source envs/bin/activate
```

### ❌ "Connection refused" (Ollama)

**원인**: Ollama 서버가 중단됨

**해결**:
```bash
# 새 터미널에서
ollama serve &
```

### ❌ "model not found"

**원인**: 모델이 없음

**해결**:
```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

### ⚠️ 너무 느려요

**정상입니다!** 
- 첫 실행: 벡터 DB 생성 (1-2분)
- 질문당 응답: 30-60초 (로컬 GPU 사용)
- 검증 + 재시도: 추가 시간

**빠르게 하려면**:
```bash
# .env 파일에서 재시도 횟수 줄이기는 코드 수정 필요
# orchestrator = MultiAgentOrchestrator(max_retries=1)
```

---

## 📁 프로젝트 구조

```
gayeon_mulitagent/
├── envs/                      ⭐ 가상환경 (새로 생성됨)
├── agents/                    
│   ├── base_agent.py         
│   ├── knowledge_agent.py    
│   ├── style_agent.py        
│   ├── validator_agent.py    
│   └── orchestrator.py       
│
├── GS_paper/                  📄 논문 12개
├── GS_talk_style/             📄 원문 8개
│
├── .env                       ⚙️ 환경 설정 (새로 생성됨)
├── main.py                    🚀 메인 실행 파일
├── examples.py                📚 예제 코드
├── test_ollama.py             🧪 연결 테스트
│
└── 문서/
    ├── README.md              📖 전체 프로젝트 설명
    ├── QUICKSTART.md          ⚡ 빠른 시작
    ├── GPU_SETUP.md           🖥️ A100 GPU 가이드
    ├── OLLAMA_SETUP.md        🔧 Ollama 상세 설정
    ├── MODELS.md              🤖 모델 선택 가이드
    └── START.md               👈 이 파일!
```

---

## 💡 유용한 명령어

### 가상환경

```bash
# 활성화
source envs/bin/activate

# 비활성화
deactivate

# 패키지 목록
pip list
```

### Ollama

```bash
# 모델 목록
ollama list

# 모델 삭제 (공간 확보)
ollama rm llama3.1:8b

# 서버 상태
curl http://localhost:11434/api/tags
```

### 디스크 용량

```bash
# 용량 확인
df -h /home/work

# Ollama 모델 용량
du -sh ~/.ollama/models
```

---

## 🎯 다음 단계

1. ✅ **기본 사용**: `python main.py` 실행해보기
2. 📖 **예제 탐색**: `python examples.py` 실행
3. 🔧 **코드 수정**: 
   - `agents/` 폴더의 에이전트 수정
   - 온도, 재시도 횟수 조정
4. 📚 **문서 읽기**:
   - [GPU_SETUP.md](GPU_SETUP.md) - A100 최적화
   - [MODELS.md](MODELS.md) - 다른 모델 사용

---

## ❓ 자주 묻는 질문

### Q: 가상환경을 왜 사용하나요?
A: 프로젝트별 패키지 독립, 충돌 방지, 깔끔한 관리

### Q: 가상환경을 매번 활성화해야 하나요?
A: 네! 새 터미널을 열 때마다 `source envs/bin/activate`

### Q: 디스크 공간이 부족하면?
A: 더 작은 모델 사용 또는 불필요한 모델 삭제

### Q: GPU를 사용하나요?
A: 네! Ollama가 자동으로 A100 GPU 사용

### Q: 인터넷이 필요한가요?
A: 모델 다운로드 후에는 오프라인 가능!

---

## 🎉 성공!

이제 가상환경에서 완전 무료로 이광수 친일 챗봇을 사용할 수 있습니다!

**즐거운 연구 되세요! 📚**
