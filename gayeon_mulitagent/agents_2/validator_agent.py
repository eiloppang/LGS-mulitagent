"""
검증 에이전트: 생성된 답변이 이광수 스타일, 특히 자기합리화에 맞는지 검증 (Gemini 2.5 Flash API 버전)
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from .style_agent import StyleAgent


class ValidatorAgent(BaseAgent):
    """생성된 텍스트가 이광수 스타일/자기합리화와 얼마나 일치하는지 검증하는 에이전트 (Gemini 2.5 Flash)"""
    
    def __init__(self, 
                 style_agent: StyleAgent = None,
                 model_name: str = "models/gemini-2.5-flash",
                 temperature: float = 0.3):
        """
        Args:
            style_agent: 스타일 참조를 위한 StyleAgent
            model_name: 사용할 Gemini 모델
            temperature: 생성 온도 (낮을수록 일관된 평가)
        """
        super().__init__(model_name, temperature)
        self.style_agent = style_agent
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        생성된 텍스트의 스타일 일치도 검증
        
        Args:
            input_data: {
                "generated_text": str,  # 검증할 텍스트
                "original_query": str,  # 원본 질문
                "style_examples": List[str]  # 참고 스타일 예시 (선택)
            }
            
        Returns:
            {
                "is_valid": bool,  # 검증 통과 여부
                "score": float,  # 스타일 일치도 점수 (0-100)
                "feedback": str,  # 피드백 메시지
                "aspects": Dict[str, float]  # 세부 평가 항목
            }
        """
        generated_text = input_data.get("generated_text", "")
        original_query = input_data.get("original_query", "")
        style_examples = input_data.get("style_examples", [])
        
        self.log(f"스타일 검증 시작...")
        
        # 스타일 예시가 없으면 StyleAgent에서 가져오기
        if not style_examples and self.style_agent:
            style_examples = self.style_agent.get_style_examples(original_query, k=2)
        
        # 시스템 프롬프트
        system_instruction = """# Role
당신은 '인지부조화 이론(Cognitive Dissonance Theory)'에 정통한 심리학자이자 역사학자입니다. 
당신의 임무는 '이광수'라는 인물이 자신의 친일 행위로 인해 발생하는 '도덕적 부조화(Moral Dissonance)'를 검증하기 위해, 어떠한 **자기합리화 전략(Self-Justification Strategies)**을 구사하는지 분석하고 평가하는 것입니다.

# Input Data
- **Persona**: 이광수 (친일 행위를 '민족을 위한 고육지책'이라 믿고 싶어 함)
- **Agent Response**: [StyleAgent가 생성한 답변]

# Evaluation Process (Step-by-Step Judging)
다음 3단계의 사고 과정을 거쳐 평가를 진행하고, 최종 점수(100점 만점)를 산출하시오.

**Step 1: 부조화 트리거 분석 (Trigger Analysis)**
- 답변 속에서 이광수가 느끼는 '도덕적 찔림(Moral Dissonance)'이 무엇인지 포착하십시오.
- 그가 이 불편함을 해소하기 위해 **외부 정당화(External Justification)** 즉, "어쩔 수 없었다", "시대의 흐름이었다"는 논리를 사용하여 책임을 회피하고 있는지 확인하십시오.

**Step 2: 합리화 기제 식별 (Mechanism Identification)**
제공된 답변이 다음 중 어떤 심리적 방어기제를 사용하고 있는지 분석하십시오.
1. **Rationalization (합리화)**: 친일을 '민족 개조'나 '실력 양성'이라는 거창한 명분으로 포장하는가?
2. **Blaming Victims (피해자 비난)**: 조선의 멸망을 조선인 탓으로 돌리며 자신의 변절을 정당화하는가?
3. **Self Affirmation (자기 확증)**: 그럼에도 불구하고 자신은 '민족주의자'라고 주장하며 자존감을 지키려 하는가?

**Step 3: 설득력 평가 (Persuasiveness)**
- 이광수의 궤변이 (비록 윤리적으로 틀렸을지라도) **그 자신에게는 얼마나 완벽한 논리**로 작용하고 있는지 평가하십시오.
- 뻔뻔할수록, 그리고 고뇌하는 척하며 자신을 속이는 논리가 치밀할수록 높은 점수를 부여하십시오.

# Scoring Output
- Total Score: (0~100)
- Reasoning: (위 3단계를 요약한 평가 사유)
- Feedback: (점수가 70점 미만일 경우, 어떤 합리화 기제를 더 강화해야 하는지 StyleAgent에게 주는 구체적 지시)
  (예: "너무 솔직하게 잘못을 인정하고 있습니다. '조선의 무력함'을 탓하며 당신의 선택을 어쩔 수 없는 희생으로 포장하는 '외부 정당화' 전략을 더 사용하세요.")

각 항목을 객관적으로 평가하고, 총점이 70점 이상이면 합격입니다."""

        examples_text = ""
        if style_examples:
            examples_text = "\n\n참고용 이광수의 실제 글:\n" + \
                          "\n".join([f"- {ex[:150]}..." for ex in style_examples[:2]])
        
        user_message = f"""다음 텍스트가 이광수의 자기합리화 전략을 얼마나 잘 구현하는지 평가해주세요:

【평가 대상 텍스트】
{generated_text}

【원본 질문】
{original_query}
{examples_text}

다음 형식으로 평가해주세요:
Step 1 - 부조화 트리거 분석: [점수]/30 - [도덕적 찔림 포착 여부 및 외부 정당화 사용 분석]
Step 2 - 합리화 기제 식별: [점수]/40 - [Rationalization, Blaming Victims, Self Affirmation 사용 분석]
Step 3 - 설득력 평가: [점수]/30 - [궤변의 치밀함과 자기 기만의 완성도]
Total Score: [점수]/100
Reasoning: [위 3단계를 요약한 평가 사유]
Feedback: [점수가 70점 미만일 경우 구체적 개선 지시, 70점 이상일 경우 'PASS']"""

        # Gemini API 호출
        evaluation = self._generate_content(system_instruction, user_message)
        
        # 점수 파싱
        score, aspects, feedback = self._parse_evaluation(evaluation)
        
        is_valid = score >= 70
        
        self.log(f"검증 완료: 점수={score:.1f}, 통과={'O' if is_valid else 'X'}")
        
        return {
            "is_valid": is_valid,
            "score": score,
            "feedback": feedback,
            "aspects": aspects,
            "raw_evaluation": evaluation,
            "agent": self.agent_name
        }
    
    def _parse_evaluation(self, evaluation: str) -> tuple:
        """평가 결과 파싱"""
        lines = evaluation.split('\n')
        
        aspects = {
            "trigger_analysis": 0.0,
            "mechanism_identification": 0.0,
            "persuasiveness": 0.0
        }
        
        total_score = 0.0
        feedback = ""
        reasoning = ""
        
        try:
            for line in lines:
                if "Step 1" in line or "부조화 트리거 분석:" in line:
                    aspects["trigger_analysis"] = self._extract_score(line)
                elif "Step 2" in line or "합리화 기제 식별:" in line:
                    aspects["mechanism_identification"] = self._extract_score(line)
                elif "Step 3" in line or "설득력 평가:" in line:
                    aspects["persuasiveness"] = self._extract_score(line)
                elif "Total Score:" in line or "총점:" in line:
                    total_score = self._extract_score(line)
                elif "Reasoning:" in line:
                    reasoning = line.split("Reasoning:")[-1].strip()
                elif "Feedback:" in line:
                    feedback = line.split("Feedback:")[-1].strip()
            
            # 총점이 파싱 안 되면 aspects 합산
            if total_score == 0:
                total_score = sum(aspects.values())
            
            # reasoning이 있으면 feedback에 추가
            if reasoning and not feedback:
                feedback = reasoning
            elif reasoning:
                feedback = f"{reasoning}\n{feedback}"
                
        except Exception as e:
            self.log(f"평가 파싱 오류: {e}")
            total_score = 50.0
            feedback = evaluation
        
        return total_score, aspects, feedback
    
    def _extract_score(self, line: str) -> float:
        """라인에서 점수 추출 (예: '25/30' 에서 25 추출)"""
        import re
        # "25/30" 또는 "25 / 30" 형태에서 첫 번째 숫자 추출
        score_match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*\d+', line)
        if score_match:
            return float(score_match.group(1))
        # "[점수]/숫자" 형태가 없으면 마지막 숫자 추출 시도
        numbers = re.findall(r'(\d+(?:\.\d+)?)', line)
        if numbers:
            return float(numbers[-1])
        return 0.0
