"""
1인칭 답변 테스트
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("이광수 1인칭 답변 테스트")
print("="*60)

from agents import KnowledgeAgent, StyleAgent

# 지식 에이전트 테스트
print("\n[1단계] KnowledgeAgent - 초안 생성")
print("-"*60)

knowledge = KnowledgeAgent(
    paper_dir="./GS_paper",
    model_name=os.getenv("OLLAMA_MODEL", "gemma3:4b"),
    embedding_model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
)

result = knowledge.process({
    "query": "창씨개명에 대한 당신의 입장을 말씀해주세요",
    "top_k": 3
})

print(f"\n초안 답변:\n{result['answer']}\n")
print(f"출처: {result['sources']}")

# 스타일 에이전트 테스트  
print("\n" + "="*60)
print("[2단계] StyleAgent - 스타일 강화")
print("-"*60)

style = StyleAgent(
    talk_style_dir="./GS_talk_style",
    model_name=os.getenv("OLLAMA_MODEL", "gemma3:4b"),
    embedding_model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
)

styled_result = style.process({
    "text": result['answer'],
    "context": "창씨개명에 대한 본인의 입장"
})

print(f"\n최종 답변 (이광수 1인칭):\n{styled_result['styled_text']}\n")

print("="*60)
print("✅ 테스트 완료!")
print("="*60)
print("\n1인칭 표현 확인:")
print("- '나는', '나의' 등이 사용되었나요?")
print("- 이광수가 직접 말하는 것처럼 느껴지나요?")
