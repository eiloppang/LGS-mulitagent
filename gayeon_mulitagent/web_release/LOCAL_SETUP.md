# 이광수 AI - 로컬 환경 설정 가이드 (Windows)

Gemini 2.5 Flash API 기반 멀티 에이전트 시스템을 로컬 Windows 환경에서 실행하는 가이드입니다.

## 📋 사전 요구사항

- Python 3.10 이상
- Gemini API Key ([Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급)
- Git Bash 또는 PowerShell

## 🚀 로컬 환경 설정

### 1. 환경 변수 설정

프로젝트 루트의 `.env` 파일에 다음 내용을 추가하세요:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=models/gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=models/text-embedding-004
```

### 2. 가상환경 활성화

#### PowerShell
```powershell
# 프로젝트 루트에서
.\envs\Scripts\Activate.ps1
```

#### Git Bash
```bash
source envs/bin/activate
```

### 3. 의존성 설치 확인

```powershell
pip install -r web_release/requirements.txt
```

## 🌐 Web Release 실행

### 방법 1: PowerShell 스크립트 사용 (권장)

```powershell
cd web_release
.\run_servers.ps1
```

메뉴에서 선택:
- **1**: API 서버만 실행 (포트 8000)
- **2**: Streamlit 앱만 실행 (포트 8501)
- **3**: 둘 다 백그라운드로 실행
- **4**: 서버 종료

### 방법 2: 수동 실행

#### 터미널 1: FastAPI 서버
```powershell
cd web_release
python api.py
```

#### 터미널 2: Streamlit 앱
```powershell
cd web_release
streamlit run app.py
```

## 🔗 접속 주소

- **Streamlit 앱**: http://localhost:8501
- **FastAPI 서버**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 🔐 로그인 정보

### 기본 계정
- **관리자**: `admin` / `password123`
- **학생1**: `student1` / `pass1234`
- **학생2**: `student2` / `pass5678`
- **교사**: `teacher` / `teacher2024`

### 사용자 관리

```powershell
# 사용자 추가
python manage_users.py add <username> <password> [admin|user]

# 사용자 목록 확인
python manage_users.py list

# 비밀번호 변경
python manage_users.py passwd <username> <new_password>

# 사용자 삭제
python manage_users.py remove <username>
```

## 🧪 agents_2 직접 테스트

Web UI 없이 agents_2를 직접 테스트하려면:

```powershell
# 프로젝트 루트에서
python main_gemini.py
```

또는

```python
from agents_2.orchestrator import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator(
    talk_style_dir="./GS_talk_style",
    paper_dir="./GS_paper",
    max_retries=3
)

result = orchestrator.process_query("이광수 선생님의 친일 행위에 대해 설명해주세요.")
print(result["final_answer"])
```

## 📁 디렉토리 구조

```
gayeon_mulitagent/
├── .env                     # 환경 변수 (GEMINI_API_KEY)
├── envs/                    # Python 가상환경
├── agents_2/                # 멀티 에이전트 시스템
│   ├── base_agent.py
│   ├── knowledge_agent.py
│   ├── style_agent.py
│   ├── validator_agent.py
│   └── orchestrator.py
├── GS_paper/                # 논문 데이터 + ChromaDB
│   └── chroma_db_gemini/
├── GS_talk_style/           # 말투 데이터 + ChromaDB
│   └── chroma_db_style_gemini/
├── web_release/             # 웹 인터페이스
│   ├── api.py              # FastAPI 백엔드
│   ├── app.py              # Streamlit 프론트엔드
│   ├── run_servers.ps1     # Windows 실행 스크립트
│   ├── manage_users.py     # 사용자 관리
│   └── requirements.txt
└── main_gemini.py          # CLI 테스트
```

## 🔧 경로 설정 변경 사항

### 학교 서버 → 로컬 환경

1. **agents_2/knowledge_agent.py**
   - 절대 경로 자동 변환 로직 유지
   - 상대 경로 `./GS_paper`에서 자동으로 절대 경로로 변환

2. **agents_2/style_agent.py**
   - 절대 경로 자동 변환 로직 유지
   - 상대 경로 `./GS_talk_style`에서 자동으로 절대 경로로 변환

3. **web_release/api.py**
   - 상대 경로 `../GS_talk_style`, `../GS_paper`에서 절대 경로로 변경
   - `os.path.join(base_dir, "GS_talk_style")` 형식으로 수정

## ⚠️ 주의사항

### 1. ChromaDB 초기화
첫 실행 시 ChromaDB가 자동으로 생성됩니다:
- `GS_paper/chroma_db_gemini/`
- `GS_talk_style/chroma_db_style_gemini/`

이미 생성되어 있으면 기존 DB를 사용합니다.

### 2. 포트 충돌
- FastAPI: 8000 포트
- Streamlit: 8501 포트

다른 프로그램이 해당 포트를 사용 중이면 종료하거나 포트를 변경하세요.

### 3. API 키 보안
- `.env` 파일을 Git에 커밋하지 마세요
- `.gitignore`에 `.env`가 포함되어 있는지 확인하세요

## 🐛 문제 해결

### ChromaDB 로딩 실패
```powershell
# ChromaDB 재생성
Remove-Item -Recurse -Force GS_paper\chroma_db_gemini
Remove-Item -Recurse -Force GS_talk_style\chroma_db_style_gemini
python main_gemini.py  # 재생성
```

### 포트 사용 중
```powershell
# 포트 8000을 사용하는 프로세스 확인
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
# 프로세스 종료
Stop-Process -Id <PID>
```

### 가상환경 활성화 오류
```powershell
# PowerShell 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. `.env` 파일에 유효한 GEMINI_API_KEY가 있는지
2. 가상환경이 활성화되어 있는지
3. 모든 의존성이 설치되었는지
4. ChromaDB 디렉토리가 올바르게 생성되었는지

## 🎯 다음 단계

1. Streamlit 앱 접속: http://localhost:8501
2. 로그인 (예: admin / password123)
3. 이광수 AI와 대화 시작
4. 검증 점수 확인
5. 로그 확인: `web_release/usage_logs/`
