"""
Phase 1: (중립 현대어 -> 이광수 원문) 병렬 학습쌍 생성.

방법 (루쉰 ST 논문 채택 + 조정):
  1) raw_txt 정리 + 문장 분절 (~25..200자, 한글비율 필터)
  2) 각 이광수 원문 문장 -> Gemini로 '중립화'(문체 제거, 의미·논증·어조 보존)
     - 문장당 2개 변형(augmentation) -> 쌍 수 약 2배
  3) JSONL 저장: {"neutral": ..., "lgs": ...}
     학습 방향 = neutral -> lgs

사용법:
  python src/build_pairs.py --file "민족 개조론"      # 한 편만 (검증용)
  python src/build_pairs.py                          # raw_txt 전체
출력:
  data/pairs/pairs.jsonl   (이어쓰기, dedup)
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from google import genai
from google.genai import types

ROOT = "C:/yeon-git/LGS-mulitagent"
RAW_DIR = f"{ROOT}/new-version-multiagent/data/raw_txt"
OUT_DIR = f"{ROOT}/new-version-multiagent/data/pairs"
MODEL = "gemini-2.5-flash"

# §4.1 gold 풀: 에세이 전체 + 1인칭 소설 3권(유정/나/그의 자서전).
# 3인칭 소설은 gold 제외(stance 누수 방지). 파일명 일부로 매칭.
GOLD_NOVELS = ["12권, 유정", "20권, 나", "16권, 그의 자서전"]
ESSAY_NAMES = [  # raw_txt 중 hwp(전집)이 아닌 에세이 PDF 추출본
    "돌베개", "민족 개조론", "창씨개명", "육장기", "조선의 학도여",
    "황민화와 조선문학", "심적 신체제와 조선 문화의 진로",
    "사상도 함께 영미 擊滅", "李光洙氏와 交談錄",
]


def is_gold(filename: str) -> bool:
    base = os.path.basename(filename)
    return any(k in base for k in GOLD_NOVELS) or any(k in base for k in ESSAY_NAMES)


def load_api_key() -> str:
    """new-version/.env 우선, 없으면 gayeon_mulitagent/.env. 키 미설정 시 친절히 안내."""
    candidates = [
        f"{ROOT}/new-version-multiagent/.env",
        f"{ROOT}/gayeon_mulitagent/.env",
    ]
    for path in candidates:
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line.startswith("GEMINI_API_KEY") and "=" in line:
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key and key != "PASTE_YOUR_KEY_HERE":
                    print(f"[key] {os.path.relpath(path, ROOT)} 사용")
                    return key
    raise SystemExit(
        "GEMINI_API_KEY 미설정. new-version-multiagent/.env 의 "
        "PASTE_YOUR_KEY_HERE 를 본인 키로 바꿔주세요."
    )

PROMPT = """너는 한국어 문체 변환기다. [원문]은 1920~40년대 이광수(춘원)의 글이다.
이를 '문체를 완전히 지운 평이한 현대 한국어'로 다시 써라. 톤은 신문 칼럼·설명문 같은 담백한 현대 문어체(-다체)다.

[꼭 지킬 것]
1. 뜻, 주장의 논리(논증적 의도), 감정적 어조는 그대로 보존한다.
2. 제거/현대화한다: 고풍 어미(-노라,-더이다), 예스러운 어휘(무릇,인심,장래), 한자어 괄호병기(更新(경신)->'쇄신'), 도치·만연체.
3. 어순·표현을 자유롭게 바꿔도 된다. 단 내용을 요약·삭제하지 마라.
4. 결과가 원문과 비슷하면 실패다. 누가 봐도 '요즘 글'로 충분히 바꿔라.

서로 다른 방식으로 바꾼 2개의 변형을 JSON으로 출력하라: {{"v1": "...", "v2": "..."}}

[예시]
원문: 무릇 어떤 관념이 지배하던 시대가 지나가고 새로운 어떤 다른 관념이 지배하려는 시대가 올 때에는 반드시 인심에 경신이라든지 개혁이라든지 하는 관념이 드는 것입니다.
출력: {{"v1": "한 시대를 지배하던 생각이 저물고 새로운 생각이 그 자리를 차지하려 할 때면, 사람들의 마음에는 늘 쇄신이나 개혁 같은 생각이 떠오른다.", "v2": "어떤 생각이 시대를 이끌다가 물러나고 다른 생각이 주도권을 잡으려 할 때, 사람들은 으레 쇄신이나 개혁을 떠올리게 된다."}}

[원문]
{src}
"""


def clean_text(t: str) -> str:
    t = t.replace("­", "")          # soft hyphen
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\s*\n\s*", " ", t)       # PDF 줄바꿈 = 문장 중간 -> 공백
    t = re.sub(r" {2,}", " ", t)
    return t.strip()


def hangul_ratio(s: str) -> float:
    if not s:
        return 0.0
    h = sum(0xAC00 <= ord(c) <= 0xD7A3 for c in s)
    return h / len(s)


def has_hanja(s: str) -> bool:
    return any(0x4E00 <= ord(c) <= 0x9FFF for c in s)


def style_density(s: str) -> float:
    """문체 밀도 점수: 한자어 포함·적정 길이·격식 어미 우대 (대표 문장 선별용)."""
    score = 0.0
    if has_hanja(s):
        score += 2.0
    score += min(len(s), 150) / 150.0
    if re.search(r"(노라|더이다|이러라|하였|이었|니라|로다)", s):
        score += 0.5
    return score


def sentences(t: str) -> list[str]:
    # 문장 종결부([.!?] 또는 닫는 인용부호) 뒤에서 분절
    parts = re.split(r"(?<=[.!?。」』])\s+", clean_text(t))
    out = []
    for s in parts:
        s = s.strip()
        if 25 <= len(s) <= 200 and hangul_ratio(s) >= 0.30:
            out.append(s)
    # dedup (순서 유지)
    seen, uniq = set(), []
    for s in out:
        if s not in seen:
            seen.add(s); uniq.append(s)
    return uniq


def neutralize(client: genai.Client, src: str) -> list[str]:
    cfg = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=1.0,
    )
    r = client.models.generate_content(
        model=MODEL, contents=PROMPT.format(src=src), config=cfg
    )
    try:
        d = json.loads(r.text)
        return [v.strip() for v in (d.get("v1"), d.get("v2")) if v and v.strip()]
    except Exception:
        return []


def collect_sentences(per_source: int, max_total: int) -> list[str]:
    """gold 파일별로 문체밀도 상위 per_source 문장 수집 -> 합쳐서 max_total로 제한."""
    files = [f for f in sorted(glob.glob(f"{RAW_DIR}/*.txt")) if is_gold(f)]
    picked: list[str] = []
    for fp in files:
        s = sentences(open(fp, encoding="utf-8").read())
        s.sort(key=style_density, reverse=True)
        take = s[:per_source] if per_source else s
        picked += take
        m = re.search(r"(\d+권)", os.path.basename(fp))
        print(f"  [{m.group(1) if m else os.path.basename(fp)[:12]}] 문장 {len(s)} -> 채택 {len(take)}")
    # dedup 전체
    seen, uniq = set(), []
    for s in picked:
        if s not in seen:
            seen.add(s); uniq.append(s)
    return uniq[:max_total] if max_total else uniq


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-source", type=int, default=700, help="소스(파일)당 상위 문장 수")
    ap.add_argument("--max-total", type=int, default=0, help="전체 문장 상한(0=무제한)")
    ap.add_argument("--sample", type=int, default=0, help="검증용: 앞 N문장만")
    ap.add_argument("--workers", type=int, default=8, help="동시 호출 수")
    args = ap.parse_args()

    client = genai.Client(api_key=load_api_key())

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = f"{OUT_DIR}/pairs.jsonl"
    existing = set()
    if os.path.exists(out_path):
        for line in open(out_path, encoding="utf-8"):
            try:
                existing.add(json.loads(line)["lgs"])
            except Exception:
                pass

    sents = collect_sentences(args.per_source, args.max_total)
    sents = [s for s in sents if s not in existing]
    if args.sample:
        sents = sents[: args.sample]
    print(f"대상 문장 {len(sents)}개 (이미 처리 {len(existing)}개 제외), workers={args.workers}")

    def work(s: str):
        for attempt in range(3):
            try:
                return s, neutralize(client, s)
            except Exception:
                time.sleep(2 * (attempt + 1))
        return s, []

    n_pairs = done = 0
    with open(out_path, "a", encoding="utf-8") as f, \
            ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(work, s) for s in sents]
        for fut in as_completed(futs):
            s, variants = fut.result()
            for nv in variants:
                f.write(json.dumps({"neutral": nv, "lgs": s}, ensure_ascii=False) + "\n")
                n_pairs += 1
            done += 1
            if done % 50 == 0:
                f.flush()
                print(f"  {done}/{len(sents)} 문장, 누적 쌍 {n_pairs}")

    print("=" * 40)
    print(f"완료: 문장 {len(sents)} -> 쌍 {n_pairs}개  ({out_path})")


if __name__ == "__main__":
    main()
