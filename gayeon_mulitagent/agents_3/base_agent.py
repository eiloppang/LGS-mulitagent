"""
기본 에이전트 추상 클래스 (Ollama gemma4 버전)

LLM은 LangChain ChatOllama로 위임한다.
- gemma4의 thinking 모드는 시스템 프롬프트 앞에 <|think|> 토큰을 주입해
  활성화하며, 모델 응답에서 <|channel|>thought ... <channel|> 블록은
  제거하고 final answer만 반환한다.
"""
import os
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

# gemma4 thought 블록 제거용 정규식.
# 사용자 명세상 시작 토큰은 <|channel|>thought, 종료 토큰은 <channel|>이지만
# 비대칭이라 가능한 변형을 모두 허용한다 (<|channel|>, <|/channel|>,
# <|message|>, <|end|>). 매칭 실패 시 원문을 보존한다.
_THOUGHT_RE = re.compile(
    r"<\|channel\|>\s*thought\b[\s\S]*?(?:<\|?/?channel\|?>|<\|message\|>|<\|end\|>)",
    re.IGNORECASE,
)
# gpt-oss 계열의 analysis 채널도 같은 방식으로 제거 (혹시 모델이 흉내낼 경우)
_ANALYSIS_RE = re.compile(
    r"<\|channel\|>\s*analysis\b[\s\S]*?<\|end\|>",
    re.IGNORECASE,
)
# 잔여 특수 토큰 정리
_LEFTOVER_TOKEN_RE = re.compile(
    r"<\|(?:message|end|start|assistant|channel)\|?>",
    re.IGNORECASE,
)


class BaseAgent(ABC):
    """모든 에이전트의 기본 클래스 (Ollama gemma4)"""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        enable_thinking: bool = False,
        base_url: Optional[str] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
    ):
        """
        Args:
            model_name: 사용할 Ollama 모델명. None이면 OLLAMA_MODEL env (기본 gemma4:e4b).
            temperature: 생성 온도. None이면 OLLAMA_TEMPERATURE env (기본 1.0).
            enable_thinking: True면 시스템 프롬프트 앞에 <|think|> 토큰 주입.
                ValidatorAgent만 기본 활성. ENABLE_VALIDATOR_THINKING env로 토글.
            base_url: Ollama 서버 URL. None이면 OLLAMA_BASE_URL env.
            top_p: nucleus sampling. None이면 OLLAMA_TOP_P env (기본 0.95).
            top_k: top-k sampling. None이면 OLLAMA_TOP_K env (기본 64).
        """
        model_name = model_name or os.getenv("OLLAMA_MODEL", "gemma4:e4b")
        base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        if temperature is None:
            temperature = float(os.getenv("OLLAMA_TEMPERATURE", "1.0"))
        if top_p is None:
            top_p = float(os.getenv("OLLAMA_TOP_P", "0.95"))
        if top_k is None:
            top_k = int(os.getenv("OLLAMA_TOP_K", "64"))

        self.model_name = model_name
        self.temperature = temperature
        self.enable_thinking = enable_thinking
        self.agent_name = self.__class__.__name__

        self.client = ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
        )

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """에이전트의 주요 처리 로직."""
        pass

    def _generate_content(self, system_instruction: str, user_message: str) -> str:
        """
        Ollama(gemma4) chat 호출. agents_2의 시그니처와 동일.

        thinking이 켜져 있으면 시스템 프롬프트 맨 앞에 <|think|> 토큰을
        한 줄 추가한다. 응답에서는 <|channel|>thought...<channel|> 블록을
        제거해 final answer만 반환한다.
        """
        try:
            sys_text = system_instruction
            if self.enable_thinking:
                sys_text = f"<|think|>\n{system_instruction}"

            messages = [
                SystemMessage(content=sys_text),
                HumanMessage(content=user_message),
            ]
            response = self.client.invoke(messages)
            raw = response.content if hasattr(response, "content") else str(response)
            return self._strip_thoughts(raw)
        except Exception as e:
            self.log(f"Ollama 호출 오류: {e}")
            self.log(
                f"  → 모델 '{self.model_name}'이 Ollama 서버에 존재하는지 "
                f"확인하세요 ('ollama list' / 'ollama pull <모델>')."
            )
            return f"오류 발생: {str(e)}"

    @staticmethod
    def _strip_thoughts(text: str) -> str:
        """gemma4 thought/analysis 블록 및 잔여 특수 토큰 제거."""
        if not isinstance(text, str):
            return str(text)
        cleaned = _THOUGHT_RE.sub("", text)
        cleaned = _ANALYSIS_RE.sub("", cleaned)
        cleaned = _LEFTOVER_TOKEN_RE.sub("", cleaned)
        return cleaned.strip()

    def log(self, message: str):
        """로깅 헬퍼 함수"""
        print(f"[{self.agent_name}] {message}")
