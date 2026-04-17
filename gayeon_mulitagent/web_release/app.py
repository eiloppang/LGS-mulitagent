"""
Streamlit 프론트엔드 - 이광수 AI (Streamlit Cloud 배포 버전)
API 서버 없이 직접 에이전트 호출 + Google Sheets 로그 저장
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import os
import sys
import uuid
import json
from dotenv import load_dotenv

# .env 로드 (로컬 실행용 — Streamlit Cloud에선 secrets.toml 사용)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# 상위 디렉토리 agents_2 임포트를 위한 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 환경변수에서 API 키 로드 (Streamlit Cloud secrets 지원, 로컬은 .env 사용)
try:
    if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
        os.environ['GEMINI_API_KEY'] = st.secrets['GEMINI_API_KEY']
except Exception:
    pass  # secrets.toml 없으면 .env에서 로드 (load_dotenv)

from agents_2.orchestrator import MultiAgentOrchestrator

# ===== Google Sheets 연동 =====
def get_gspread_client():
    """Google Sheets 클라이언트 생성 (secrets.toml 없으면 None 반환)"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        secrets = st.secrets.to_dict()
        if 'gcp_service_account' in secrets:
            credentials = Credentials.from_service_account_info(
                secrets['gcp_service_account'],
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
            )
            return gspread.authorize(credentials)
    except Exception:
        pass  # secrets.toml 없거나 인증 실패 시 조용히 None 반환
    return None

@st.cache_resource(show_spinner=False)
def get_sheets():
    """Google Sheets 워크시트 가져오기"""
    client = get_gspread_client()
    if client:
        try:
            # 스프레드시트 열기
            sheet_name = "이광수AI_로그"
            try:
                sheet_name = st.secrets.get("SHEET_NAME", sheet_name)
            except Exception:
                pass
            spreadsheet = client.open(sheet_name)
            
            # 워크시트 가져오기 또는 생성
            try:
                conversations = spreadsheet.worksheet("대화기록")
            except:
                conversations = spreadsheet.add_worksheet("대화기록", 1000, 10)
                conversations.append_row(["시간", "대화ID", "질문", "답변", "점수", "합격여부", "재시도", "출처"])
            
            try:
                feedbacks = spreadsheet.worksheet("피드백")
            except:
                feedbacks = spreadsheet.add_worksheet("피드백", 1000, 8)
                feedbacks.append_row(["시간", "대화ID", "질문", "평점", "유형", "코멘트"])
            
            return {"conversations": conversations, "feedbacks": feedbacks}
        except Exception as e:
            st.sidebar.warning(f"시트 접근 오류: {e}")
    return None

def log_to_sheets(sheet_type: str, data: list):
    """Google Sheets에 로그 저장"""
    try:
        sheets = get_sheets()
        if sheets and sheet_type in sheets:
            sheets[sheet_type].append_row(data)
            return True
    except Exception as e:
        print(f"로그 저장 오류: {e}")
    return False

# ===== Orchestrator 캐싱 =====
@st.cache_resource(show_spinner=False)
def get_orchestrator():
    """Orchestrator 싱글톤 인스턴스"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return MultiAgentOrchestrator(
        talk_style_dir=os.path.join(base_dir, "GS_talk_style"),
        paper_dir=os.path.join(base_dir, "GS_paper"),
        max_retries=3
    )

st.set_page_config(
    page_title="이광수의 자기변명",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = set()  # 피드백을 준 대화 ID 저장


import re as _re
import html as _html


def _extract_keywords(text: str, min_len: int = 2) -> set:
    """텍스트에서 고유명사·핵심 용어 추출 (2음절 이상 한글 단어)."""
    # 한자 괄호 안의 한글 읽기를 추출: 漢字(한글) → 한글
    readings = set(_re.findall(r'[\u4e00-\u9fff]+\(([가-힣]+)\)', text))
    # 일반 한글 단어 (2음절+)
    words = set(_re.findall(r'[가-힣]{' + str(min_len) + r',}', text))
    # 연도 패턴
    years = set(_re.findall(r'(?:19|20)\d{2}', text))
    all_kw = words | readings | years
    # 불용어 제거
    stopwords = {
        '하는', '있는', '없는', '되는', '했다', '있다', '없다', '되었',
        '이는', '그는', '또한', '대한', '통해', '위한', '따라', '대해',
        '그러', '하여', '함으로', '있어', '에서', '으로', '까지',
        '라는', '이다', '것이', '수가', '있으', '에게', '라고',
        '하고', '되고', '하며', '이며', '이요', '이니', '하옵',
        '나니', '할지', '하지', '소이', '니라', '이라',
    }
    return {kw for kw in all_kw if kw not in stopwords and len(kw) >= min_len}


def _split_sentences(text: str) -> list:
    """한국어 문장 분할 (마침 어미 기준)."""
    parts = _re.split(r'(?<=[.!?。\n])\s*', text)
    # 너무 짧은 조각은 이전 문장에 병합
    merged = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if merged and len(p) < 15:
            merged[-1] += ' ' + p
        else:
            merged.append(p)
    return merged


def annotate_citations(answer: str, knowledge_items: list) -> str:
    """
    답변 텍스트의 문장별로 논문 청크와 키워드 매칭하여
    관련 문장에 인라인 각주(밑줄 + hover tooltip) HTML을 삽입.

    프롬프트 수정 없이 후처리(post-processing)로 동작.
    """
    if not knowledge_items or not answer:
        return _html.escape(answer)

    # 1. 각 소스별 키워드 추출
    source_keywords = []
    for item in knowledge_items:
        kws = _extract_keywords(item.get('content', ''))
        source_keywords.append({
            'keywords': kws,
            'source': item.get('source', 'Unknown'),
            'page': item.get('page', '?'),
        })

    # 2. 답변을 문장 단위로 분할
    sentences = _split_sentences(answer)

    # 3. 각 문장에 대해 매칭
    annotated_parts = []
    for sent in sentences:
        sent_kws = _extract_keywords(sent)
        best_match = None
        best_count = 0

        for src in source_keywords:
            overlap = sent_kws & src['keywords']
            if len(overlap) > best_count and len(overlap) >= 2:
                best_count = len(overlap)
                best_match = src

        escaped = _html.escape(sent)
        if best_match:
            source_name = _html.escape(best_match['source'].replace('.pdf', ''))
            page = _html.escape(str(best_match['page']))
            tooltip = f"📄 {source_name} (p.{page})"
            annotated_parts.append(
                f'<span class="cited">{escaped}'
                f'<span class="cite-tooltip">{tooltip}</span>'
                f'</span>'
            )
        else:
            annotated_parts.append(escaped)

    return ' '.join(annotated_parts)


def call_api(query: str):
    """직접 Orchestrator 호출"""
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.process_query(query, verbose=False)
        
        conversation_id = str(uuid.uuid4())[:8]
        
        # Google Sheets에 대화 기록 저장
        log_success = log_to_sheets("conversations", [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            conversation_id,
            query,
            result["final_answer"][:500],  # 답변 길이 제한
            result["validation_score"],
            "합격" if result["success"] else "불합격",
            result["retry_count"],
            ", ".join(result["knowledge_sources"][:3])
        ])
        
        if not log_success:
            st.sidebar.error("📝 Google Sheets 로그 저장 실패")
        
        # knowledge_items 추출 (각주 매칭용)
        ki = []
        for entry in result.get("workflow_log", []):
            if entry.get("agent") == "KnowledgeAgent":
                ki = entry.get("result", {}).get("knowledge_items", [])
                break

        return {
            "conversation_id": conversation_id,
            "answer": result["final_answer"],
            "validation_score": result["validation_score"],
            "validation_details": result["validation_details"],
            "knowledge_sources": result["knowledge_sources"],
            "knowledge_items": ki,
            "retry_count": result["retry_count"],
            "success": result["success"]
        }, None
        
    except Exception as e:
        return None, f"처리 중 오류 발생: {str(e)}"


def submit_feedback(conversation_id: str, query: str, answer: str, rating: int, comment: str, feedback_type: str):
    """피드백 저장 (Google Sheets + 세션)"""
    try:
        # 세션 상태에 저장
        if "feedbacks" not in st.session_state:
            st.session_state.feedbacks = []
        st.session_state.feedbacks.append({
            "conversation_id": conversation_id,
            "query": query,
            "rating": rating,
            "comment": comment,
            "feedback_type": feedback_type,
            "timestamp": datetime.now().isoformat()
        })
        
        # Google Sheets에 피드백 저장
        type_labels = {"positive": "👍 좋아요", "negative": "👎 개선필요", "suggestion": "💡 제안"}
        feedback_success = log_to_sheets("feedbacks", [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            conversation_id,
            query[:200],  # 질문 길이 제한
            rating,
            type_labels.get(feedback_type, feedback_type),
            comment[:500] if comment else ""
        ])
        
        if not feedback_success:
            st.sidebar.error("📝 피드백 저장 실패")
        
        return True
    except:
        return False


def get_stats():
    """세션 통계"""
    return {
        "total_queries": st.session_state.get("total_queries", 0),
        "avg_score": 0
    }, None


# CSS 스타일 — Tier 1: Streamlit 기본 크롬 숨김 + 헤더 타이포그래피
st.markdown("""
<style>
    /* Streamlit 기본 UI 숨김 (발표용) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stHeader"] {background: transparent;}

    /* 기본 여백 축소 — 첫 화면에 더 많은 내용 담기 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* 버튼 전체 너비 */
    .stButton>button {
        width: 100%;
    }

    /* 샘플 질문 버튼 — 카드 느낌 */
    div[data-testid="column"] .stButton>button {
        white-space: normal;
        word-wrap: break-word;
        min-height: 5rem;
        text-align: left;
        padding: 0.75rem 1rem;
        line-height: 1.4;
        border: 1px solid #8B7355;
        background-color: #F5EDD6;
    }
    div[data-testid="column"] .stButton>button:hover {
        background-color: #E8DCC0;
        border-color: #3D2817;
    }

    /* Google Fonts — Noto Serif KR (이광수 답변용 세리프체) */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700&display=swap');

    /* 이광수 답변 카드 */
    .lgs-answer {
        font-family: 'Noto Serif KR', serif;
        font-size: 1.08rem;
        line-height: 1.85;
        color: #2C1F15;
        background: linear-gradient(135deg, #FAF3E3 0%, #F0E6CE 100%);
        border-left: 4px solid #8B2929;
        padding: 1.25rem 1.5rem;
        margin: 0.75rem 0 1rem 0;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 6px rgba(44,31,21,0.08);
    }

    /* 인라인 각주 — 밑줄 + hover tooltip */
    .cited {
        border-bottom: 2px dotted #8B2929;
        cursor: help;
        position: relative;
        display: inline;
    }
    .cited .cite-tooltip {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        bottom: 130%;
        left: 0;
        background: #2C1F15;
        color: #F5EDD6;
        padding: 0.5rem 0.85rem;
        border-radius: 5px;
        font-family: sans-serif;
        font-size: 0.78rem;
        line-height: 1.4;
        white-space: nowrap;
        z-index: 9999;
        box-shadow: 0 3px 10px rgba(0,0,0,0.35);
        transition: opacity 0.15s;
        pointer-events: none;
    }
    .cited .cite-tooltip::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 1.5rem;
        border: 6px solid transparent;
        border-top-color: #2C1F15;
    }
    .cited:hover .cite-tooltip {
        visibility: visible;
        opacity: 1;
    }

    /* 카카오톡 스타일 타이핑 인디케이터 (점 3개) */
    .typing-bubble {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 14px 20px;
        background: linear-gradient(135deg, #FAF3E3 0%, #F0E6CE 100%);
        border-radius: 18px;
        border-left: 3px solid #8B2929;
    }
    .typing-bubble span {
        width: 9px;
        height: 9px;
        background: #8B7355;
        border-radius: 50%;
        animation: typingBounce 1.4s infinite ease-in-out;
    }
    .typing-bubble span:nth-child(2) { animation-delay: 0.2s; }
    .typing-bubble span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typingBounce {
        0%, 80%, 100% { transform: scale(0.5); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* Running cache indicator 숨기기 */
    [data-testid="stStatusWidget"] { display: none !important; }

    /* 출처 목록 (답변 하단) */
    .lgs-sources {
        font-size: 0.82rem;
        color: #5A4A3A;
        margin-top: 0.5rem;
        padding: 0.5rem 0;
        border-top: 1px dashed #C4B396;
    }
    .lgs-sources strong {
        color: #3D2817;
    }

    /* 헤더: 제목 + 부제 */
    .lgs-header {
        text-align: center;
        padding: 0.5rem 0 1.5rem 0;
        border-bottom: 2px solid #3D2817;
        margin-bottom: 1.5rem;
    }
    .lgs-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #2C1F15;
        letter-spacing: 0.02em;
        margin-bottom: 0.25rem;
    }
    .lgs-subtitle {
        font-size: 1.05rem;
        color: #5A4A3A;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)


# 헤더
st.markdown(
    """
    <div class="lgs-header">
        <div class="lgs-title">이광수(李光洙)의 자기변명</div>
        <div class="lgs-subtitle">친일 문학자의 인지부조화(認知不調和) 언어 분석</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Google Sheets 연결은 백그라운드에서 조용히 (배너 숨김)
sheets_status = get_sheets()

# 사이드바
with st.sidebar:
    st.header("📊 분석 결과")
    
    if "last_result" in st.session_state:
        result = st.session_state.last_result
        
        # 검증 점수
        score = result["validation_score"]
        is_valid = result["success"]
        
        # 게이지 차트
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "검증 점수"},
            delta={'reference': 70},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen" if is_valid else "darkred"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 70], 'color': "gray"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        # 세부 점수
        st.subheader("세부 평가")
        details = result["validation_details"]
        aspects = details.get("aspects", {})
        
        st.metric(
            "1️⃣ 부조화 트리거",
            f"{aspects.get('trigger_analysis', 0):.0f} / 30",
            help="도덕적 찔림 포착 및 외부 정당화 분석"
        )
        
        st.metric(
            "2️⃣ 합리화 기제",
            f"{aspects.get('mechanism_identification', 0):.0f} / 40",
            help="Rationalization, Blaming Victims, Self Affirmation"
        )
        
        st.metric(
            "3️⃣ 설득력",
            f"{aspects.get('persuasiveness', 0):.0f} / 30",
            help="궤변의 치밀함과 자기 기만의 완성도"
        )
        
        # 재시도 정보
        if result["retry_count"] > 0:
            st.info(f"🔄 재시도: {result['retry_count']}회")
        
        # 피드백
        feedback = details.get("feedback", "")
        if feedback and feedback != "PASS":
            with st.expander("💬 피드백 보기"):
                st.write(feedback)
        
        # 출처
        st.divider()
        st.subheader("📚 참고 문헌")
        for i, source in enumerate(result["knowledge_sources"][:3], 1):
            st.caption(f"{i}. {source}")
    
    else:
        st.info("질문을 입력하면 분석 결과가 여기에 표시됩니다.")

# 메인 채팅 영역
st.subheader("💬 대화")

# 샘플 질문 (대화가 비어 있을 때만) — 5가지 쟁점축 기반
if not st.session_state.messages:
    st.markdown(
        "<p style='color:#5A4A3A; margin-bottom:0.5rem;'>"
        "아래 예시 질문을 클릭하거나, 하단 입력창에 직접 질문을 입력하세요."
        "</p>",
        unsafe_allow_html=True,
    )
    sample_questions = [
        ("전향의 내적 동인",
         "친일로 전향하신 가장 결정적인 계기는 무엇이었습니까?"),
        ("자전적 글쓰기 전략",
         "『나의 고백』에서 자신의 잘못을 어떻게 서술하셨는지 말씀해 주십시오."),
        ("창씨개명·선도적 협력",
         "창씨개명을 조선에서 앞장서 시행하신 까닭은 무엇입니까?"),
        ("참정권·감성 정치",
         "참정권 획득이 일제 협력의 명분이 된다고 보십니까?"),
        ("허위의식·공범론",
         "친일을 한 게 부끄럽지 않으십니까?"),
    ]
    sample_cols = st.columns(5)
    for idx, (topic, question) in enumerate(sample_questions):
        with sample_cols[idx]:
            if st.button(
                f"**{topic}**\n\n{question}",
                key=f"sample_q_{idx}",
                use_container_width=True,
            ):
                st.session_state.pending_prompt = question
                st.rerun()

# 대화 이력
chat_container = st.container()
with chat_container:
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant" and "meta" in msg:
                meta = msg["meta"]
                ki = meta.get("knowledge_items", [])
                annotated = annotate_citations(msg["content"], ki)
                src_html = ""
                srcs = meta.get("knowledge_sources", [])
                if srcs:
                    src_list = " / ".join(s.replace('.pdf', '') for s in srcs[:3])
                    src_html = (
                        f'<div class="lgs-sources">'
                        f'<strong>참고 문헌:</strong> {_html.escape(src_list)}'
                        f'</div>'
                    )
                st.markdown(
                    f'<div class="lgs-answer">{annotated}{src_html}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.write(msg["content"])
            
            # 메타 정보 + 피드백 버튼 (assistant만)
            if msg["role"] == "assistant" and "meta" in msg:
                meta = msg["meta"]
                conv_id = meta.get("conversation_id", str(idx))
                
                st.caption(
                    f"⏱️ 시간: {meta['timestamp']} | "
                    f"📊 점수: {meta['score']:.0f} | "
                    f"{'✅ 합격' if meta['success'] else '❌ 불합격'}"
                )
                
                # 피드백 버튼 (아직 피드백을 주지 않은 경우만)
                if conv_id not in st.session_state.feedback_given:
                    with st.expander("📝 이 답변에 피드백 남기기"):
                        # 이전 사용자 질문 찾기
                        prev_query = ""
                        if idx > 0 and st.session_state.messages[idx-1]["role"] == "user":
                            prev_query = st.session_state.messages[idx-1]["content"]
                        
                        col_a, col_b = st.columns([1, 1])
                        with col_a:
                            rating = st.slider(
                                "평점", 
                                min_value=1, 
                                max_value=5, 
                                value=3, 
                                key=f"rating_{conv_id}",
                                help="1: 매우 불만족, 5: 매우 만족"
                            )
                        with col_b:
                            feedback_type = st.selectbox(
                                "피드백 유형",
                                ["positive", "negative", "suggestion"],
                                format_func=lambda x: {"positive": "👍 좋아요", "negative": "👎 개선 필요", "suggestion": "💡 제안"}[x],
                                key=f"type_{conv_id}"
                            )
                        
                        comment = st.text_area(
                            "코멘트 (선택사항)",
                            placeholder="답변에 대한 의견을 자유롭게 작성해주세요...",
                            key=f"comment_{conv_id}"
                        )
                        
                        if st.button("피드백 제출", key=f"submit_{conv_id}", type="primary"):
                            success = submit_feedback(
                                conv_id, 
                                prev_query, 
                                msg["content"], 
                                rating, 
                                comment, 
                                feedback_type
                            )
                            if success:
                                st.session_state.feedback_given.add(conv_id)
                                st.success("✅ 피드백이 저장되었습니다. 감사합니다!")
                                st.rerun()
                            else:
                                st.error("피드백 저장에 실패했습니다.")
                else:
                    st.caption("✅ 피드백 완료")

# 입력 (샘플 버튼에서 지정된 prompt가 있으면 그것을 우선 사용)
prompt = st.chat_input("이광수에게 질문하세요...")
if not prompt and st.session_state.get("pending_prompt"):
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    # 사용자 메시지 추가
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    # 화면 업데이트
    with chat_container:
        with st.chat_message("user"):
            st.write(prompt)
    
    # AI 응답
    with chat_container:
        with st.chat_message("assistant"):
            # 카카오톡 스타일 타이핑 인디케이터
            typing_ph = st.empty()
            typing_ph.markdown(
                '<div class="typing-bubble">'
                '<span></span><span></span><span></span>'
                '</div>',
                unsafe_allow_html=True,
            )
            result, error = call_api(prompt)
            typing_ph.empty()

            if error:
                st.error(f"❌ {error}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"[오류] {error}"
                })
            else:
                answer = result["answer"]
                conv_id = result.get("conversation_id", "unknown")
                ki = result.get("knowledge_items", [])

                # 각주 달린 HTML 답변 카드
                annotated = annotate_citations(answer, ki)
                sources_html = ""
                if result.get("knowledge_sources"):
                    src_list = " / ".join(
                        s.replace('.pdf', '') for s in result["knowledge_sources"][:3]
                    )
                    sources_html = (
                        f'<div class="lgs-sources">'
                        f'<strong>참고 문헌:</strong> {_html.escape(src_list)}'
                        f'</div>'
                    )
                st.markdown(
                    f'<div class="lgs-answer">{annotated}{sources_html}</div>',
                    unsafe_allow_html=True,
                )

                # 메타 정보
                timestamp = datetime.now().strftime('%H:%M:%S')
                st.caption(
                    f"⏱️ {timestamp} | "
                    f"📊 {result['validation_score']:.0f}/100 | "
                    f"{'✅ 합격' if result['success'] else '❌ 불합격'}"
                )

                # 세션에 저장
                st.session_state.last_result = result
                st.session_state.total_queries += 1
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "meta": {
                        "conversation_id": conv_id,
                        "timestamp": timestamp,
                        "score": result["validation_score"],
                        "success": result["success"],
                        "knowledge_items": ki,
                        "knowledge_sources": result.get("knowledge_sources", []),
                    }
                })
    
    # 사이드바 점수 업데이트를 위한 리렌더
    st.rerun()

