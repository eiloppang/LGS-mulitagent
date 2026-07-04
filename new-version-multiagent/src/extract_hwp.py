"""
Phase 0 (hwp): 태학사판 이광수 전집 .hwp/.hwpx -> 클린 UTF-8 텍스트.

gethwp.read_hwp / read_hwpx 사용 (두 포맷 모두 처리됨, 한자어 괄호병기 보존 확인).
헤더 찌꺼기·각주표시·페이지번호 등 잡음 제거. 1인칭 점수도 함께 출력해 §4.1 분류 보조.

사용법:
    python src/extract_hwp.py
출력:
    data/raw_txt/<원본이름>.txt
    + 콘솔에 파일별 chars/hangul/1인칭점수
"""
from __future__ import annotations
import glob
import os
import re

import gethwp

ROOT = "C:/yeon-git/LGS-mulitagent"
SRC_DIR = f"{ROOT}/new-version-multiagent/LGS-text-zip"
OUT_DIR = f"{ROOT}/new-version-multiagent/data/raw_txt"

# 각주/페이지번호/장번호만 있는 줄
JUNK_LINE = re.compile(r"^[\s]*\(?\^?\d+[\.\)]?[\s]*$")


def hangul_ratio(s: str) -> float:
    if not s:
        return 0.0
    return sum(0xAC00 <= ord(c) <= 0xD7A3 for c in s) / len(s)


def clean(text: str) -> str:
    lines = text.splitlines()
    # 1) 선두 헤더 찌꺼기 제거: 한글 거의 없는 줄을 본문 시작 전까지 버림
    start = 0
    for i, ln in enumerate(lines):
        if hangul_ratio(ln) >= 0.3 and len(ln.strip()) >= 10:
            start = i
            break
    lines = lines[start:]
    # 2) 각주/번호만 있는 줄 제거
    lines = [ln for ln in lines if not JUNK_LINE.match(ln)]
    text = "\n".join(lines)
    # 3) 제어문자 제거
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def first_person_score(text: str) -> float:
    """1인칭 지표(나/내가/나는/우리) 밀도. 1000자당 출현 수."""
    if not text:
        return 0.0
    hits = len(re.findall(r"(나는|내가|나도|나의|우리(가|는|의)?|내 )", text))
    return round(hits / (len(text) / 1000), 1)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(glob.glob(f"{SRC_DIR}/*.hwp")) + sorted(glob.glob(f"{SRC_DIR}/*.hwpx"))
    if not files:
        raise SystemExit("hwp 파일 없음")

    rows = []
    for p in files:
        kind = "hwpx" if p.endswith(".hwpx") else "hwp"
        try:
            raw = gethwp.read_hwpx(p) if kind == "hwpx" else gethwp.read_hwp(p)
        except Exception as e:
            print(f"[ERR] {os.path.basename(p)}: {type(e).__name__}: {e}")
            continue
        text = clean(raw)
        name = os.path.splitext(os.path.basename(p))[0]
        with open(f"{OUT_DIR}/{name}.txt", "w", encoding="utf-8") as f:
            f.write(text)
        h = sum(0xAC00 <= ord(c) <= 0xD7A3 for c in text)
        fp = first_person_score(text)
        rows.append((name, kind, len(text), h, fp))

    # 1인칭 점수 내림차순 -> gold 후보가 위로
    print(f"{'권':40s} {'fmt':4s} {'chars':>8s} {'hangul':>8s} {'1인칭':>6s}")
    print("-" * 72)
    for name, kind, c, h, fp in sorted(rows, key=lambda r: -r[4]):
        tag = " <- 1인칭 gold 후보" if fp >= 8 else ""
        # 콘솔 인코딩 회피용: 권 번호만 ascii로
        m = re.search(r"(\d+)권", name)
        label = f"{m.group(0) if m else name[:10]}"
        print(f"{label:40s} {kind:4s} {c:8d} {h:8d} {fp:6.1f}{tag}")


if __name__ == "__main__":
    main()
