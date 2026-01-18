#!/bin/bash

# 이광수 AI - 서버 실행 스크립트

echo "======================================"
echo "이광수 AI - 서버 시작"
echo "======================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 가상환경 확인
if [ ! -d "../envs" ]; then
    echo -e "${RED}❌ 가상환경을 찾을 수 없습니다.${NC}"
    echo "상위 디렉토리에서 'source envs/bin/activate'를 실행하세요."
    exit 1
fi

# 환경변수 확인
if [ ! -f "../.env" ]; then
    echo -e "${RED}❌ .env 파일을 찾을 수 없습니다.${NC}"
    echo "../.env 파일에 GEMINI_API_KEY를 설정하세요."
    exit 1
fi

echo -e "${GREEN}✅ 환경 설정 확인 완료${NC}"
echo ""

# 사용자 선택
echo "실행 모드를 선택하세요:"
echo "  1) API 서버만 실행 (포트 8000)"
echo "  2) Streamlit 앱만 실행 (포트 8501)"
echo "  3) 둘 다 실행 (백그라운드)"
echo "  4) 서버 종료"
echo ""
read -p "선택 (1-4): " choice

case $choice in
    1)
        echo -e "${YELLOW}🚀 FastAPI 서버 시작...${NC}"
        cd /home/work/gayeon_mulitagent
        source envs/bin/activate
        cd web_release
        python api.py
        ;;
    2)
        echo -e "${YELLOW}🚀 Streamlit 앱 시작...${NC}"
        cd /home/work/gayeon_mulitagent
        source envs/bin/activate
        cd web_release
        streamlit run app.py
        ;;
    3)
        echo -e "${YELLOW}🚀 서버들을 백그라운드로 시작...${NC}"
        cd /home/work/gayeon_mulitagent
        source envs/bin/activate
        cd web_release
        
        # API 서버 시작
        nohup python api.py > api.log 2>&1 &
        API_PID=$!
        echo $API_PID > api.pid
        echo -e "${GREEN}✅ FastAPI 서버 시작 (PID: $API_PID)${NC}"
        echo "   로그: web_release/api.log"
        echo "   URL: http://localhost:8000"
        
        # 잠시 대기
        sleep 3
        
        # Streamlit 앱 시작
        nohup streamlit run app.py > app.log 2>&1 &
        APP_PID=$!
        echo $APP_PID > app.pid
        echo -e "${GREEN}✅ Streamlit 앱 시작 (PID: $APP_PID)${NC}"
        echo "   로그: web_release/app.log"
        echo "   URL: http://localhost:8501"
        
        echo ""
        echo -e "${GREEN}======================================"
        echo "🎉 모든 서버가 시작되었습니다!"
        echo "======================================"
        echo -e "${NC}"
        echo "서버를 종료하려면:"
        echo "  ./run_servers.sh 선택 후 4번"
        ;;
    4)
        echo -e "${YELLOW}🛑 서버 종료 중...${NC}"
        
        if [ -f "api.pid" ]; then
            API_PID=$(cat api.pid)
            kill $API_PID 2>/dev/null
            rm api.pid
            echo -e "${GREEN}✅ FastAPI 서버 종료 (PID: $API_PID)${NC}"
        fi
        
        if [ -f "app.pid" ]; then
            APP_PID=$(cat app.pid)
            kill $APP_PID 2>/dev/null
            rm app.pid
            echo -e "${GREEN}✅ Streamlit 앱 종료 (PID: $APP_PID)${NC}"
        fi
        
        echo -e "${GREEN}✅ 모든 서버가 종료되었습니다.${NC}"
        ;;
    *)
        echo -e "${RED}❌ 잘못된 선택입니다.${NC}"
        exit 1
        ;;
esac
