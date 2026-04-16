"""
Gemini 임베딩을 위한 커스텀 클래스

주의: 2026년 기준 `text-embedding-004`는 Google API v1/v1beta 양쪽에서
404를 반환하므로 사용 불가. 후속 모델 `gemini-embedding-001`(최대 3072 dim)을
`output_dimensionality=768`로 호출해 기존 768차원 파이프라인과 호환 유지.
"""
import time
from typing import List
from google import genai
from google.genai import types
from langchain_core.embeddings import Embeddings


# 기본 차원. 기존 ChromaDB 컬렉션이 768차원으로 생성되어 있으므로 변경 시 재색인 필요
DEFAULT_OUTPUT_DIM = 768
# 503 재시도 설정
_MAX_RETRIES = 3
_BASE_BACKOFF_SEC = 1.5


def _is_transient_error(exc: Exception) -> bool:
    msg = str(exc).upper()
    return "503" in msg or "UNAVAILABLE" in msg or "429" in msg or "RESOURCE_EXHAUSTED" in msg


class GeminiEmbeddings(Embeddings):
    """Gemini API를 사용한 임베딩 클래스 (gemini-embedding-001 기반)"""

    def __init__(
        self,
        model: str = "gemini-embedding-001",
        output_dim: int = DEFAULT_OUTPUT_DIM,
    ):
        """
        Args:
            model: 사용할 Gemini 임베딩 모델 이름
            output_dim: 출력 차원 수 (기존 ChromaDB 호환을 위해 768 기본)
        """
        # 구 모델명이 env/인자로 들어오면 자동 교정 (후방 호환)
        if "text-embedding-004" in model:
            print(
                f"[GeminiEmbeddings] '{model}'은 deprecated. "
                f"'gemini-embedding-001'로 자동 교체합니다."
            )
            model = "gemini-embedding-001"

        self.client = genai.Client()
        self.model = model
        self.output_dim = output_dim
        self._config = types.EmbedContentConfig(output_dimensionality=output_dim)

    def _embed_one(self, text: str) -> List[float]:
        """단일 텍스트 임베딩. 503/429 일시 오류는 exponential backoff로 재시도."""
        last_exc: Exception = None
        for attempt in range(_MAX_RETRIES):
            try:
                result = self.client.models.embed_content(
                    model=self.model,
                    contents=text,
                    config=self._config,
                )
                return list(result.embeddings[0].values)
            except Exception as e:
                last_exc = e
                if _is_transient_error(e) and attempt < _MAX_RETRIES - 1:
                    wait = _BASE_BACKOFF_SEC * (2 ** attempt)
                    print(
                        f"[GeminiEmbeddings] 임베딩 일시 오류 "
                        f"(시도 {attempt + 1}/{_MAX_RETRIES}), {wait:.1f}s 후 재시도: "
                        f"{str(e)[:120]}"
                    )
                    time.sleep(wait)
                    continue
                break
        # 최종 실패 시 zero vector (기존 동작 유지)
        print(f"임베딩 오류: {last_exc}")
        return [0.0] * self.output_dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """문서 리스트를 임베딩으로 변환"""
        return [self._embed_one(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        """단일 쿼리를 임베딩으로 변환"""
        return self._embed_one(text)
