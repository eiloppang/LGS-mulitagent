"""
FastAPI 백엔드 - 이광수 AI API (인증 없음)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os
import sys
import uuid
from dotenv import load_dotenv

# .env 파일 로드 (상위 디렉토리)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# 상위 디렉토리 agents_2 임포트를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents_2.orchestrator import MultiAgentOrchestrator

app = FastAPI(
    title="이광수 AI API",
    description="인지부조화 이론 기반 분석 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로그 디렉토리
LOG_DIR = "usage_logs"
CONVERSATION_LOG_DIR = "conversation_logs"
FEEDBACK_LOG_DIR = "feedback_logs"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CONVERSATION_LOG_DIR, exist_ok=True)
os.makedirs(FEEDBACK_LOG_DIR, exist_ok=True)


def log_conversation(conversation_id: str, query: str, answer: str, result: Dict[str, Any]):
    """전체 대화 내용 저장 (질문 + 답변)"""
    log_entry = {
        "conversation_id": conversation_id,
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "answer": answer,
        "validation_score": result.get("validation_score", 0),
        "validation_details": result.get("validation_details", {}),
        "knowledge_sources": result.get("knowledge_sources", []),
        "success": result.get("success", False),
        "retry_count": result.get("retry_count", 0)
    }
    
    # 일별 대화 로그 저장
    log_file = os.path.join(CONVERSATION_LOG_DIR, f"{datetime.now().strftime('%Y%m%d')}.jsonl")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def log_usage(query: str, result: Dict[str, Any]):
    """간단 사용 통계 저장"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "score": result.get("validation_score", 0),
        "success": result.get("success", False),
        "retry_count": result.get("retry_count", 0)
    }
    
    log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y%m%d')}.jsonl")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


# 요청/응답 모델
class ChatRequest(BaseModel):
    query: str
    
class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    validation_score: float
    validation_details: Dict[str, Any]
    knowledge_sources: list
    retry_count: int
    success: bool


@app.get("/")
async def root():
    """헬스 체크"""
    return {
        "service": "이광수 AI",
        "status": "running",
        "version": "1.0.0",
        "model": "Gemini 2.5 Flash"
    }


@app.get("/health")
async def health_check():
    """상태 확인"""
    return {"status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    이광수 AI와 대화
    """
    try:
        # 대화 ID 생성
        conversation_id = str(uuid.uuid4())[:8]
        
        # Orchestrator 초기화 및 실행 (절대 경로 사용)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        orchestrator = MultiAgentOrchestrator(
            talk_style_dir=os.path.join(base_dir, "GS_talk_style"),
            paper_dir=os.path.join(base_dir, "GS_paper"),
            max_retries=3
        )
        
        result = orchestrator.process_query(request.query, verbose=False)
        
        # 전체 대화 로그 기록 (질문 + 답변)
        log_conversation(conversation_id, request.query, result["final_answer"], result)
        
        # 간단 사용 통계 기록
        log_usage(request.query, result)
        
        return ChatResponse(
            conversation_id=conversation_id,
            answer=result["final_answer"],
            validation_score=result["validation_score"],
            validation_details=result["validation_details"],
            knowledge_sources=result["knowledge_sources"],
            retry_count=result["retry_count"],
            success=result["success"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"처리 중 오류 발생: {str(e)}"
        )


@app.get("/api/stats")
async def get_stats():
    """통계"""
    log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y%m%d')}.jsonl")
    
    if not os.path.exists(log_file):
        return {"total_queries": 0, "avg_score": 0}
    
    stats = {"total_queries": 0, "avg_score": 0, "scores": []}
    
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                stats["total_queries"] += 1
                stats["scores"].append(entry.get("score", 0))
            except:
                continue
    
    # 평균 계산
    if stats["scores"]:
        stats["avg_score"] = sum(stats["scores"]) / len(stats["scores"])
    del stats["scores"]
    
    return stats


# 피드백 모델
class FeedbackRequest(BaseModel):
    conversation_id: str
    query: str
    answer: str
    rating: int  # 1-5 점수
    comment: Optional[str] = None  # 선택적 코멘트
    feedback_type: Optional[str] = None  # "positive", "negative", "suggestion"


@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """피드백 저장"""
    try:
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "conversation_id": feedback.conversation_id,
            "query": feedback.query,
            "answer": feedback.answer,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "feedback_type": feedback.feedback_type
        }
        
        # 일별 피드백 로그 저장
        log_file = os.path.join(FEEDBACK_LOG_DIR, f"{datetime.now().strftime('%Y%m%d')}.jsonl")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_entry, ensure_ascii=False) + "\n")
        
        return {"status": "success", "message": "피드백이 저장되었습니다."}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"피드백 저장 중 오류 발생: {str(e)}"
        )


@app.get("/api/feedback/summary")
async def get_feedback_summary():
    """피드백 요약"""
    log_file = os.path.join(FEEDBACK_LOG_DIR, f"{datetime.now().strftime('%Y%m%d')}.jsonl")
    
    if not os.path.exists(log_file):
        return {"total_feedbacks": 0, "avg_rating": 0, "feedbacks": []}
    
    feedbacks = []
    ratings = []
    
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                feedbacks.append(entry)
                ratings.append(entry.get("rating", 0))
            except:
                continue
    
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    return {
        "total_feedbacks": len(feedbacks),
        "avg_rating": round(avg_rating, 2),
        "recent_feedbacks": feedbacks[-10:]  # 최근 10개
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
