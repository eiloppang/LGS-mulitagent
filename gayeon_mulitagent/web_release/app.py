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

# 상위 디렉토리 agents_2 임포트를 위한 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 환경변수에서 API 키 로드 (Streamlit Cloud secrets 지원)
if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
    os.environ['GEMINI_API_KEY'] = st.secrets['GEMINI_API_KEY']

from agents_2.orchestrator import MultiAgentOrchestrator

# ===== Google Sheets 연동 =====
def get_gspread_client():
    """Google Sheets 클라이언트 생성"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
            credentials_dict = dict(st.secrets['gcp_service_account'])
            credentials = Credentials.from_service_account_info(
                credentials_dict,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
            )
            return gspread.authorize(credentials)
    except Exception as e:
        st.sidebar.warning(f"Google Sheets 연결 실패: {e}")
    return None

@st.cache_resource
def get_sheets():
    """Google Sheets 워크시트 가져오기"""
    client = get_gspread_client()
    if client:
        try:
            # 스프레드시트 열기 (secrets에서 이름 가져오기)
            sheet_name = st.secrets.get("SHEET_NAME", "이광수AI_로그")
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
@st.cache_resource
def get_orchestrator():
    """Orchestrator 싱글톤 인스턴스"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return MultiAgentOrchestrator(
        talk_style_dir=os.path.join(base_dir, "GS_talk_style"),
        paper_dir=os.path.join(base_dir, "GS_paper"),
        max_retries=3
    )

st.set_page_config(
    page_title="이광수 AI",
    page_icon="🤔",
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


def call_api(query: str):
    """직접 Orchestrator 호출"""
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.process_query(query, verbose=False)
        
        conversation_id = str(uuid.uuid4())[:8]
        
        # Google Sheets에 대화 기록 저장
        log_to_sheets("conversations", [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            conversation_id,
            query,
            result["final_answer"][:500],  # 답변 길이 제한
            result["validation_score"],
            "합격" if result["success"] else "불합격",
            result["retry_count"],
            ", ".join(result["knowledge_sources"][:3])
        ])
        
        return {
            "conversation_id": conversation_id,
            "answer": result["final_answer"],
            "validation_score": result["validation_score"],
            "validation_details": result["validation_details"],
            "knowledge_sources": result["knowledge_sources"],
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
        log_to_sheets("feedbacks", [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            conversation_id,
            query[:200],  # 질문 길이 제한
            rating,
            type_labels.get(feedback_type, feedback_type),
            comment[:500] if comment else ""
        ])
        
        return True
    except:
        return False


def get_stats():
    """세션 통계"""
    return {
        "total_queries": st.session_state.get("total_queries", 0),
        "avg_score": 0
    }, None


# CSS 스타일
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# 헤더
st.title("🤔 이광수 AI - 인지부조화 분석")
st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.divider()

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
    
    # 통계
    st.divider()
    st.subheader("📈 오늘의 통계")
    
    if st.button("통계 새로고침", use_container_width=True):
        stats, error = get_stats()
        
        if error:
            st.error(error)
        elif stats:
            st.metric("총 질문 수", stats["total_queries"])
            st.metric("평균 점수", f"{stats['avg_score']:.1f}")

# 메인 채팅 영역
st.subheader("💬 대화")

# 대화 이력
chat_container = st.container()
with chat_container:
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
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

# 입력
prompt = st.chat_input("이광수에게 질문하세요...")

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
            with st.spinner("🤔 이광수가 고뇌하고 있습니다..."):
                result, error = call_api(prompt)
                
                if error:
                    st.error(f"❌ {error}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"[오류] {error}"
                    })
                else:
                    answer = result["answer"]
                    conv_id = result.get("conversation_id", "unknown")
                    st.write(answer)
                    
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
                            "success": result["success"]
                        }
                    })
    
    # 사이드바 업데이트를 위한 리렌더
    st.rerun()

# 하단 정보
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("총 질문 수", st.session_state.total_queries)
with col2:
    st.metric("현재 세션", len(st.session_state.messages) // 2)
with col3:
    st.caption("Powered by Gemini 2.5 Flash")
