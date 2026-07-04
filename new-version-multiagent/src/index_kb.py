"""
KB 인덱싱: secondary_sources.json(24엔트리) → ChromaDB (로컬 임베딩 bge-m3).
임베딩 대상 = 하위주제 + 핵심_논거 + 키워드.
metadata(검색 후 반환) = 논문_출처(저자·연도·제목·학술지·권호·페이지)·쟁점축·시기·하위주제·관련_1차사료·키워드.

사용:
  python src/index_kb.py            # 인덱스 빌드
  python src/index_kb.py --test     # 빌드 후 검색 테스트
출력:
  data/chroma_kb/ (Chroma 영속 인덱스)
"""
from __future__ import annotations
import argparse
import json
import os

ROOT = "C:/yeon-git/LGS-mulitagent/new-version-multiagent"
KB = f"{ROOT}/secondary_sources.json"
CHROMA_DIR = f"{ROOT}/data/chroma_kb"
COLL = "lgs_secondary"
EMB_MODEL = "BAAI/bge-m3"


def doc_text(e: dict) -> str:
    kw = ", ".join(e.get("키워드", []))
    return f"[{e['쟁점축']}] {e['하위주제']}\n{e['핵심_논거']}\n키워드: {kw}"


def metadata(e: dict) -> dict:
    s = e["논문_출처"]
    return {
        "id": e["id"],
        "쟁점축": e["쟁점축"],
        "하위주제": e["하위주제"],
        "저자": str(s.get("저자", "")),
        "연도": str(s.get("연도", "")),
        "제목": str(s.get("제목", "")),
        "학술지": str(s.get("학술지", "")),
        "권호": str(s.get("권호", "")),
        "페이지": str(s.get("페이지", "")),
        "시기": str(e.get("시기", "")),
        "관련_1차사료": " / ".join(e.get("관련_1차사료", [])),
        "키워드": ", ".join(e.get("키워드", [])),
    }


def build(model):
    import chromadb
    entries = json.load(open(KB, encoding="utf-8"))
    docs = [doc_text(e) for e in entries]
    print(f"엔트리 {len(entries)}개 임베딩 중 ({EMB_MODEL}) ...")
    embs = model.encode(docs, normalize_embeddings=True, show_progress_bar=False)

    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection(COLL)
    except Exception:
        pass
    coll = client.create_collection(COLL, metadata={"hnsw:space": "cosine"})
    coll.add(
        ids=[e["id"] for e in entries],
        embeddings=[v.tolist() for v in embs],
        documents=docs,
        metadatas=[metadata(e) for e in entries],
    )
    print(f"인덱스 완료: {coll.count()}개 -> {CHROMA_DIR}")
    return client


def test(model, client=None, axis=None):
    import chromadb
    if client is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
    coll = client.get_collection(COLL)
    queries = [
        "이광수가 창씨개명에 협력한 이유는 무엇인가",
        "친일은 민족을 위한 불가피한 선택이었다는 자기변명",
        "징병을 권유한 프로파간다",
        "왜 전향했는가, 사상이 어떻게 바뀌었나",
    ]
    out_lines = []
    for q in queries:
        qe = model.encode([q], normalize_embeddings=True)[0].tolist()
        res = coll.query(query_embeddings=[qe], n_results=3)
        out_lines.append(f"Q: {q}")
        for i in range(len(res["ids"][0])):
            m = res["metadatas"][0][i]
            dist = res["distances"][0][i]
            out_lines.append(
                f"  [{m['id']}] ({m['쟁점축']}) {m['저자']}({m['연도']}) sim={1-dist:.3f}"
            )
        out_lines.append("")
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(CHROMA_DIR)),
        "data", "_retrieval_test.txt")
    open(out_path, "w", encoding="utf-8").write("\n".join(out_lines))
    print("검색 테스트 ->", out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    args = ap.parse_args()
    from sentence_transformers import SentenceTransformer
    print("임베딩 모델 로드 중(최초 1회 다운로드 ~2GB)...")
    model = SentenceTransformer(EMB_MODEL)
    client = build(model)
    if args.test:
        test(model, client)


if __name__ == "__main__":
    main()
