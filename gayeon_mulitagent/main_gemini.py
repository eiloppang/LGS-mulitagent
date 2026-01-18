"""
Gemini 2.5 Flash API를 사용한 멀티 에이전트 챗봇 테스트
"""
import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# agents_2 모듈 임포트
from agents_2.orchestrator import MultiAgentOrchestrator


def main():
    """메인 실행 함수"""
    
    # Gemini API 키 확인
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  경고: GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("export GEMINI_API_KEY='your-api-key' 를 실행하거나 .env 파일에 추가하세요.")
        return
    
    print("=" * 60)
    print("이광수 친일 챗봇 (Gemini 2.5 Flash API 버전)")
    print("=" * 60)
    print()
    
    # 오케스트레이터 초기화
    orchestrator = MultiAgentOrchestrator(
        talk_style_dir="./GS_talk_style",
        paper_dir="./GS_paper",
        max_retries=3,
        model_name="models/gemini-2.5-flash"
    )
    
    # 대화형 인터페이스 시작
    orchestrator.chat()


if __name__ == "__main__":
    main()
