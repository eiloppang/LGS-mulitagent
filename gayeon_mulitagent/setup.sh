#!/bin/bash

# 이광수 친일 챗봇 - 가상환경 설치 스크립트 (A100 GPU 최적화)

set -e  # 오류 발생 시 중단

echo "=========================================="
echo "이광수 친일 챗봇 설치 시작"
echo "GPU: NVIDIA A100 40GB"
echo "=========================================="
echo ""

# 현재 디렉토리 확인
cd /home/work/gayeon_mulitagent

# 1. 가상환경 생성
echo "🔨 [1/5] 가상환경 생성 중..."
if [ -d "envs" ]; then
    echo "   ⚠️  기존 envs 폴더가 있습니다. 삭제하고 새로 만들까요? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        rm -rf envs
        python -m venv envs
        echo "   ✓ 가상환경 재생성 완료"
    else
        echo "   ⏭️  기존 가상환경 사용"
    fi
else
    python -m venv envs
    echo "   ✓ 가상환경 생성 완료"
fi

# 가상환경 활성화
source envs/bin/activate
echo "   ✓ 가상환경 활성화: $(which python)"
echo ""

# 2. pip 업그레이드
echo "📦 [2/5] pip 업그레이드 중..."
pip install --upgrade pip -q
echo "   ✓ pip 업그레이드 완료"
echo ""

# 3. 패키지 설치
echo "📥 [3/5] 패키지 설치 중..."
pip install -r requirements.txt
echo "   ✓ 패키지 설치 완료"
echo ""

# 4. Ollama 확인
echo "🔍 [4/5] Ollama 상태 확인 중..."
if command -v ollama &> /dev/null; then
    echo "   ✓ Ollama 설치 확인됨"
    
    # Ollama 실행 확인
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "   ✓ Ollama 서버 실행 중"
    else
        echo "   ⚠️  Ollama 서버가 실행되지 않음"
        echo "   📌 다른 터미널에서 'ollama serve' 실행 필요"
    fi
else
    echo "   ❌ Ollama가 설치되지 않음"
    echo "   📌 설치 방법: curl -fsSL https://ollama.com/install.sh | sh"
fi
echo ""

# 5. 모델 다운로드 제안
echo "🤖 [5/5] 모델 다운로드 안내"
echo ""
echo "A100 40GB GPU를 위한 추천 모델:"
echo ""
echo "추천 1) qwen2.5:32b (한국어 최강, 18GB)"
echo "  ollama pull qwen2.5:32b"
echo ""
echo "추천 2) llama3.1:70b (최고 품질, 40GB)"
echo "  ollama pull llama3.1:70b"
echo ""
echo "필수) 임베딩 모델 (274MB)"
echo "  ollama pull nomic-embed-text"
echo ""
echo "지금 다운로드하시겠습니까? (1/2/n)"
echo "1: qwen2.5:32b (추천)"
echo "2: llama3.1:70b"
echo "n: 나중에 수동으로"
read -r choice

if [ "$choice" = "1" ]; then
    echo "📥 qwen2.5:32b 다운로드 중... (약 18GB, 시간 소요)"
    ollama pull qwen2.5:32b
    ollama pull nomic-embed-text
    MODEL="qwen2.5:32b"
    echo "   ✓ 모델 다운로드 완료"
elif [ "$choice" = "2" ]; then
    echo "📥 llama3.1:70b 다운로드 중... (약 40GB, 시간 소요)"
    ollama pull llama3.1:70b
    ollama pull nomic-embed-text
    MODEL="llama3.1:70b"
    echo "   ✓ 모델 다운로드 완료"
else
    MODEL="llama3.1"
    echo "   ⏭️  모델 다운로드 건너뜀"
fi
echo ""

# 6. 환경 변수 파일 생성
echo "⚙️  환경 변수 설정 중..."
cat > .env << EOF
# Ollama 설정
OLLAMA_BASE_URL=http://localhost:11434

# 사용할 모델 (A100 40GB 최적화)
OLLAMA_MODEL=$MODEL

# 임베딩 모델
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
EOF
echo "   ✓ .env 파일 생성 완료"
echo ""

# 완료 메시지
echo "=========================================="
echo "✅ 설치 완료!"
echo "=========================================="
echo ""
echo "📋 다음 단계:"
echo ""
echo "1. Ollama 서버가 실행 중인지 확인:"
echo "   새 터미널에서: ollama serve"
echo ""
echo "2. 가상환경 활성화 (새 터미널을 열 때마다):"
echo "   source envs/bin/activate"
echo ""
echo "3. 프로그램 실행:"
echo "   python main.py"
echo ""
echo "4. 예제 실행:"
echo "   python examples.py"
echo ""
echo "=========================================="
echo "📚 문서 참고:"
echo "  - GPU_SETUP.md: A100 최적화 가이드"
echo "  - QUICKSTART.md: 빠른 시작"
echo "  - OLLAMA_SETUP.md: Ollama 상세 가이드"
echo "=========================================="
