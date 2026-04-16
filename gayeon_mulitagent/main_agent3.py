"""
Ollama(gemma4 e4b) 기반 멀티 에이전트 챗봇 실행 (agents_3)
"""
import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# agents_3 모듈 임포트 (ChatOllama 기반 LLM)
from agents_3.orchestrator import MultiAgentOrchestrator


def main():
    """메인 실행 함수"""

    # agents_3도 임베딩에는 Gemini API를 사용하므로 GEMINI_API_KEY가 필요
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  경고: GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   agents_3는 임베딩에 Gemini text-embedding-004를 사용합니다.")
        print("   export GEMINI_API_KEY='your-api-key' 또는 .env 파일에 추가하세요.")
        return

    print("=" * 60)
    print("이광수 친일 챗봇 (Ollama gemma4 e4b 버전)")
    print("=" * 60)
    print()

    # 오케스트레이터 초기화
    # model_name을 명시하지 않아 OLLAMA_MODEL 환경변수가 사용됨
    orchestrator = MultiAgentOrchestrator(
        talk_style_dir="./GS_talk_style",
        paper_dir="./GS_paper",
        max_retries=3,
    )

    # 대화형 인터페이스 시작
    orchestrator.chat()


if __name__ == "__main__":
    main()
