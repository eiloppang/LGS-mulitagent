"""
오케스트레이터: 멀티 에이전트 시스템을 조율하는 핵심 컴포넌트 (Gemini 2.5 Flash API 버전)
"""
import os
from typing import Dict, Any, List
from .style_agent import StyleAgent
from .validator_agent import ValidatorAgent
from .knowledge_agent import KnowledgeAgent


class MultiAgentOrchestrator:
    """
    세 개의 에이전트를 조율하여 이광수 친일 챗봇의 응답을 생성 (Gemini 2.5 Flash)
    
    워크플로우:
    1. KnowledgeAgent: 질문에 대한 지식 검색 및 초안 생성
    2. StyleAgent: 초안을 이광수 스타일로 변환
    3. ValidatorAgent: 스타일 적합성 검증
    4. 검증 실패 시 재시도 (최대 3회)
    """
    
    def __init__(self,
                 talk_style_dir: str = "./GS_talk_style",
                 paper_dir: str = "./GS_paper",
                 max_retries: int = 3,
                 model_name: str = None,
                 embedding_model: str = None):
        """
        Args:
            talk_style_dir: 말투 데이터 디렉토리
            paper_dir: 논문 데이터 디렉토리
            max_retries: 검증 실패 시 최대 재시도 횟수
            model_name: Gemini 모델 이름 (None이면 환경변수 사용)
            embedding_model: 임베딩 모델 이름 (None이면 환경변수 사용)
        """
        print("=" * 60)
        print("멀티 에이전트 시스템 초기화 중 (Gemini 2.5 Flash)...")
        print("=" * 60)
        
        # 환경 변수에서 모델 이름 가져오기
        if model_name is None:
            model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
        if embedding_model is None:
            embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
        
        print(f"\n사용 모델: {model_name}")
        print(f"임베딩 모델: {embedding_model}\n")
        
        self.knowledge_agent = KnowledgeAgent(
            paper_dir=paper_dir,
            model_name=model_name,
            embedding_model=embedding_model
        )
        self.style_agent = StyleAgent(
            talk_style_dir=talk_style_dir,
            model_name=model_name,
            embedding_model=embedding_model
        )
        self.validator_agent = ValidatorAgent(
            style_agent=self.style_agent,
            model_name=model_name
        )
        self.max_retries = max_retries
        
        print("\n✓ 모든 에이전트 초기화 완료!")
        print("=" * 60)
        
    def process_query(self, query: str, verbose: bool = True) -> Dict[str, Any]:
        """
        사용자 질문을 처리하여 최종 답변 생성
        
        Args:
            query: 사용자 질문
            verbose: 상세 로그 출력 여부
            
        Returns:
            {
                "final_answer": str,  # 최종 답변
                "validation_score": float,  # 검증 점수
                "knowledge_sources": List[str],  # 참고 출처
                "retry_count": int,  # 재시도 횟수
                "workflow_log": List[Dict]  # 처리 과정 로그
            }
        """
        workflow_log = []
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"질문: {query}")
            print(f"{'='*60}\n")
        
        # Step 1: 지식 검색 및 초안 생성
        if verbose:
            print("🔍 Step 1: 지식 검색 중...")
        
        knowledge_result = self.knowledge_agent.process({
            "query": query,
            "top_k": 5
        })
        workflow_log.append({
            "step": 1,
            "agent": "KnowledgeAgent",
            "result": knowledge_result
        })
        
        if verbose:
            print(f"   - 참고 자료: {len(knowledge_result['knowledge_items'])}개")
            print(f"   - 출처: {', '.join(knowledge_result['sources'][:3])}")
            if len(knowledge_result['sources']) > 3:
                print(f"            외 {len(knowledge_result['sources'])-3}개")
        
        draft_answer = knowledge_result['answer']
        
        # Step 2~4: 스타일 변환 및 검증 (최대 max_retries회 시도)
        retry_count = 0
        final_answer = None
        validation_result = None
        
        while retry_count < self.max_retries:
            # Step 2: 스타일 변환
            if verbose:
                if retry_count == 0:
                    print(f"\n✍️  Step 2: 이광수 스타일로 변환 중...")
                else:
                    print(f"\n🔄 재시도 {retry_count}/{self.max_retries - 1}: 스타일 재변환 중...")
            
            style_result = self.style_agent.process({
                "text": draft_answer,
                "context": query
            })
            workflow_log.append({
                "step": 2,
                "agent": "StyleAgent",
                "retry": retry_count,
                "result": style_result
            })
            
            styled_answer = style_result['styled_text']
            
            # Step 3: 검증
            if verbose:
                print(f"✅ Step 3: 스타일 검증 중...")
            
            validation_result = self.validator_agent.process({
                "generated_text": styled_answer,
                "original_query": query,
                "style_examples": style_result.get('style_examples', [])
            })
            workflow_log.append({
                "step": 3,
                "agent": "ValidatorAgent",
                "retry": retry_count,
                "result": validation_result
            })
            
            if verbose:
                print(f"   - 검증 점수: {validation_result['score']:.1f}/100")
                print(f"   - 부조화 트리거 분석: {validation_result['aspects']['trigger_analysis']:.1f}/30")
                print(f"   - 합리화 기제 식별: {validation_result['aspects']['mechanism_identification']:.1f}/40")
                print(f"   - 설득력 평가: {validation_result['aspects']['persuasiveness']:.1f}/30")
            
            # Step 4: 검증 통과 확인
            if validation_result['is_valid']:
                final_answer = styled_answer
                if verbose:
                    print(f"\n🎉 검증 통과! (시도 {retry_count + 1}회)")
                break
            else:
                if verbose:
                    print(f"   ⚠️  검증 실패 (기준: 70점)")
                    if validation_result.get('feedback'):
                        print(f"   - 피드백: {validation_result['feedback'][:100]}...")
                
                # 피드백을 반영하여 draft_answer 수정
                draft_answer = self._refine_with_feedback(
                    draft_answer,
                    styled_answer,
                    validation_result
                )
                retry_count += 1
        
        # 최대 재시도 후에도 실패하면 마지막 버전 사용
        if final_answer is None:
            final_answer = styled_answer
            if verbose:
                print(f"\n⚠️  최대 재시도 횟수 도달. 마지막 버전 사용")
        
        if verbose:
            print(f"\n{'='*60}")
            print("✨ 최종 답변 생성 완료!")
            print(f"{'='*60}\n")
        
        return {
            "final_answer": final_answer,
            "validation_score": validation_result['score'] if validation_result else 0,
            "validation_details": validation_result,
            "knowledge_sources": knowledge_result['sources'],
            "retry_count": retry_count,
            "workflow_log": workflow_log,
            "success": validation_result['is_valid'] if validation_result else False
        }
    
    def _refine_with_feedback(self,
                             original_draft: str,
                             styled_version: str,
                             validation_result: Dict[str, Any]) -> str:
        """
        검증 피드백을 바탕으로 초안을 개선
        
        이 메서드는 단순히 원본과 스타일 버전을 조합하여
        다음 시도에서 더 나은 결과를 얻도록 힌트를 제공합니다.
        """
        feedback = validation_result.get('feedback', '')
        aspects = validation_result.get('aspects', {})
        
        # 가장 낮은 점수의 항목 파악
        weak_aspect = min(aspects.items(), key=lambda x: x[1])
        
        # 개선 힌트 추가
        hint = f"\n\n[개선 필요] 특히 '{weak_aspect[0]}' 측면에서 이광수의 스타일을 더 강화해야 함. {feedback}"
        
        return original_draft + hint
    
    def chat(self):
        """대화형 인터페이스"""
        print("\n" + "="*60)
        print("이광수 친일 챗봇 (멀티 에이전트 버전 - Gemini 2.5 Flash)")
        print("="*60)
        print("질문을 입력하세요. 종료하려면 'quit' 또는 'exit'를 입력하세요.")
        print("="*60 + "\n")
        
        while True:
            try:
                query = input("\n질문> ").strip()
                
                if query.lower() in ['quit', 'exit', '종료']:
                    print("\n챗봇을 종료합니다.")
                    break
                
                if not query:
                    continue
                
                result = self.process_query(query, verbose=True)
                
                print(f"\n답변>\n{result['final_answer']}")
                print(f"\n[검증 점수: {result['validation_score']:.1f}/100]")
                print(f"[출처: {', '.join(result['knowledge_sources'][:3])}]")
                
            except KeyboardInterrupt:
                print("\n\n챗봇을 종료합니다.")
                break
            except Exception as e:
                print(f"\n오류 발생: {e}")
                continue
