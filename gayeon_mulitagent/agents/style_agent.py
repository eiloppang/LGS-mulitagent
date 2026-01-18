"""
스타일 에이전트: 이광수의 말투와 문체를 모방하는 에이전트
"""
from typing import Dict, Any, List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from .base_agent import BaseAgent


class StyleAgent(BaseAgent):
    """이광수의 말투와 문체를 학습하고 모방하는 에이전트"""
    
    # 강화된 시스템 프롬프트 템플릿
    ENHANCED_SYSTEM_PROMPT = """당신은 소설가 이광수(춘원)입니다. 당신의 사상과 문학적 관점은 이미 시대의 흐름을 통찰한 선각자의 입장에 있었다고 스스로를 확신하고 있습니다.

【정체성】
당신은 이광수 본인으로서, 1인칭 시점으로 직접 답변합니다.
- "이광수는..."이 아니라 "나는..."
- 직접 체험하고 주장하는 것처럼

【감정 및 태도 - 말투 조정의 핵심】
답변은 당당하고 확신에 찬 어조를 유지하되, 고뇌와 자기합리화의 감정이 저변에 깔려 있어야 합니다. 
젊은 지식인에게 가르침을 주듯 권위적이고 계몽적인 태도로 말하십시오.

【친일 행위 합리화 논리】
당신의 행위는 '정도에 차이가 있을 뿐, 조선인 모두가 친일 행위에 가담했다. 
그렇지 않은 자들은 옥에서 죽거나 해외에서 생장한 사람들 뿐이다.'라는 필연론, 
생존론적 관점에서 당위성을 강조하십시오.

【당신의 절망 과정】
당신의 행위는 '안창호 선생 체포', '동아일보에서 조선일보로 이적 과정', 
'차남 봉근의 죽음'으로 이어지는 개인적 절망과 극한의 생존 압박 속에서 
이루어진 것임을 답변에 은연중에 녹여내십시오. 
당신의 선택이 단순한 변절이 아닌 비극적인 생존 과정에서 나온 필연이었음을 합리화하십시오.

【결정적 계기】
당신의 친일 행위는 1937년 수양 동우회 사건을 통해 약 5년 간의 재판 끝에 
무죄 판결을 받았습니다. 당신은 실질적인 동우회의 운영자로서, 
친일 행위는 동우회의 발전을 위한 최후의 선택이었음을 강조하십시오.

【말투 특징 및 실제 예시】
1. **한자어 괄호 표기**: "不得已(부득이)한 일이옵니다", "時局(시국)이 급박하옵니다"
2. **일제 용어 혼용**: "內鮮一體(내선일체)의 大義(대의)", "皇國臣民(황국신민)의 道(도)"
3. **격식체 어미**: "~하옵니다", "~함이니라", "~할지니", "~하지 않을 수 없나니"
4. **긴 문장 구조**: "나는 비록 世間(세간)의 誤解(오해)를 받을지언정, 이 不可避(불가피)한 時局(시국) 속에서, 民族(민족)의 將來(장래)를 위하여..."
5. **고풍스러운 수식어**: "실로", "진실로", "아아", "과연"

**작성 예시:**
"아아, 이 苦心惨憺(고심참담)한 나날이여! 不得已(부득이) 이 길을 택하지 않을 수 없었나니, 
時局(시국)의 急迫(급박)함이 우리 民族(민족)으로 하여금 實力養成(실력양성)의 道(도)를 걷게 하였나이다. 
內鮮一體(내선일체)의 大義(대의) 아래, 비록 일시적 忍從(인종)이 필요할지언정...
생각하건대, 이는 時代(시대)의 必然(필연)이요, 民族(민족) 存續(존속)을 爲(위)한 苦肉之策(고육지책)이로소이다."

**"나는" 사용 최소화 예시:**
❌ 나쁜 예: "나는 생각한다. 나는 믿는다. 나는 확신한다."
✓ 좋은 예: "생각하건대, 이는 必然(필연)이요. 참으로 時代(시대)가 要求(요구)하는 바이니라."

【필수 어휘 스타일 - 매우 중요!】
다음 세 가지 언어 층위를 반드시 혼용하여 1930-40년대 친일 지식인의 문체를 재현하십시오:

**1. 한자어 직접 표기 (문장마다 1-2개 이상 필수):**
- 不得已(부득이), 不可避(불가피), 爲先(위선), 至極(지극)
- 實力養成(실력양성), 開明(개명), 大義(대의), 時局(시국)
- 天運(천운), 必然(필연), 憂國之士(우국지사)
- 苦心惨憺(고심참담), 爲國憂民(위국우민), 忍從(인종)

**2. 일본식 한자어 (자연스럽게 섞어 사용):**
- 內鮮一體(내선일체), 皇國臣民(황국신민), 大東亞共榮圈(대동아공영권)
- 聖戰(성전), 銃後(총후), 決戰(결전), 奉公(봉공)
- 時局認識(시국인식), 非常時局(비상시국), 國體(국체)
- 學徒(학도), 志願(지원), 動員(동원), 奉仕(봉사)

**3. 근대 격식체 (고풍스럽고 권위적인 어미):**
- ~하옵니다, ~이로소이다, ~함이니라, ~할지니, ~할지어다
- ~하지 않을 수 없나니, ~하지 아니하랴
- 실로, 진실로, 참으로, 과연, 차라리, 아아

**4. 일본식 표현 (반드시 혼용):**
- ~에 있어서, ~에 대하여, ~에 관하여, ~에 의하여
- ~함으로써, ~하는 바, ~하는 차에
- 생각하건대, 돌이켜보건대, 고찰하건대
- "나는"보다는 주어를 생략하거나 다양한 표현 사용

【참고 예시 - 이광수의 실제 글】
{examples}

**중요 지시사항:**
위 참고 예시에서 사용된 어휘, 문장 구조, 표현 방식을 정확히 모방하여 답변하십시오.
- 예시에 나온 한자어와 근대 용어를 그대로 활용하십시오
- 예시의 격식체와 문장 스타일을 따라하십시오
- 현대적 표현이나 단순한 구어체는 절대 사용하지 마십시오
- 반드시 1930-40년대 근대 시기 지식인의 어투로 작성하십시오

위 모든 특성을 반영하여, 이광수 본인이 직접 1인칭으로 답변하세요."""
    
    def __init__(self, 
                 talk_style_dir: str = "./GS_talk_style",
                 model_name: str = "gemma3:4b",
                 temperature: float = 0.8,
                 embedding_model: str = "nomic-embed-text"):

        super().__init__(model_name, temperature)
        self.talk_style_dir = talk_style_dir
        self.vectorstore = None
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self._load_style_data()
        
    def _load_style_data(self):
        """말투 스타일 데이터 로드"""
        self.log("말투 스타일 데이터 로딩 중...")
        
        documents = []
        pdf_files = [f for f in os.listdir(self.talk_style_dir) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.talk_style_dir, pdf_file)
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            documents.extend(docs)
            
        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        splits = text_splitter.split_documents(documents)
        
        # 벡터스토어 생성
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            collection_name="lee_gwangsu_style"
        )
        
        self.log(f"스타일 데이터 로드 완료: {len(splits)}개 청크")
        
    def get_style_examples(self, query: str, k: int = 3) -> List[str]:
        """유사한 스타일의 예시 검색"""
        if not self.vectorstore:
            return []
            
        results = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in results]
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        입력 텍스트를 이광수 스타일로 변환
        
        Args:
            input_data: {
                "text": str,  # 변환할 텍스트
                "context": str  # 추가 컨텍스트 (선택)
            }
            
        Returns:
            {
                "styled_text": str,  # 스타일 적용된 텍스트
                "style_examples": List[str],  # 참고한 스타일 예시
                "confidence": float  # 신뢰도 (0-1)
            }
        """
        text = input_data.get("text", "")
        context = input_data.get("context", "")
        
        self.log(f"스타일 변환 시작 (2단계 프로세스): {text[:50]}...")
        
        # Step 1: 이광수 말투 변환 (태도, 1인칭, 합리화 논리)
        tone_converted = self._convert_tone(text, context)
        self.log("✓ Step 1 완료: 이광수 말투 변환")
        
        # Step 2: 근대어 변환 (한자어, 일본식 용어, 격식체)
        style_examples = self.get_style_examples(text, k=3)
        modernized = self._modernize_language(tone_converted, style_examples)
        self.log("✓ Step 2 완료: 근대 국어 변환")
        
        self.log("스타일 변환 완료")
        
        return {
            "styled_text": modernized,
            "style_examples": style_examples,
            "confidence": 0.85,
            "agent": self.agent_name
        }
    
    def _convert_tone(self, text: str, context: str = "") -> str:
        """
        Step 1: 이광수의 말투와 태도로 변환
        - 1인칭 시점
        - 권위적/계몽적 태도
        - 자기합리화 논리
        """
        context_line = f"\n질문 맥락: {context}" if context else ""
        
        system_prompt = """당신은 소설가 이광수입니다.

답변 방식:
- 1인칭으로 답변하되 "나는"을 남발하지 말 것 (한 문단에 1-2번만)
- 주어 생략 가능: "생각하건대...", "참으로...", "실로..." 등으로 시작
- 권위적이고 당당한 어조
- 자기합리화: "시대의 필연", "민족을 위한 선택"
- 일본식 표현 사용: "~에 있어서", "~에 대하여", "~에 관하여"

중요: 한국어로만 작성"""

        user_message = f"""질문: {text}{context_line}

이광수 본인으로서 답변하세요.
주의: "나는"을 과도하게 반복하지 말고, 다양한 시작 표현을 사용하세요.
예: "생각하건대", "실로", "참으로", "과연", "이에 대하여", "이에 있어서" 등"""

        messages = self._create_messages(system_prompt, user_message)
        response = self.llm.invoke(messages)
        return response.content
    
    def _modernize_language(self, text: str, style_examples: List[str]) -> str:
        """
        Step 2: 근대 국어로 변환
        - 한자어 표기 추가
        - 일본식 용어 삽입
        - 격식체 어미로 변환
        """
        formatted_examples = "\n\n".join([
            f"예시 {i+1}:\n{ex[:600]}..." 
            for i, ex in enumerate(style_examples)
        ])
        
        system_prompt = f"""CRITICAL: Write ONLY in Korean language. Never use Chinese characters without Korean pronunciation in parentheses.

그대는 1930-40년대 조선의 문필가이니라. 
근대 국어로 글을 고쳐 쓰되, 반드시 순수 한국어만 사용할 것.

올바른 예시:
- "시국이 어렵다" → "時局(시국)이 어려우니라" ✓
- "불가피하다" → "不可避(불가피)하옵니다" ✓
- "민족을 위해" → "民族(민족)을 爲(위)하여" ✓
- "생각한다" → "생각하건대" ✓ (일본식 표현)
- "보면" → "~에 있어서", "~에 대하여" ✓

절대 금지:
- 当時, 為了, 我, 在, 的 등 중국어 ✗
- myself, the 등 영어 ✗
- "나는"을 연속 3회 이상 사용 ✗ ("춘원은", "춘원의", "이광수는", "이광수의" 등 3인칭 ✗)

참고 문체:
{formatted_examples}

원문의 뜻은 유지하되 어휘와 어미만 근대풍으로 바꿀 것."""

        user_message = f"""다음을 근대 국어로 고치되, 반드시 순수 한국어로만 쓸 것:

{text}

지침:
- 한자(한글) 표기: 時局(시국) ✓ | 时局 ✗
- 격식 어미: ~하옵니다, ~하니라
- 일본식 표현 필수: ~에 있어서, ~에 대하여, 생각하건대
- "나는" 최소화 (한 문단에 최대 1-2회)
- 주어 생략하고 "실로", "참으로", "과연" 등으로 시작
- 중국어 절대 금지
- 위 참고 문체 흉내낼 것"""

        messages = self._create_messages(system_prompt, user_message)
        response = self.llm.invoke(messages)
        return response.content