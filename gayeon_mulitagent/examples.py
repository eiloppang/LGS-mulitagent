"""
멀티 에이전트 시스템 예제 및 테스트
"""
import os
from dotenv import load_dotenv
from agents import MultiAgentOrchestrator

# 환경 변수 로드
load_dotenv()


def example_single_query():
    """단일 질문 예제"""
    print("\n" + "="*60)
    print("예제 1: 단일 질문 처리")
    print("="*60)
    
    orchestrator = MultiAgentOrchestrator(
        talk_style_dir="./GS_talk_style",
        paper_dir="./GS_paper",
        max_retries=2
    )
    
    query = "이광수가 창씨개명을 어떻게 정당화했나요?"
    
    result = orchestrator.process_query(query, verbose=True)
    
    print(f"\n\n{'='*60}")
    print("최종 결과 요약")
    print(f"{'='*60}")
    print(f"검증 성공: {result['success']}")
    print(f"검증 점수: {result['validation_score']:.1f}/100")
    print(f"재시도 횟수: {result['retry_count']}")
    print(f"참고 출처: {len(result['knowledge_sources'])}개")
    print(f"\n최종 답변:\n{result['final_answer']}")


def example_multiple_queries():
    """여러 질문 연속 처리 예제"""
    print("\n" + "="*60)
    print("예제 2: 여러 질문 연속 처리")
    print("="*60)
    
    orchestrator = MultiAgentOrchestrator(
        talk_style_dir="./GS_talk_style",
        paper_dir="./GS_paper",
        max_retries=2
    )
    
    queries = [
        "이광수의 민족 개조론에 대해 설명해주세요.",
        "이광수가 징병제를 지지한 이유는 무엇인가요?",
    ]
    
    results = []
    for i, query in enumerate(queries, 1):
        print(f"\n\n[질문 {i}/{len(queries)}]")
        result = orchestrator.process_query(query, verbose=True)
        results.append({
            "query": query,
            "answer": result['final_answer'],
            "score": result['validation_score']
        })
    
    print(f"\n\n{'='*60}")
    print("전체 결과 요약")
    print(f"{'='*60}")
    for i, res in enumerate(results, 1):
        print(f"\n{i}. {res['query']}")
        print(f"   점수: {res['score']:.1f}/100")
        print(f"   답변: {res['answer'][:100]}...")


def example_detailed_validation():
    """상세 검증 정보 확인 예제"""
    print("\n" + "="*60)
    print("예제 3: 상세 검증 정보 확인")
    print("="*60)
    
    orchestrator = MultiAgentOrchestrator(
        talk_style_dir="./GS_talk_style",
        paper_dir="./GS_paper",
        max_retries=1
    )
    
    query = "이광수의 친일 행적에 대해 간단히 설명해주세요."
    
    result = orchestrator.process_query(query, verbose=False)
    
    print(f"\n질문: {query}")
    print(f"\n{'='*60}")
    print("검증 세부 항목")
    print(f"{'='*60}")
    
    validation = result['validation_details']
    aspects = validation['aspects']
    
    print(f"\n1. 어휘 선택:    {aspects['vocabulary']:.1f}/25")
    print(f"2. 문장 구조:    {aspects['structure']:.1f}/25")
    print(f"3. 어조와 톤:    {aspects['tone']:.1f}/25")
    print(f"4. 역사적 맥락:  {aspects['context']:.1f}/25")
    print(f"\n총점: {validation['score']:.1f}/100")
    print(f"통과 여부: {'✓ 통과' if validation['is_valid'] else '✗ 실패'}")
    
    if validation.get('feedback'):
        print(f"\n피드백:\n{validation['feedback']}")


def test_individual_agents():
    """개별 에이전트 테스트"""
    print("\n" + "="*60)
    print("예제 4: 개별 에이전트 테스트")
    print("="*60)
    
    from agents import StyleAgent, ValidatorAgent, KnowledgeAgent
    
    # 1. KnowledgeAgent 테스트
    print("\n[1] KnowledgeAgent 테스트")
    print("-" * 40)
    knowledge_agent = KnowledgeAgent(paper_dir="./GS_paper")
    
    knowledge_result = knowledge_agent.process({
        "query": "이광수의 창씨개명 논리",
        "top_k": 3
    })
    
    print(f"답변: {knowledge_result['answer'][:200]}...")
    print(f"출처: {knowledge_result['sources']}")
    
    # 2. StyleAgent 테스트
    print("\n\n[2] StyleAgent 테스트")
    print("-" * 40)
    style_agent = StyleAgent(talk_style_dir="./GS_talk_style")
    
    style_result = style_agent.process({
        "text": "창씨개명은 조선인이 일본인과 동등한 권리를 얻기 위한 방법입니다.",
        "context": "창씨개명에 대한 설명"
    })
    
    print(f"원본: 창씨개명은 조선인이 일본인과 동등한 권리를 얻기 위한 방법입니다.")
    print(f"\n스타일 변환:\n{style_result['styled_text']}")
    
    # 3. ValidatorAgent 테스트
    print("\n\n[3] ValidatorAgent 테스트")
    print("-" * 40)
    validator_agent = ValidatorAgent(style_agent=style_agent)
    
    validation_result = validator_agent.process({
        "generated_text": style_result['styled_text'],
        "original_query": "창씨개명에 대한 설명"
    })
    
    print(f"검증 점수: {validation_result['score']:.1f}/100")
    print(f"통과 여부: {validation_result['is_valid']}")
    print(f"세부 점수: {validation_result['aspects']}")


if __name__ == "__main__":
    import sys
    
    # Ollama 연결 확인은 선택사항 (기본값 사용)
    print("Ollama를 사용합니다. localhost:11434에서 실행 중인지 확인하세요.")
    
    print("\n이광수 친일 챗봇 - 멀티 에이전트 시스템 예제")
    print("="*60)
    print("\n실행할 예제를 선택하세요:")
    print("1. 단일 질문 처리")
    print("2. 여러 질문 연속 처리")
    print("3. 상세 검증 정보 확인")
    print("4. 개별 에이전트 테스트")
    print("5. 모두 실행")
    
    choice = input("\n선택 (1-5): ").strip()
    
    if choice == "1":
        example_single_query()
    elif choice == "2":
        example_multiple_queries()
    elif choice == "3":
        example_detailed_validation()
    elif choice == "4":
        test_individual_agents()
    elif choice == "5":
        test_individual_agents()
        example_single_query()
        example_detailed_validation()
    else:
        print("잘못된 선택입니다.")
