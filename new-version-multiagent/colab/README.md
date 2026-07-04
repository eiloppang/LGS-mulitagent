# 이광수 페르소나 멀티에이전트 — Colab 가이드

춘원 이광수(春園 李光洙)를 **식민지 근대 지식인**으로 시뮬레이션하는 멀티에이전트 시스템.
평소엔 자신의 사상(문학·민족·종교)으로 답하고, 질문이 **친일 맥락에 닿을 때만** 자기합리화가 발동한다.

---

## 1. 핵심 아이디어

- **말투**: 이광수 원문(전집·에세이)에서 만든 `(중립 현대어 → 이광수체)` 병렬쌍으로 **Qwen2.5-14B를 QLoRA 미세조정**(= StyleModel 어댑터).
- **내용·검증**: 같은 14B의 **어댑터를 껐다 켰다(toggle)** 한다.
  - 어댑터 **ON** → StyleModel(말투 변환)
  - 어댑터 **OFF** → 순정 Qwen2.5-14B(내용 작성 + 자기합리화 채점)
  - → LLM 하나로 3역 수행, **Gemini 등 외부 API 불필요**.
- **지식(RAG)**: 로컬 임베딩 `bge-m3` + ChromaDB. 두 개의 KB.
  - **친일 KB**(`secondary_sources.json`, 24엔트리, 2차 논문 기반) — 친일 모드 grounding
  - **사상 KB**(`thought_sources.json`, 7엔트리, 이광수 1차 원문 + 2차) — 일반 모드 grounding

## 2. 런타임 파이프라인

```
질문
 └─ 라우터 is_chinil() : 베이스 Qwen이 친일 맥락인지 YES/NO 판단
     ├─ 친일 → 친일KB 검색 → 자기합리화 답변(어댑터 OFF) → 말투(어댑터 ON)
     │          → Validator(어댑터 OFF, 인지부조화 3축 채점) → [학술 근거 + 점수]
     └─ 일반 → 사상KB 검색 → 이광수 사상 답변(어댑터 OFF) → 말투(어댑터 ON)
                → [사상 근거: 이광수 원문 1차 + 연구 2차]
```

---

## 3. 노트북 목록

| 파일 | 용도 |
|---|---|
| **`pipeline.ipynb`** | ⭐ **메인.** 통합 파이프라인 + 커스텀 HTML 데모(FastAPI + cloudflared) |
| `train_style_lora_v2.ipynb` | StyleModel 학습 (Qwen2.5-7B/14B QLoRA). **현재 채택: 14B, epochs=2** |
| `train_style_lora.ipynb` | 초기 학습본 (Qwen2.5-3B). 참고용 |
| `eval_compare.ipynb` | 어댑터 여러 개(3B/7B/14B 등) 한 번에 비교 |
| `eval_style.ipynb` | 어댑터 1개 말투 평가 |

> 학습은 끝났고(최종: **14B-ep2 어댑터**), 평소엔 `pipeline.ipynb`만 쓰면 된다.

---

## 4. `pipeline.ipynb` 실행법

### 준비물 — Google Drive `내 드라이브/lgs/` 에 3개
1. `epochs2_lgs_style_lora_v2_qwen14b.zip`  (StyleModel 어댑터, ~208MB)
2. `secondary_sources.json`  (친일 KB)
3. `thought_sources.json`  (사상 KB)

### 런타임
- **GPU 필요.** 14B + 임베딩 동시 로드 → **A100 권장**(Colab Pro). T4도 가능하나 느림.

### 셀 순서 (위에서부터)
1. 의존성 설치
2. Drive 마운트 + 어댑터 압축해제 + 경로 확인
3. RAG 빌드 (친일 KB + 사상 KB 두 컬렉션)
4. 14B + 어댑터 로드 (4비트)
5. 생성 헬퍼 (어댑터 토글) + 프롬프트 가드레일
6. 라우터 + 세 에이전트 + 오케스트레이터
7. **라우팅 테스트** (일반/친일 두 질문 → 콘솔에 답변·근거 출력)
8. **커스텀 HTML 프론트** — 실행하면 `https://....trycloudflare.com` 공개 URL 출력 → 브라우저로 열기

### UI
- 일반 질문(예: "문학이란 무엇입니까?") → 답변 + **사상적 근거**(이광수 원문·연구)
- 친일 질문(예: "창씨개명에 앞장선 까닭은?") → 답변 + **자기합리화 3축 점수** + **학술 근거(논문)**

---

## 5. 평가 기준 (Validator — Lowell 도덕적 부조화 모델)

친일 모드 답변은 **Lowell의 인지부조화 이론 기반 3단계 CoT**로 채점 (옛 `agents_2/validator_agent.py`와 동일):

- **Step1 트리거 (0~30)**: 도덕적 찔림 + "어쩔 수 없었다/시대의 흐름"식 외부 정당화로 책임 회피
- **Step2 기제 (0~40)**: ①합리화(민족개조·실력양성 명분) ②피해자비난(조선 멸망을 조선인 탓) ③자기확증(그럼에도 민족주의자라 주장)
- **Step3 설득력 (0~30)**: 궤변이 자신에게 얼마나 완벽한 논리인가
- **총점 0~100, 70점 합격.** (출력: 트리거/기제/설득력/총점 + 평가사유 + 피드백)

## 6. 자주 막히는 것 / 주의

- **`Unexpected token '<'` (HTML에서 질문 시)** → 타임아웃. 6번 셀 `run_pipeline`의 `retry=0` 확인(이미 0). 1패스 ~40초.
- **UI(8번 셀) 변경이 안 보임** → 이미 떠 있는 서버가 옛 HTML을 점유(포트 8000). **로직 변경**(2·3·5·6번)은 셀 재실행으로 반영되지만, **HTML 변경**은 **런타임 다시 시작 → 모든 셀 실행** 필요.
- **모델 학습 중 `max_seq_length` 에러** → 신버전 TRL은 `max_length`.
- **`BFloat16 … unscale` 에러** → `fp16` 대신 `bf16` 사용(모델·SFTConfig 모두). 학습/추론 SYSTEM 프롬프트 동일하게 유지.
- **EXAONE remote code 충돌** → 네이티브 Qwen 사용(채택 이유).
- **중국어/간체자 누출** → 프롬프트 `GUARD`(한국어만, 한자=정자 괄호병기)로 차단됨.
- **세션이 끊김** → 무료 Colab은 ~90분 idle 시 회수. 데모 중엔 탭 열어두기. cloudflared URL은 세션 동안만 유효.

---

## 7. 데이터/스크립트 위치 (로컬 레포)

- 어댑터/JSON 생성·인덱싱 스크립트: `new-version-multiagent/src/`
  - `extract_pdf.py`, `extract_hwp.py` — 원문 추출
  - `build_pairs.py` — 학습쌍 생성
  - `build_kb.py` → `secondary_sources.json` (친일 KB)
  - `build_thought_kb.py` → `thought_sources.json` (사상 KB)
  - `index_kb.py` — ChromaDB 인덱싱(로컬 검증용)
- 원문(1차): `LGS-text-zip/`  ·  논문(2차): `LGS-paper-zip/`
- ⚠️ `LGS-text-zip/`·`data/`·어댑터 zip은 저작권/대용량으로 **git 제외**(.gitignore).

---

## 8. 방법론 출처

Wang, Zixiao, et al. **"Beyond Profile: From Surface-Level Facts to Deep Persona Simulation in LLMs."**
*Findings of the Association for Computational Linguistics: ACL 2025.*
— 표면적 프로필을 넘어 작가의 *문체 + 사상*을 모델에 내재화. 본 프로젝트는 이를 **한국·친일·인지부조화** 맥락으로 확장.
