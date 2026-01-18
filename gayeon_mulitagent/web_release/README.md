# 이광수 AI - Web Release

Gemini 2.5 Flash API 기반 멀티 에이전트 시스템의 웹 배포 버전입니다.

## 🚀 빠른 시작 (Windows 로컬 환경)

### 전체 가이드
자세한 설정 방법은 [LOCAL_SETUP.md](LOCAL_SETUP.md)를 참조하세요.

### 1. 환경 설정
```powershell
# .env 파일 생성 (프로젝트 루트)
GEMINI_API_KEY=your_api_key_here
```

### 2. 간편 실행 (PowerShell)
```powershell
cd web_release
.\run_servers.ps1
```

선택 메뉴:
- **1**: API 서버만 실행 (포트 8000)
- **2**: Streamlit 앱만 실행 (포트 8501)
- **3**: 둘 다 백그라운드로 실행 ⭐ 권장
- **4**: 서버 종료

### 3. 수동 실행 (선택)

#### 터미널 1: FastAPI 서버
```powershell
.\envs\Scripts\Activate.ps1
cd web_release
python api.py
```

#### 터미널 2: Streamlit 앱
```powershell
.\envs\Scripts\Activate.ps1
cd web_release
streamlit run app.py
```

### 접속 주소
- Streamlit 앱: http://localhost:8501
- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 📁 파일 구조

```
web_release/
├── api.py              # FastAPI 백엔드
├── app.py              # Streamlit 프론트엔드
├── manage_users.py     # 사용자 관리 도구
├── requirements.txt    # 의존성 패키지
├── README.md          # 이 파일
├── usage_logs/        # 사용 로그 (자동 생성)
└── users.json         # 사용자 DB (자동 생성)
```

## 🔐 인증 시스템

### 기본 계정
- **관리자**: admin / password123
- **학생1**: student1 / pass1234
- **학생2**: student2 / pass5678
- **교사**: teacher / teacher2024

### 사용자 관리 명령어

```bash
# 사용자 추가
python manage_users.py add <username> <password> [admin|user]

# 사용자 목록
python manage_users.py list

# 비밀번호 변경
python manage_users.py passwd <username> <new_password>

# 사용자 삭제
python manage_users.py remove <username>
```

## 📊 주요 기능

### 1. 실시간 대화
- 이광수 AI와 1:1 대화
- 자동 인지부조화 분석
- 검증 점수 실시간 표시

### 2. 검증 시스템
- **부조화 트리거 분석** (30점)
- **합리화 기제 식별** (40점)
- **설득력 평가** (30점)
- 총점 70점 이상 합격

### 3. 사용 로그
- 일별 로그 자동 저장
- 사용자별 통계 추적
- 관리자 대시보드

### 4. 관리자 기능
- 실시간 통계 조회
- 사용자별 평균 점수
- 성공률 모니터링

## 🔧 API 엔드포인트

### GET /
헬스 체크

### POST /api/chat
대화 요청 (인증 필요)

**Request:**
```json
{
  "query": "이광수 선생님, 친일에 대해 어떻게 생각하시나요?"
}
```

**Response:**
```json
{
  "answer": "생성된 답변...",
  "validation_score": 85.0,
  "validation_details": {...},
  "knowledge_sources": ["논문1.pdf", "논문2.pdf"],
  "retry_count": 1,
  "success": true
}
```

### GET /api/stats
통계 조회 (관리자 전용)

## 📈 배포 옵션

### Option 1: Render (추천)
```bash
# render.yaml 사용하여 자동 배포
git push origin main
```

### Option 2: 로컬 서버
```bash
# 서버에서 직접 실행
nohup python api.py > api.log 2>&1 &
nohup streamlit run app.py > app.log 2>&1 &
```

### Option 3: Docker
```bash
docker-compose up -d
```

## 🛡️ 보안 권장사항

1. **프로덕션 환경**에서는 `USERS` 딕셔너리를 데이터베이스로 교체
2. 비밀번호를 **bcrypt** 또는 **argon2**로 해싱
3. **HTTPS** 사용 (Let's Encrypt)
4. **Rate Limiting** 추가 (FastAPI-Limiter)
5. **CORS** 설정을 특정 도메인만 허용

## 📝 로그 형식

```json
{
  "timestamp": "2025-12-07T10:30:45",
  "username": "student1",
  "query": "친일 행위에 대해...",
  "score": 85.5,
  "success": true,
  "retry_count": 1
}
```

## 🐛 문제 해결

### API 연결 오류
```bash
# API 서버가 실행 중인지 확인
curl http://localhost:8000/health
```

### 임베딩 오류
```bash
# .env 파일에 API 키 확인
cat ../.env | grep GEMINI_API_KEY
```

### 로그인 실패
```bash
# 사용자 목록 확인
python manage_users.py list
```

## 📞 지원

문제가 발생하면 로그 파일을 확인하세요:
- API 로그: `api.log`
- 앱 로그: `app.log`
- 사용 로그: `usage_logs/YYYYMMDD.jsonl`

## 📄 라이선스

이 프로젝트는 학술 연구 목적으로 개발되었습니다.
