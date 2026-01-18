"""
기본 에이전트 추상 클래스 (Gemini 2.5 Flash API 버전)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from google import genai


class BaseAgent(ABC):
    """모든 에이전트의 기본 클래스 (Gemini 2.5 Flash 사용)"""
    
    def __init__(self, model_name: str = "models/gemini-2.5-flash", temperature: float = 0.7):
        """
        Args:
            model_name: 사용할 Gemini 모델명 (models/gemini-2.5-flash, models/gemini-2.5-pro 등)
            temperature: 생성 온도 (0.0 ~ 2.0)
        """
        # GEMINI_API_KEY 환경변수에서 자동으로 API 키를 가져옴
        self.client = genai.Client()
        self.model_name = model_name
        self.temperature = temperature
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
    
    def _generate_content(self, system_instruction: str, user_message: str) -> str:
        """
        Gemini API를 사용하여 콘텐츠 생성
        
        Args:
            system_instruction: 시스템 프롬프트
            user_message: 사용자 메시지
            
        Returns:
            생성된 텍스트
        """
        try:
            # Gemini 2.5 Flash API 호출
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"{system_instruction}\n\n{user_message}",
                config={
                    "temperature": self.temperature,
                }
            )
            return response.text
        except Exception as e:
            self.log(f"API 호출 오류: {e}")
            return f"오류 발생: {str(e)}"
    
    def log(self, message: str):
        """로깅 헬퍼 함수"""
        print(f"[{self.agent_name}] {message}")
