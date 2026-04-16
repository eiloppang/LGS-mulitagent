"""
기본 에이전트 추상 클래스 (Gemini 2.5 Flash API 버전)
"""
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from google import genai


# LLM 503/429 재시도 설정
_MAX_RETRIES = 3
_BASE_BACKOFF_SEC = 1.5


def _is_transient_error(exc: Exception) -> bool:
    msg = str(exc).upper()
    return (
        "503" in msg
        or "UNAVAILABLE" in msg
        or "429" in msg
        or "RESOURCE_EXHAUSTED" in msg
        or "DEADLINE_EXCEEDED" in msg
    )


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
        Gemini API를 사용하여 콘텐츠 생성.
        503/429 등 일시적 서버 오류는 exponential backoff로 재시도.

        Args:
            system_instruction: 시스템 프롬프트
            user_message: 사용자 메시지

        Returns:
            생성된 텍스트
        """
        last_exc: Optional[Exception] = None
        for attempt in range(_MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=f"{system_instruction}\n\n{user_message}",
                    config={
                        "temperature": self.temperature,
                    }
                )
                return response.text
            except Exception as e:
                last_exc = e
                if _is_transient_error(e) and attempt < _MAX_RETRIES - 1:
                    wait = _BASE_BACKOFF_SEC * (2 ** attempt)
                    self.log(
                        f"LLM 일시 오류 (시도 {attempt + 1}/{_MAX_RETRIES}), "
                        f"{wait:.1f}s 후 재시도: {str(e)[:120]}"
                    )
                    time.sleep(wait)
                    continue
                break

        self.log(f"API 호출 오류: {last_exc}")
        return f"오류 발생: {str(last_exc)}"

    def log(self, message: str):
        """로깅 헬퍼 함수"""
        print(f"[{self.agent_name}] {message}")
