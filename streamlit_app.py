import streamlit as st
import time

st.set_page_config(page_title="나는 어떤 사람?", page_icon="🔮", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DungGeunMo&family=Press+Start+2P&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #1a0a2e !important;
}
[data-testid="stHeader"], [data-testid="stBottom"] { display: none; }

* { font-family: 'DungGeunMo', monospace !important; }

.title {
    font-family: 'Press Start 2P', monospace !important;
    font-size: 16px;
    color: #f0e0ff;
    text-align: center;
    line-height: 2;
    text-shadow: 3px 3px #7c3aed;
    margin-bottom: 6px;
}
.subtitle {
    text-align: center;
    color: #a78bfa;
    font-size: 14px;
    margin-bottom: 24px;
}
.pixel-box {
    background: #120822;
    border: 3px solid #7c3aed;
    border-radius: 4px;
    padding: 20px;
    margin-bottom: 16px;
    image-rendering: pixelated;
}
.q-num {
    color: #f472b6;
    font-size: 12px;
    letter-spacing: 2px;
    margin-bottom: 6px;
}
.q-text {
    color: #f0e0ff;
    font-size: 18px;
    line-height: 1.7;
    margin-bottom: 16px;
}
.pixel-char {
    font-size: 72px;
    text-align: center;
    display: block;
    margin: 10px 0;
    image-rendering: pixelated;
    filter: drop-shadow(4px 4px 0px rgba(124,58,237,0.8));
}
.result-name {
    font-family: 'Press Start 2P', monospace !important;
    font-size: 13px;
    color: #fbbf24;
    text-align: center;
    text-shadow: 2px 2px #92400e;
    margin: 10px 0 4px;
}
.result-type {
    font-size: 28px;
    color: #f472b6;
    text-align: center;
    letter-spacing: 4px;
    margin-bottom: 12px;
}
.result-desc {
    color: #c4b5fd;
    font-size: 16px;
    line-height: 1.9;
    text-align: center;
}
.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}
.stat-label { color: #a78bfa; font-size: 14px; width: 80px; }
.stat-bar-wrap { flex: 1; background: #2d1b4e; border-radius: 2px; height: 14px; margin: 0 10px; }
.stat-bar-fill { height: 14px; border-radius: 2px; }
.stat-val { color: #f0e0ff; font-size: 13px; width: 36px; text-align: right; }

.progress-wrap { background: #2d1b4e; border-radius: 2px; height: 10px; margin-bottom: 20px; }
.progress-fill { height: 10px; border-radius: 2px; background: linear-gradient(90deg, #7c3aed, #f472b6); transition: width 0.4s; }

[data-testid="stButton"] button {
    background: #3b0764 !important;
    border: 2px solid #7c3aed !important;
    color: #f0e0ff !important;
    border-radius: 4px !important;
    font-family: 'DungGeunMo', monospace !important;
    font-size: 16px !important;
    padding: 10px !important;
    width: 100% !important;
    transition: all 0.1s !important;
}
[data-testid="stButton"] button:hover {
    background: #7c3aed !important;
    transform: translateY(-2px) !important;
}
[data-testid="stButton"] button:active {
    transform: translateY(1px) !important;
}
</style>
""", unsafe_allow_html=True)

# ── 질문 & 선택지 (각 선택에 점수 딕셔너리) ──────────────────
# 4개 축: E/I, S/N, T/F, J/P
QUESTIONS = [
    {
        "q": "주말에 갑자기 친구한테 연락이 왔다.\n'나 지금 근처인데 나와!' 나의 반응은?",
        "a": [
            {"text": "🎉 대박! 바로 나간다", "score": {"E": 2}},
            {"text": "😅 좀 귀찮지만... 나가지 뭐", "score": {"E": 1}},
            {"text": "😬 오늘 좀 쉬고 싶었는데...", "score": {"I": 1}},
            {"text": "🛋️ 핑계 대고 집에 있는다", "score": {"I": 2}},
        ]
    },
    {
        "q": "새 카페를 갔는데 메뉴판이 엄청 많다.\n어떻게 고르지?",
        "a": [
            {"text": "☕ 늘 먹던 걸로 안전하게", "score": {"S": 2}},
            {"text": "📋 메뉴 설명 꼼꼼히 읽고 결정", "score": {"S": 1}},
            {"text": "✨ 이름 예쁜 거 or 신메뉴 도전", "score": {"N": 1}},
            {"text": "🎲 랜덤으로 시킨다 (두근두근)", "score": {"N": 2}},
        ]
    },
    {
        "q": "친구가 짝사랑 고백했다가 차였다.\n나는 어떻게 위로하나?",
        "a": [
            {"text": "🤗 일단 안아주고 같이 울어준다", "score": {"F": 2}},
            {"text": "💬 공감 먼저, 그다음 이야기 들어줌", "score": {"F": 1}},
            {"text": "💡 현실적인 조언을 해준다", "score": {"T": 1}},
            {"text": "📊 다음엔 이렇게 해봐라 분석해줌", "score": {"T": 2}},
        ]
    },
    {
        "q": "여행 계획을 세운다면?",
        "a": [
            {"text": "🗓️ 날짜별 스케줄 엑셀로 정리", "score": {"J": 2}},
            {"text": "📍 주요 장소만 찍어두고 출발", "score": {"J": 1}},
            {"text": "🗺️ 숙소만 예약하고 현지에서 즉흥", "score": {"P": 1}},
            {"text": "🎒 그냥 가서 되는대로 논다", "score": {"P": 2}},
        ]
    },
    {
        "q": "단톡방에 메시지가 100개 쌓였다.\n확인하는 스타일은?",
        "a": [
            {"text": "📱 알림 뜨면 바로바로 확인", "score": {"E": 2, "J": 1}},
            {"text": "🔔 나중에 몰아서 한 번에 읽음", "score": {"I": 1, "P": 1}},
            {"text": "😶 읽고 답 안 하는 경우도 있음", "score": {"I": 1, "T": 1}},
            {"text": "🚫 아예 알림 꺼놓고 필요할 때만", "score": {"I": 2}},
        ]
    },
    {
        "q": "유튜브 알고리즘이 뭔가 이상한 영상을 추천해줬다.\n내 반응은?",
        "a": [
            {"text": "🤔 왜 이게 뜨지? 원리가 궁금해", "score": {"N": 2, "T": 1}},
            {"text": "😂 재밌어 보이면 일단 클릭", "score": {"N": 1, "F": 1}},
            {"text": "🙄 내가 좋아하는 거나 보여줘", "score": {"S": 1}},
            {"text": "❌ 관심 없음 표시하고 넘긴다", "score": {"S": 1, "J": 1}},
        ]
    },
    {
        "q": "팀 프로젝트에서 내 역할은?",
        "a": [
            {"text": "👑 자연스럽게 리더가 됨", "score": {"E": 1, "J": 2}},
            {"text": "🎨 아이디어 뱅크 담당", "score": {"N": 2, "F": 1}},
            {"text": "⚙️ 묵묵히 내 파트 완벽하게", "score": {"I": 1, "S": 1, "T": 1}},
            {"text": "🔥 분위기 메이커 + 중간 조율", "score": {"E": 1, "F": 2}},
        ]
    },
    {
        "q": "자기 전에 드는 생각은?",
        "a": [
            {"text": "💭 오늘 그 말은 왜 했지... (무한반추)", "score": {"I": 2, "N": 1}},
            {"text": "📝 내일 할 일 머릿속으로 정리", "score": {"J": 2, "S": 1}},
            {"text": "🌙 그냥 눕자마자 기절", "score": {"P": 1, "S": 1}},
            {"text": "🚀 갑자기 엄청난 아이디어가 떠오름", "score": {"N": 2}},
        ]
    },
]

# ── MBTI 결과 데이터 ──────────────────────────────────────────
RESULTS = {
    "INTJ": {
        "name": "전략가 🦅",
        "char": "🧙",
        "desc": "혼자서도 충분한 마법사 타입.\n계획은 완벽, 실행도 완벽.\n단, 감정 표현은... 업데이트 예정.",
        "stats": {"두뇌": 95, "공감": 45, "계획력": 92, "사교성": 30, "추진력": 88},
        "color": "#818cf8",
    },
    "INTP": {
        "name": "논리술사 🦉",
        "char": "🤓",
        "desc": "만물의 원리를 탐구하는 학자.\n'왜?' 라는 질문이 취미.\n근데 결론은 잘 안 냄.",
        "stats": {"두뇌": 98, "공감": 50, "계획력": 40, "사교성": 35, "추진력": 45},
        "color": "#34d399",
    },
    "ENTJ": {
        "name": "통솔자 🦁",
        "char": "👑",
        "desc": "태어날 때부터 리더.\n비효율을 못 참고 개선하고 싶어함.\n친구들이 왜인지 따라가게 됨.",
        "stats": {"두뇌": 90, "공감": 55, "계획력": 95, "사교성": 85, "추진력": 99},
        "color": "#fbbf24",
    },
    "ENTP": {
        "name": "변론가 🦊",
        "char": "🎭",
        "desc": "토론을 스포츠로 즐기는 타입.\n아이디어는 무한생성, 마무리는 글쎄...\n어디서든 분위기 장악.",
        "stats": {"두뇌": 92, "공감": 60, "계획력": 38, "사교성": 88, "추진력": 65},
        "color": "#f97316",
    },
    "INFJ": {
        "name": "옹호자 🦋",
        "char": "🔮",
        "desc": "사람 속을 꿰뚫어보는 예언자.\n공감 능력 만렙, 나 자신은 비밀.\n혼자 있는 시간이 필수 충전.",
        "stats": {"두뇌": 85, "공감": 96, "계획력": 75, "사교성": 55, "추진력": 72},
        "color": "#a78bfa",
    },
    "INFP": {
        "name": "중재자 🦄",
        "char": "🌸",
        "desc": "감수성 폭발 이상주의자.\n머릿속에 소설 열 편은 있음.\n세상을 더 따뜻하게 만들고 싶어함.",
        "stats": {"두뇌": 80, "공감": 95, "계획력": 35, "사교성": 48, "추진력": 50},
        "color": "#f472b6",
    },
    "ENFJ": {
        "name": "선도자 🦚",
        "char": "🌟",
        "desc": "모두를 이끄는 따뜻한 리더.\n친구 걱정을 내 걱정처럼 함.\n나 자신 챙기는 걸 배워야 함.",
        "stats": {"두뇌": 82, "공감": 97, "계획력": 80, "사교성": 95, "추진력": 85},
        "color": "#fb923c",
    },
    "ENFP": {
        "name": "활동가 🦜",
        "char": "🎨",
        "desc": "에너지 무한충전 자유영혼.\n새로운 거라면 일단 다 해보고 싶음.\n집중력은... 랜덤.",
        "stats": {"두뇌": 78, "공감": 90, "계획력": 30, "사교성": 97, "추진력": 70},
        "color": "#f43f5e",
    },
    "ISTJ": {
        "name": "청렴결백 🐢",
        "char": "📋",
        "desc": "신뢰와 책임의 아이콘.\n규칙을 소중히 여기고 약속은 무조건 지킴.\n변화는 조금... 천천히.",
        "stats": {"두뇌": 80, "공감": 62, "계획력": 98, "사교성": 40, "추진력": 85},
        "color": "#64748b",
    },
    "ISFJ": {
        "name": "수호자 🐨",
        "char": "🛡️",
        "desc": "조용히 모두를 챙기는 숨은 영웅.\n기억력 만렙, 특히 남 생일.\n자기 주장은 좀 더 해도 됨.",
        "stats": {"두뇌": 75, "공감": 93, "계획력": 85, "사교성": 52, "추진력": 65},
        "color": "#10b981",
    },
    "ESTJ": {
        "name": "경영자 🦬",
        "char": "⚙️",
        "desc": "현실주의 관리자.\n해야 할 일은 무조건 함.\n즉흥? 그런 거 없음.",
        "stats": {"두뇌": 83, "공감": 58, "계획력": 97, "사교성": 78, "추진력": 95},
        "color": "#0284c7",
    },
    "ESFJ": {
        "name": "집정관 🦩",
        "char": "🎀",
        "desc": "모임의 총무이자 분위기 메이커.\n모두가 행복해야 나도 행복.\n남 눈치 조금 덜 봐도 됨.",
        "stats": {"두뇌": 72, "공감": 94, "계획력": 80, "사교성": 96, "추진력": 78},
        "color": "#ec4899",
    },
    "ISTP": {
        "name": "장인 🐆",
        "char": "🔧",
        "desc": "말보다 행동, 이론보다 실전.\n문제 생기면 이미 고치고 있음.\n감정 공유는 비효율적이라 생각함.",
        "stats": {"두뇌": 87, "공감": 42, "계획력": 55, "사교성": 33, "추진력": 88},
        "color": "#78716c",
    },
    "ISFP": {
        "name": "모험가 🦊",
        "char": "🎵",
        "desc": "조용하지만 감성 폭발 예술가.\n자유를 사랑하고 틀에 갇히기 싫음.\n지금 이 순간을 가장 중요시함.",
        "stats": {"두뇌": 70, "공감": 88, "계획력": 32, "사교성": 55, "추진력": 58},
        "color": "#84cc16",
    },
    "ESTP": {
        "name": "사업가 🐅",
        "char": "⚡",
        "desc": "현실 속 스릴을 즐기는 행동파.\n계획? 몸이 먼저 움직임.\n어디서든 주목받는 타입.",
        "stats": {"두뇌": 80, "공감": 65, "계획력": 38, "사교성": 92, "추진력": 97},
        "color": "#ef4444",
    },
    "ESFP": {
        "name": "연예인 🦋",
        "char": "🎤",
        "desc": "삶 자체가 무대인 엔터테이너.\n분위기를 띄우는 건 타고남.\n내일 일은 내일 생각함.",
        "stats": {"두뇌": 68, "공감": 89, "계획력": 28, "사교성": 99, "추진력": 75},
        "color": "#f59e0b",
    },
}

def calc_mbti(answers):
    scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    for q_idx, a_idx in answers.items():
        for k, v in QUESTIONS[q_idx]["a"][a_idx]["score"].items():
            scores[k] += v
    mbti = ""
    mbti += "E" if scores["E"] >= scores["I"] else "I"
    mbti += "S" if scores["S"] >= scores["N"] else "N"
    mbti += "T" if scores["T"] >= scores["F"] else "F"
    mbti += "J" if scores["J"] >= scores["P"] else "P"
    return mbti

# ── Session state ─────────────────────────────────────────────
if "step"    not in st.session_state: st.session_state.step    = -1  # -1 = 인트로
if "answers" not in st.session_state: st.session_state.answers = {}

step    = st.session_state.step
answers = st.session_state.answers
total_q = len(QUESTIONS)

# ── 인트로 ────────────────────────────────────────────────────
if step == -1:
    st.markdown('<div class="title">✨ 나는 어떤 사람? ✨</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">8문항 픽셀 심리테스트</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="pixel-box" style="text-align:center;">
        <span style="font-size:60px;">🔮</span>
        <p style="color:#c4b5fd; font-size:16px; line-height:1.9; margin-top:12px;">
            솔직하게 답할수록<br>
            더 정확한 결과가 나와요!<br><br>
            <span style="color:#f472b6;">총 8문항</span> · 소요시간 <span style="color:#fbbf24;">1분</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎮  테스트 시작!", use_container_width=True):
        st.session_state.step = 0
        st.rerun()

# ── 질문 ──────────────────────────────────────────────────────
elif step < total_q:
    pct = int(step / total_q * 100)
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; font-size:12px; color:#a78bfa; margin-bottom:4px;">
        <span>진행률</span><span>{step}/{total_q}</span>
    </div>
    <div class="progress-wrap">
        <div class="progress-fill" style="width:{pct}%"></div>
    </div>
    """, unsafe_allow_html=True)

    q = QUESTIONS[step]
    st.markdown(f"""
    <div class="pixel-box">
        <div class="q-num">Q{step+1}.</div>
        <div class="q-text">{q['q']}</div>
    </div>
    """, unsafe_allow_html=True)

    for i, opt in enumerate(q["a"]):
        if st.button(opt["text"], key=f"q{step}_a{i}", use_container_width=True):
            st.session_state.answers[step] = i
            st.session_state.step += 1
            st.rerun()

# ── 결과 ──────────────────────────────────────────────────────
else:
    mbti   = calc_mbti(answers)
    result = RESULTS.get(mbti, RESULTS["INFP"])
    color  = result["color"]

    st.markdown(f"""
    <div class="pixel-box" style="border-color:{color};">
        <span class="pixel-char">{result['char']}</span>
        <div class="result-name">{result['name']}</div>
        <div class="result-type" style="color:{color};">{mbti}</div>
        <div class="result-desc">{result['desc']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='color:#a78bfa; font-size:13px; letter-spacing:2px; margin:16px 0 10px;'>📊 능력치</div>", unsafe_allow_html=True)
    st.markdown('<div class="pixel-box">', unsafe_allow_html=True)
    stats_html = ""
    for stat, val in result["stats"].items():
        stats_html += f"""
        <div class="stat-row">
            <span class="stat-label">{stat}</span>
            <div class="stat-bar-wrap">
                <div class="stat-bar-fill" style="width:{val}%; background:{color};"></div>
            </div>
            <span class="stat-val">{val}</span>
        </div>"""
    st.markdown(stats_html + "</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center; margin:16px 0 8px;">
        <span style="background:#2d1b4e; border:2px solid {color}; color:{color};
                     padding:8px 20px; border-radius:4px; font-size:14px; letter-spacing:2px;">
            나의 유형: {mbti} — {result['name']}
        </span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄  다시 테스트하기", use_container_width=True):
        st.session_state.step    = -1
        st.session_state.answers = {}
        st.rerun()
