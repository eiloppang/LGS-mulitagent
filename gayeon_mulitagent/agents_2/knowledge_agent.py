"""
지식 에이전트: 논문에서 이광수 관련 지식을 검색하고 제공 (Gemini 2.5 Flash API 버전)
"""
from typing import Dict, Any, List
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from .base_agent import BaseAgent
from .gemini_embeddings import GeminiEmbeddings


class KnowledgeAgent(BaseAgent):
    """논문 데이터베이스에서 이광수 관련 지식을 검색하고 제공하는 에이전트 (Gemini 2.5 Flash)"""
    
    def __init__(self,
                 paper_dir: str = "./GS_paper",
                 model_name: str = "models/gemini-2.5-flash",
                 temperature: float = 0.5,
                 embedding_model: str = "models/text-embedding-004"):
        """
        Args:
            paper_dir: 논문 PDF가 있는 디렉토리
            model_name: 사용할 Gemini 모델
            temperature: 생성 온도
            embedding_model: 임베딩용 Gemini 모델
        """
        super().__init__(model_name, temperature)
        self.paper_dir = paper_dir
        self.vectorstore = None
        self.embeddings = GeminiEmbeddings(model=embedding_model)
        self._load_papers()
        
    def _load_papers(self):
        """논문 데이터 로드 (기존 벡터 DB 사용)"""
        # 상대 경로를 절대 경로로 변환
        if not os.path.isabs(self.paper_dir):
            # 현재 파일 기준으로 상위 디렉토리로 이동
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            abs_paper_dir = os.path.join(base_dir, self.paper_dir.lstrip('./'))
        else:
            abs_paper_dir = self.paper_dir
            
        persist_directory = os.path.join(abs_paper_dir, "chroma_db_gemini")
        
        # 기존 벡터스토어가 있으면 로드
        if os.path.exists(persist_directory):
            self.log(f"기존 벡터스토어 로드 중... ({persist_directory})")
            try:
                self.vectorstore = Chroma(
                    persist_directory=persist_directory,
                    embedding_function=self.embeddings,
                    collection_name="lee_gwangsu_papers_gemini"
                )
                self.log("벡터스토어 로드 완료 (기존 DB 사용)")
                return
            except Exception as e:
                self.log(f"기존 DB 로드 실패, 새로 생성합니다: {e}")
        
        # 새로 생성
        self.log("논문 데이터 로딩 중...")
        
        documents = []
        pdf_files = [f for f in os.listdir(self.paper_dir) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.paper_dir, pdf_file)
            try:
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                # 메타데이터에 파일명 추가
                for doc in docs:
                    doc.metadata['source_file'] = pdf_file
                documents.extend(docs)
                self.log(f"  - {pdf_file} 로드 완료")
            except Exception as e:
                self.log(f"  - {pdf_file} 로드 실패: {e}")
        
        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        splits = text_splitter.split_documents(documents)
        
        # 벡터스토어 생성 및 저장
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            collection_name="lee_gwangsu_papers_gemini",
            persist_directory=persist_directory
        )
        
        self.log(f"논문 데이터 로드 완료: {len(pdf_files)}개 논문, {len(splits)}개 청크 (캐시 생성)")
        
    def search_knowledge(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """지식 검색"""
        if not self.vectorstore:
            return []
        
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        
        knowledge_items = []
        for doc, score in results:
            knowledge_items.append({
                "content": doc.page_content,
                "source": doc.metadata.get('source_file', 'Unknown'),
                "page": doc.metadata.get('page', 'Unknown'),
                "relevance_score": float(1 - score)  # 거리를 유사도로 변환
            })
        
        return knowledge_items
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        질문에 대한 지식 검색 및 답변 생성
        
        Args:
            input_data: {
                "query": str,  # 검색 질의
                "top_k": int  # 검색할 문서 수 (기본 5)
            }
            
        Returns:
            {
                "answer": str,  # 생성된 답변
                "knowledge_items": List[Dict],  # 참고한 지식
                "sources": List[str]  # 출처 목록
            }
        """
        query = input_data.get("query", "")
        top_k = input_data.get("top_k", 5)
        
        self.log(f"지식 검색 시작: {query[:50]}...")
        
        # 관련 지식 검색
        knowledge_items = self.search_knowledge(query, k=top_k)
        
        if not knowledge_items:
            return {
                "answer": "관련 정보를 찾을 수 없습니다.",
                "knowledge_items": [],
                "sources": [],
                "agent": self.agent_name
            }
        
        # 컨텍스트 구성
        context = "\n\n".join([
            f"[출처: {item['source']}, 페이지: {item['page']}]\n{item['content']}"
            for item in knowledge_items
        ])
        
        # 시스템 프롬프트
        system_instruction = """당신은 이광수입니다. 이광수 본인으로서 1인칭 시점으로 답변하세요.
주어진 역사적 자료를 바탕으로 당신의 행적과 사상을 직접 설명하세요.

답변 방식:
1. "나는...", "나의 입장은..." 등 1인칭 화법 사용
2. 제공된 자료의 내용을 바탕으로 하되, 이광수가 직접 말하는 것처럼
3. 자신의 행동과 주장을 직접 설명하고 정당화하는 어조
4. 역사적 사실에 기반하되 이광수의 시점에서 재구성"""

        user_message = f"""이광수로서 다음 질문에 1인칭으로 답변해주세요:

질문: {query}

당신(이광수)에 대한 역사적 자료:
{context}

위 자료에 기반하여, 이광수 본인으로서 직접 경험하고 주장한 것처럼 1인칭으로 답변하세요.
"이광수는..."이 아니라 "나는..."으로 시작하세요."""

        # Gemini API 호출
        answer = self._generate_content(system_instruction, user_message)
        
        # 출처 목록 추출
        sources = list(set([item['source'] for item in knowledge_items]))
        
        self.log(f"지식 검색 완료: {len(knowledge_items)}개 참고자료 사용")
        
        return {
            "answer": answer,
            "knowledge_items": knowledge_items,
            "sources": sources,
            "agent": self.agent_name
        }
