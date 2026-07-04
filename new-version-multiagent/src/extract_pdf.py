"""
Phase 0: LGS-text-zip 의 이광수 원문 PDF → 클린 UTF-8 텍스트 추출.

에세이(친일 1인칭) PDF는 PyMuPDF로 깨끗이 추출됨(한자어 괄호 병기 보존).
hwp 소설은 별도 처리(추후). 이 스크립트는 PDF만 대상.

사용법:
    python src/extract_pdf.py
출력:
    data/raw_txt/<원본이름>.txt
"""
from __future__ import annotations
import glob
import os

import fitz  # PyMuPDF

SRC_DIR = "new-version-multiagent/LGS-text-zip"
OUT_DIR = "new-version-multiagent/data/raw_txt"


def extract(path: str) -> str:
    doc = fitz.open(path)
    return "\n".join(doc[i].get_text() for i in range(doc.page_count))


def hangul_count(text: str) -> int:
    return sum(0xAC00 <= ord(c) <= 0xD7A3 for c in text)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    pdfs = sorted(glob.glob(os.path.join(SRC_DIR, "*.pdf")))
    if not pdfs:
        raise SystemExit(f"PDF 없음: {SRC_DIR}")

    total = 0
    for p in pdfs:
        text = extract(p)
        name = os.path.splitext(os.path.basename(p))[0]
        out = os.path.join(OUT_DIR, name + ".txt")
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        h = hangul_count(text)
        total += len(text)
        # 콘솔 인코딩 문제 회피: 길이/한글수만 ASCII로 출력
        print(f"[OK] chars={len(text):6d} hangul={h:6d}  -> {out}")

    print("=" * 40)
    print(f"총 {len(pdfs)}개 PDF, 총 {total} chars 추출 완료")


if __name__ == "__main__":
    main()
