"""
Gemini 임베딩을 위한 커스텀 클래스
"""
from typing import List
from google import genai
from langchain_core.embeddings import Embeddings


class GeminiEmbeddings(Embeddings):
    """Gemini API를 사용한 임베딩 클래스"""
    
    def __init__(self, model: str = "models/text-embedding-004"):
        """
        Args:
            model: 사용할 Gemini 임베딩 모델
        """
        self.client = genai.Client()
        self.model = model
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """문서 리스트를 임베딩으로 변환"""
        embeddings = []
        for text in texts:
            try:
                result = self.client.models.embed_content(
                    model=self.model,
                    contents=text  # content -> contents
                )
                embeddings.append(result.embeddings[0].values)
            except Exception as e:
                print(f"임베딩 오류: {e}")
                # 오류 시 제로 벡터 반환 (768 차원)
                embeddings.append([0.0] * 768)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """단일 쿼리를 임베딩으로 변환"""
        try:
            result = self.client.models.embed_content(
                model=self.model,
                contents=text  # content -> contents
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"쿼리 임베딩 오류: {e}")
            return [0.0] * 768
