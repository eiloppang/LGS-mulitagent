"""
간단한 테스트 스크립트
실제 API 호출 없이 시스템 구조 확인
"""

def test_structure():
    """프로젝트 구조 테스트"""
    import os
    
    print("="*60)
    print("프로젝트 구조 확인")
    print("="*60)
    
    # 필수 디렉토리 확인
    required_dirs = [
        "./agents",
        "./GS_paper",
        "./GS_talk_style"
    ]
    
    print("\n[필수 디렉토리 확인]")
    for dir_path in required_dirs:
        exists = os.path.exists(dir_path)
        status = "✓" if exists else "✗"
        print(f"{status} {dir_path}")
    
    # 필수 파일 확인
    required_files = [
        "./agents/__init__.py",
        "./agents/base_agent.py",
        "./agents/style_agent.py",
        "./agents/validator_agent.py",
        "./agents/knowledge_agent.py",
        "./agents/orchestrator.py",
        "./main.py",
        "./examples.py",
        "./requirements.txt"
    ]
    
    print("\n[필수 파일 확인]")
    for file_path in required_files:
        exists = os.path.exists(file_path)
        status = "✓" if exists else "✗"
        print(f"{status} {file_path}")
    
    # PDF 파일 확인
    print("\n[데이터 파일 확인]")
    
    if os.path.exists("./GS_paper"):
        paper_pdfs = [f for f in os.listdir("./GS_paper") if f.endswith('.pdf')]
        print(f"✓ GS_paper: {len(paper_pdfs)}개 논문")
    else:
        print("✗ GS_paper 디렉토리 없음")
    
    if os.path.exists("./GS_talk_style"):
        style_pdfs = [f for f in os.listdir("./GS_talk_style") if f.endswith('.pdf')]
        print(f"✓ GS_talk_style: {len(style_pdfs)}개 원문")
    else:
        print("✗ GS_talk_style 디렉토리 없음")


def test_imports():
    """모듈 임포트 테스트"""
    print("\n" + "="*60)
    print("모듈 임포트 테스트")
    print("="*60 + "\n")
    
    try:
        from agents import base_agent
        print("✓ base_agent 임포트 성공")
    except Exception as e:
        print(f"✗ base_agent 임포트 실패: {e}")
    
    try:
        from agents import style_agent
        print("✓ style_agent 임포트 성공")
    except Exception as e:
        print(f"✗ style_agent 임포트 실패: {e}")
    
    try:
        from agents import validator_agent
        print("✓ validator_agent 임포트 성공")
    except Exception as e:
        print(f"✗ validator_agent 임포트 실패: {e}")
    
    try:
        from agents import knowledge_agent
        print("✓ knowledge_agent 임포트 성공")
    except Exception as e:
        print(f"✗ knowledge_agent 임포트 실패: {e}")
    
    try:
        from agents import orchestrator
        print("✓ orchestrator 임포트 성공")
    except Exception as e:
        print(f"✗ orchestrator 임포트 실패: {e}")
    
    try:
        from agents import MultiAgentOrchestrator
        print("✓ MultiAgentOrchestrator 클래스 임포트 성공")
    except Exception as e:
        print(f"✗ MultiAgentOrchestrator 클래스 임포트 실패: {e}")


def show_architecture():
    """아키텍처 다이어그램 출력"""
    print("\n" + "="*60)
    print("멀티 에이전트 시스템 아키텍처")
    print("="*60 + "\n")
    
    diagram = """
    사용자 질문 입력
         │
         ▼
    ┌────────────────────────────────────────┐
    │   MultiAgentOrchestrator (조율자)     │
    │                                        │
    │  워크플로우 관리 및 에이전트 조율     │
    └────────────────────────────────────────┘
         │
         │ Step 1: 지식 검색
         ▼
    ┌────────────────────────────────────────┐
    │   KnowledgeAgent (지식 에이전트)      │
    │                                        │
    │  • GS_paper 논문에서 검색             │
    │  • RAG 기반 답변 초안 생성            │
    │  • 출처 정보 제공                     │
    └────────────────────────────────────────┘
         │
         │ Step 2: 스타일 변환
         ▼
    ┌────────────────────────────────────────┐
    │   StyleAgent (스타일 에이전트)        │
    │                                        │
    │  • GS_talk_style 원문 학습           │
    │  • 이광수 말투로 변환                 │
    │  • Few-shot 학습 적용                │
    └────────────────────────────────────────┘
         │
         │ Step 3: 검증
         ▼
    ┌────────────────────────────────────────┐
    │   ValidatorAgent (검증 에이전트)      │
    │                                        │
    │  • 4가지 기준으로 평가                │
    │    - 어휘 선택 (25점)                 │
    │    - 문장 구조 (25점)                 │
    │    - 어조와 톤 (25점)                 │
    │    - 역사적 맥락 (25점)               │
    │  • 70점 이상 통과                     │
    └────────────────────────────────────────┘
         │
         │ 검증 통과?
         ├─ Yes → 최종 답변 반환
         │
         └─ No → Step 2로 재시도 (최대 3회)
    
    
    📊 데이터 흐름:
    
    GS_paper/ (논문 12개)
         │
         ├─→ KnowledgeAgent
         │        │
         │        ▼
         │   벡터 DB (Chroma)
         │        │
         │        ▼
         │   지식 검색 결과
         │
         ▼
    최종 답변 ← StyleAgent ← GS_talk_style/ (원문 8개)
                   ▲              │
                   │              ▼
                   │         벡터 DB (Chroma)
                   │              │
                   │              ▼
                   └─ ValidatorAgent (검증)
    """
    
    print(diagram)


if __name__ == "__main__":
    test_structure()
    test_imports()
    show_architecture()
    
    print("\n" + "="*60)
    print("테스트 완료!")
    print("="*60)
    print("\n다음 단계:")
    print("1. .env 파일에 OPENAI_API_KEY 설정")
    print("2. pip install -r requirements.txt 실행")
    print("3. python main.py 또는 python examples.py 실행")
