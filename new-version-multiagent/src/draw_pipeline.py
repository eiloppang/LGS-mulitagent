"""논문 figure용 파이프라인 다이어그램 PNG 생성 (matplotlib, 300dpi)."""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import font_manager

# 한글 폰트
fp = "C:/Windows/Fonts/malgun.ttf"
font_manager.fontManager.addfont(fp)
plt.rcParams["font.family"] = font_manager.FontProperties(fname=fp).get_name()
plt.rcParams["axes.unicode_minus"] = False

INK = "#1a1a1a"; SUB = "#555"; EDGE = "#3a3a3a"
FACE = "#ffffff"; SOFT = "#eeeeee"; STAR = "#fbe6c4"; STAREDGE = "#c08a3e"
SRC = "#e9eef2"; SRCEDGE = "#7f9aa8"

W, H = 15.2, 7.4
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")


def box(cx, cy, w, h, title, sub=None, face=FACE, edge=EDGE, lw=1.4, tcol=INK):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.14",
        linewidth=lw, edgecolor=edge, facecolor=face, zorder=2))
    if sub:
        ax.text(cx, cy + 0.20, title, ha="center", va="center",
                fontsize=12.5, fontweight="bold", color=tcol, zorder=3)
        ax.text(cx, cy - 0.28, sub, ha="center", va="center",
                fontsize=9.3, color=SUB, zorder=3)
    else:
        ax.text(cx, cy, title, ha="center", va="center",
                fontsize=11.5, fontweight="bold", color=tcol, zorder=3)
    return dict(cx=cx, cy=cy, w=w, h=h)


def arrow(a, b, style="-|>", color=EDGE, lw=1.7, ls="-", rad=0.0, z=1.5):
    ax.add_patch(FancyArrowPatch(
        a, b, arrowstyle=style, mutation_scale=16, lw=lw,
        color=color, linestyle=ls,
        connectionstyle=f"arc3,rad={rad}", zorder=z))


def rightleft(A, B, **kw):
    arrow((A["cx"] + A["w"] / 2, A["cy"]), (B["cx"] - B["w"] / 2, B["cy"]), **kw)


# ----- 단계 라벨 -----
ax.text(0.25, 6.95, "①  오프라인 · 말투 모델(StyleModel) 학습", ha="left",
        fontsize=12, fontweight="bold", color=STAREDGE)
ax.text(0.25, 3.15, "②  런타임 · 멀티 에이전트 추론", ha="left",
        fontsize=12, fontweight="bold", color=EDGE)

# ===== ① 오프라인 (y≈5.4) =====
y1 = 5.35; h1 = 1.25
s1 = box(2.0, y1, 2.5, h1, "1차 사료", "이광수 원문\n에세이·1인칭 소설", face=SRC, edge=SRCEDGE)
s2 = box(5.5, y1, 2.6, h1, "추출 · 분류", "PDF·hwp 추출\n1인칭 gold 선별")
s3 = box(9.1, y1, 2.8, h1, "중립화 → 병렬쌍", "(중립어 ↔ 이광수체)\n4,620쌍")
s4 = box(12.7, y1, 2.7, h1, "QLoRA 학습 ★", "Qwen2.5-3B\n→ StyleModel(LoRA)",
         face=STAR, edge=STAREDGE)
for A, B in [(s1, s2), (s2, s3), (s3, s4)]:
    rightleft(A, B)

# ===== ② 런타임 (y≈1.5) =====
y2 = 1.5; h2 = 1.25
q = box(1.4, y2, 1.5, h2, "사용자\n질문", face=SOFT, edge=EDGE)
k = box(4.6, y2, 2.7, h2, "지식 에이전트", "논문 RAG\n친일 논거")
st = box(8.2, y2, 2.7, h2, "말투 모델 ★", "이광수 문체로\n재서술", face=STAR, edge=STAREDGE)
v = box(11.8, y2, 2.7, h2, "검증 에이전트", "자기합리화 3축\n정합성 채점")
a = box(14.2, y2, 1.5, h2, "최종\n답변", face=SOFT, edge=EDGE)
# 본류 화살표
arrow((q["cx"] + q["w"] / 2, y2), (k["cx"] - k["w"] / 2, y2))
rightleft(k, st); rightleft(st, v)
arrow((v["cx"] + v["w"] / 2, y2), (a["cx"] - a["w"] / 2, y2))

# 재시도 루프 (아래로 우회)
arrow((v["cx"], v["cy"] - h2 / 2), (st["cx"], st["cy"] - h2 / 2),
      color=STAREDGE, lw=1.5, ls=(0, (5, 3)), rad=-0.35)
ax.text((st["cx"] + v["cx"]) / 2, 0.42, "검증 미달 시 재시도 (≤ 3회)",
        ha="center", fontsize=9, color=STAREDGE)

# ① → ② : 어댑터 탑재 (대각 점선)
arrow((s4["cx"], s4["cy"] - h1 / 2), (st["cx"], st["cy"] + h2 / 2),
      color=STAREDGE, lw=1.6, ls=(0, (4, 3)), rad=0.12)
ax.text(10.7, 3.55, "어댑터 탑재", ha="center", fontsize=9.5,
        color=STAREDGE, fontweight="bold", rotation=0)

# 2차 사료 -> 지식·검증
src2 = box(4.6, 3.85, 2.4, 0.9, "2차 사료 · 논문", face=SRC, edge=SRCEDGE)
arrow((src2["cx"], src2["cy"] - 0.45), (k["cx"], k["cy"] + h2 / 2),
      color=SRCEDGE, lw=1.3)
arrow((src2["cx"] + 1.2, src2["cy"]), (v["cx"], v["cy"] + h2 / 2),
      color=SRCEDGE, lw=1.2, ls=(0, (3, 3)), rad=-0.25)
ax.text(8.7, 3.0, "검증 기준", ha="center", fontsize=8, color=SRCEDGE)

out = "C:/yeon-git/LGS-mulitagent/new-version-multiagent/docs/pipeline.png"
plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
print("saved:", out)
