"""
기본 에이전트 추상 클래스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


class BaseAgent(ABC):
    """모든 에이전트의 기본 클래스"""
    
    def __init__(self, model_name: str = "llama3.1", temperature: float = 0.7):
        """
        Args:
            model_name: 사용할 Ollama 모델명 (llama3.1, mistral, qwen2.5 등)
            temperature: 생성 온도 (0.0 ~ 1.0)
        """
        self.llm = ChatOllama(model=model_name, temperature=temperature)
        self.agent_name = self.__class__.__name__
        
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
    
    def _create_messages(self, system_prompt: str, user_message: str):
        """메시지 생성 헬퍼 함수"""
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
    
    def log(self, message: str):
        """로깅 헬퍼 함수"""
        print(f"[{self.agent_name}] {message}")
