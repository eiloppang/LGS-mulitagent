"""
간단한 Ollama 연결 테스트
"""
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

print("="*60)
print("Ollama 연결 테스트")
print("="*60)

# 1. 환경 변수 확인
print("\n[환경 변수]")
print(f"OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
print(f"OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'gemma3:4b')}")
print(f"OLLAMA_EMBEDDING_MODEL: {os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')}")

# 2. Ollama 서버 연결 테스트
print("\n[서버 연결 테스트]")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags")
    if response.status_code == 200:
        print("✓ Ollama 서버 연결 성공")
        models = response.json().get('models', [])
        print(f"✓ 사용 가능한 모델 수: {len(models)}")
        for model in models:
            print(f"  - {model['name']}")
    else:
        print("✗ 서버 응답 오류")
except Exception as e:
    print(f"✗ 서버 연결 실패: {e}")

# 3. ChatOllama 테스트
print("\n[ChatOllama 테스트]")
try:
    from langchain_community.chat_models import ChatOllama
    
    llm = ChatOllama(
        model=os.getenv('OLLAMA_MODEL', 'gemma3:4b'),
        temperature=0.7
    )
    
    print("✓ ChatOllama 초기화 성공")
    
    # 간단한 테스트
    print("\n테스트 질문: 안녕하세요?")
    response = llm.invoke("안녕하세요? 간단히 인사해주세요.")
    print(f"답변: {response.content}")
    
except Exception as e:
    print(f"✗ ChatOllama 테스트 실패: {e}")
    import traceback
    traceback.print_exc()

# 4. OllamaEmbeddings 테스트
print("\n[OllamaEmbeddings 테스트]")
try:
    from langchain_community.embeddings import OllamaEmbeddings
    
    embeddings = OllamaEmbeddings(
        model=os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
    )
    
    print("✓ OllamaEmbeddings 초기화 성공")
    
    # 간단한 임베딩 테스트
    test_text = "테스트 문장입니다."
    vec = embeddings.embed_query(test_text)
    print(f"✓ 임베딩 생성 성공 (차원: {len(vec)})")
    
except Exception as e:
    print(f"✗ OllamaEmbeddings 테스트 실패: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("테스트 완료!")
print("="*60)
