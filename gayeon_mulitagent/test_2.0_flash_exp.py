#!/usr/bin/env python3
"""
Gemini 2.0 Flash Exp 모델 테스트
"""
import os
from dotenv import load_dotenv
from google import genai

# 환경변수 로드
load_dotenv('.env')

api_key = os.getenv('GEMINI_API_KEY')
model_name = os.getenv('GEMINI_MODEL', 'models/gemini-2.0-flash-exp')

print(f"API Key: {api_key[:20]}...")
print(f"Model: {model_name}")

# Gemini 클라이언트 초기화
client = genai.Client(api_key=api_key)

# 간단한 테스트
try:
    print("\n=== 테스트 시작 ===")
    response = client.models.generate_content(
        model=model_name,
        contents="안녕하세요, 당신은 누구인가요? 간단히 답변해주세요."
    )
    
    print(f"\n✅ 성공!")
    print(f"답변: {response.text[:200]}")
    print(f"\n사용 토큰: {response.usage_metadata}")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
