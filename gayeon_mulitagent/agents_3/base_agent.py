"""
기본 에이전트 추상 클래스 (Ollama gemma4 버전 - 스켈레톤)

LLM만 ChatOllama로 교체한 1차 스켈레톤입니다.
thinking 토글, thought 블록 파싱 등의 부가 기능은 후속 커밋에서 추가합니다.
"""
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage


class BaseAgent(ABC):
    """모든 에이전트의 기본 클래스 (Ollama gemma4)"""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        base_url: Optional[str] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
    ):
        """
        Args:
            model_name: 사용할 Ollama 모델명. None이면 OLLAMA_MODEL env를 따름.
            temperature: 생성 온도. None이면 OLLAMA_TEMPERATURE env (기본 1.0).
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
        """
        에이전트의 주요 처리 로직

        Args:
            input_data: 입력 데이터

        Returns:
            처리 결과
        """
        pass

    def _generate_content(self, system_instruction: str, user_message: str) -> str:
        """
        Ollama(gemma4) chat 호출. agents_2의 시그니처와 동일하게 유지.

        Args:
            system_instruction: 시스템 프롬프트
            user_message: 사용자 메시지

        Returns:
            생성된 텍스트
        """
        try:
            messages = [
                SystemMessage(content=system_instruction),
                HumanMessage(content=user_message),
            ]
            response = self.client.invoke(messages)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            self.log(f"Ollama 호출 오류: {e}")
            return f"오류 발생: {str(e)}"

    def log(self, message: str):
        """로깅 헬퍼 함수"""
        print(f"[{self.agent_name}] {message}")
