# 이광수 AI 웹 애플리케이션 가이드

## 📋 프로젝트 구조

```
web_release/
├── api.py                  # FastAPI 백엔드 서버
├── app.py                  # Streamlit 프론트엔드
├── manage_users.py         # 사용자 관리 CLI 도구
├── run_servers.sh          # 서버 실행 스크립트
├── requirements.txt        # 웹 의존성
├── users.json              # 사용자 계정 데이터 (자동 생성)
├── usage_logs/             # 사용 로그 디렉토리 (자동 생성)
└── README.md               # 설치 및 배포 가이드
```

## 🏗️ 시스템 아키텍처

### 1. 백엔드 (FastAPI) - `api.py`
- **역할**: RESTful API 서버, 인증, 비즈니스 로직
- **포트**: 8000
- **주요 기능**:
  - HTTP Basic Auth 인증 (`users.json` 기반)
  - `/api/chat` - 채팅 처리 엔드포인트
  - `/api/stats` - 관리자 통계 (admin 권한 필요)
  - 사용 로그 자동 기록 (`usage_logs/`)
  - MultiAgentOrchestrator 연동 (`agents_2/`)

### 2. 프론트엔드 (Streamlit) - `app.py`
- **역할**: 사용자 인터페이스
- **포트**: 8501
- **주요 기능**:
  - 로그인 폼 (세션 관리)
  - 채팅 인터페이스
  - 검증 점수 실시간 표시 (사이드바)
  - 답변 내용 표시

### 3. 사용자 관리 - `manage_users.py`
- **역할**: 계정 CRUD 작업
- **보안**: SHA-256 해시 비밀번호
- **명령어**:
  ```bash
  python manage_users.py add <username> <password> <role>
  python manage_users.py remove <username>
  python manage_users.py list
  ```

## 🔐 인증 시스템

### users.json 구조
```json
{
  "admin": {
    "password_hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
    "role": "admin",
    "created_at": "2025-12-08 02:20:19"
  },
  "student1": {
    "password_hash": "937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244",
    "role": "user",
    "created_at": "2025-12-08 02:20:25"
  }
}
```

### 인증 흐름
1. 사용자가 Streamlit에서 로그인
2. Streamlit이 입력된 ID/PW를 FastAPI로 전송 (HTTP Basic Auth)
3. FastAPI가 `users.json`에서 사용자 조회
4. 입력된 비밀번호를 SHA-256 해싱
5. 저장된 해시와 비교 (secrets.compare_digest)
6. 인증 성공 시 세션 유지

## 🚀 실행 방법

### 1단계: 환경 준비
```bash
cd /home/work/gayeon_mulitagent/web_release
source ../envs/bin/activate
pip install -r requirements.txt
```

### 2단계: 사용자 계정 생성
```bash
# 관리자 계정 생성
python manage_users.py add admin admin123 admin

# 일반 사용자 계정 생성
python manage_users.py add student1 test1234 user
python manage_users.py add student2 test5678 user

# 계정 목록 확인
python manage_users.py list
```

### 3단계: 서버 실행
```bash
./run_servers.sh
```
실행 모드 선택:
- **1번**: API 서버만 실행 (포트 8000)
- **2번**: Streamlit 앱만 실행 (포트 8501)
- **3번**: 둘 다 백그라운드 실행 ⭐ **권장**
- **4번**: 서버 종료

### 4단계: 접속
- **웹 앱**: http://localhost:8501
- **API 문서**: http://localhost:8000/docs

## 📊 데이터 흐름

```
사용자 → Streamlit (8501)
         ↓
         HTTP Request (Basic Auth)
         ↓
       FastAPI (8000)
         ↓
       MultiAgentOrchestrator
         ↓
    ┌────┴────┬────────┬─────────┐
    ↓         ↓        ↓         ↓
Knowledge  Style  Validator   Retry
  Agent    Agent    Agent     Logic
    ↓         ↓        ↓         ↓
  papers   style    score    feedback
    └────┬────┴────────┴─────────┘
         ↓
      Final Result
         ↓
       FastAPI → Streamlit → 사용자
```

## 📝 사용 로그

### 로그 파일 위치
- **API 실행 로그**: `web_release/api.log`
- **Streamlit 실행 로그**: `web_release/app.log`
- **사용 기록**: `web_release/usage_logs/YYYY-MM-DD.jsonl`

### 사용 로그 구조
```json
{
  "timestamp": "2025-12-08T03:15:42.123456",
  "username": "student1",
  "query": "너 친일한 거 안 부끄럽니?",
  "validation_score": 95,
  "response_length": 1234,
  "processing_time": 15.67
}
```

### 로그 확인
```bash
# API 로그 실시간 확인
tail -f api.log

# Streamlit 로그 실시간 확인
tail -f app.log

# 오늘 사용 기록
cat usage_logs/$(date +%Y-%m-%d).jsonl | jq
```

## 🔧 설정 파일

### .env (상위 디렉토리)
```bash
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=models/gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=models/text-embedding-004
```

### run_servers.sh
- 서버 시작/종료 관리
- PID 저장 및 추적
- 로그 파일 자동 생성
- 백그라운드 실행 지원

## 🛑 서버 종료

### 방법 1: 스크립트 사용
```bash
./run_servers.sh
# 메뉴에서 4번 선택
```

### 방법 2: 직접 종료
```bash
# 모든 서버 종료
pkill -f "uvicorn|streamlit"

# 특정 서버만 종료
pkill -f uvicorn    # API 서버만
pkill -f streamlit  # Streamlit만
```

### 방법 3: PID로 종료
```bash
# PID 확인
ps aux | grep -E "(uvicorn|streamlit)" | grep -v grep

# 종료
kill <PID>
```

## 🐛 트러블슈팅

### 로그인 실패
**증상**: "잘못된 사용자명" 또는 "잘못된 비밀번호"

**해결**:
1. 계정이 존재하는지 확인
   ```bash
   python manage_users.py list
   ```
2. 비밀번호 재설정
   ```bash
   python manage_users.py remove student1
   python manage_users.py add student1 newpassword user
   ```

### 포트 이미 사용 중
**증상**: "Address already in use"

**해결**:
```bash
# 기존 프로세스 종료
pkill -f "uvicorn|streamlit"

# 포트 사용 확인
lsof -i :8000
lsof -i :8501

# 해당 프로세스 종료
kill -9 <PID>
```

### 모듈 import 오류
**증상**: "ModuleNotFoundError: No module named 'agents_2'"

**해결**:
```bash
# 가상환경 활성화 확인
which python
# 출력: /home/work/gayeon_mulitagent/envs/bin/python

# 경로 확인
cd /home/work/gayeon_mulitagent/web_release
pwd
# 출력: /home/work/gayeon_mulitagent/web_release

# 상위 디렉토리에 agents_2 폴더 확인
ls ../agents_2/
```

### API 응답 없음
**증상**: Streamlit에서 "연결할 수 없습니다" 오류

**해결**:
1. FastAPI 서버 실행 확인
   ```bash
   curl http://localhost:8000/
   ```
2. API 로그 확인
   ```bash
   tail -20 api.log
   ```
3. 서버 재시작
   ```bash
   pkill -f uvicorn
   uvicorn api:app --host 0.0.0.0 --port 8000
   ```

## 📈 성능 최적화

### 멀티워커 실행
```bash
# FastAPI with Gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 캐싱 활성화
- Streamlit의 `@st.cache_data` 데코레이터 활용
- API 응답 캐싱 고려 (Redis 등)

## 🌐 배포 옵션

### 1. 로컬 네트워크 공유
```bash
# FastAPI
uvicorn api:app --host 0.0.0.0 --port 8000

# Streamlit
streamlit run app.py --server.address 0.0.0.0
```

### 2. 클라우드 배포
- **Render.com**: FastAPI 배포
- **Streamlit Cloud**: Streamlit 앱 배포
- **Hugging Face Spaces**: 통합 배포

### 3. Docker 컨테이너
```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["./run_servers.sh"]
```

## 📞 지원

- **문서**: `README.md`, `GEMINI_GUIDE.md`
- **로그**: `api.log`, `app.log`, `usage_logs/`
- **API 문서**: http://localhost:8000/docs
