"""
이광수 친일 챗봇 - 멀티 에이전트 시스템 (Ollama 버전)
메인 실행 파일
"""
import os
from dotenv import load_dotenv
from agents import MultiAgentOrchestrator

# 환경 변수 로드
load_dotenv()

def main():
    """메인 실행 함수"""
    
    # Ollama 설정
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "gemma3:4b")
    
    print("\n" + "="*60)
    print(f"Ollama 설정")
    print("="*60)
    print(f"URL: {ollama_base_url}")
    print(f"모델: {ollama_model}")
    print("="*60 + "\n")
    
    # 멀티 에이전트 오케스트레이터 초기화
    orchestrator = MultiAgentOrchestrator(
        talk_style_dir="./GS_talk_style",
        paper_dir="./GS_paper",
        max_retries=3
    )
    
    # 대화형 인터페이스 시작
    orchestrator.chat()


if __name__ == "__main__":
    main()
