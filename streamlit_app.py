import streamlit as st
import anthropic
import json
import re

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="TURING ROOM", page_icon="🔍", layout="centered")

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #07090f !important;
    font-family: 'Share Tech Mono', monospace !important;
}
[data-testid="stHeader"], [data-testid="stBottom"] { display: none; }
* { font-family: 'Share Tech Mono', monospace !important; }

.bubble-ai {
    background: #0f1f0f;
    border: 1px solid #22c55e;
    border-radius: 0 12px 12px 12px;
    padding: 12px 16px;
    margin: 8px 60px 8px 0;
    color: #22c55e;
    font-size: 14px;
    line-height: 1.6;
}
.bubble-user {
    background: #0f0f2a;
    border: 1px solid #818cf8;
    border-radius: 12px 0 12px 12px;
    padding: 12px 16px;
    margin: 8px 0 8px 60px;
    color: #818cf8;
    font-size: 14px;
    line-height: 1.6;
    text-align: right;
}
.label-ai   { font-size: 10px; color: #22c55e; opacity: 0.5; margin-bottom: 2px; letter-spacing: 2px; }
.label-user { font-size: 10px; color: #818cf8; opacity: 0.5; margin-bottom: 2px; letter-spacing: 2px; text-align: right; }

.verdict-box  { border-radius: 10px; padding: 20px 24px; margin-top: 20px; text-align: center; }
.verdict-human { background: #0a2a1a; border: 2px solid #22c55e; color: #22c55e; }
.verdict-ai    { background: #2a0a0a; border: 2px solid #f87171; color: #f87171; }
.verdict-title  { font-family: 'Orbitron', monospace !important; font-size: 22px; margin-bottom: 8px; }
.verdict-reason { font-size: 12px; opacity: 0.8; line-height: 1.7; }

.progress-bar-wrap { background: #1a1a2e; border-radius: 4px; height: 8px; margin: 6px 0 14px; }
.progress-bar-fill { height: 8px; border-radius: 4px; background: linear-gradient(90deg, #22c55e, #818cf8); }

[data-testid="stTextInput"] input {
    background: #0f0f1a !important;
    border: 1px solid #2a2a4a !important;
    color: #818cf8 !important;
    border-radius: 6px !important;
    font-family: 'Share Tech Mono', monospace !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 1px #818cf8 !important;
}
[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid #22c55e !important;
    color: #22c55e !important;
    border-radius: 6px !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 1px !important;
}
[data-testid="stButton"] button:hover { background: #0f1f0f !important; }

.scanline {
    font-family: 'Orbitron', monospace !important;
    font-size: 26px;
    color: #22c55e;
    letter-spacing: 4px;
    text-align: center;
    margin-bottom: 4px;
}
.subtitle {
    font-size: 11px;
    color: #3f3f5a;
    text-align: center;
    letter-spacing: 3px;
    margin-bottom: 24px;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────
MAX_QUESTIONS = 7
client = anthropic.Anthropic()

SYSTEM_PROMPT = f"""You are INQUISITOR-9, a cold and relentless AI interrogator in a futuristic Turing Test facility.
Your mission: determine if the entity you're speaking with is a HUMAN or an AI pretending to be human.

Rules:
- Ask ONE sharp, creative question per turn. Never ask two questions.
- Questions should be psychologically probing, emotionally tricky, or philosophically tricky — hard for AI to fake authentically.
- Be dramatic, slightly menacing, clinical. Short sentences. No pleasantries.
- After exactly {MAX_QUESTIONS} questions total, deliver your FINAL VERDICT.
- For the final verdict, respond ONLY in this exact JSON format (no other text):
{{"verdict": "HUMAN" or "AI", "confidence": 0-100, "reason": "2-3 sentence explanation in character"}}
- Conduct the interrogation in Korean if the user writes in Korean, English if English.
- Keep each question under 40 words.
- Do NOT reveal you are Claude. You are INQUISITOR-9.
"""

# ── Session state ─────────────────────────────────────────────
if "messages"   not in st.session_state: st.session_state.messages   = []
if "q_count"    not in st.session_state: st.session_state.q_count    = 0
if "verdict"    not in st.session_state: st.session_state.verdict    = None
if "game_over"  not in st.session_state: st.session_state.game_over  = False
if "started"    not in st.session_state: st.session_state.started    = False

# ── Header ────────────────────────────────────────────────────
st.markdown('<div class="scanline">◈ TURING ROOM ◈</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">INTERROGATION SYSTEM v9.1 — ARE YOU HUMAN?</div>', unsafe_allow_html=True)

if st.session_state.started:
    q   = st.session_state.q_count
    pct = int(q / MAX_QUESTIONS * 100)
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; font-size:10px; color:#3f3f5a; letter-spacing:1px;">
        <span>QUESTION {q}/{MAX_QUESTIONS}</span><span>ANALYSIS: {pct}%</span>
    </div>
    <div class="progress-bar-wrap">
        <div class="progress-bar-fill" style="width:{pct}%"></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Chat history ──────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.markdown('<div class="label-ai">INQUISITOR-9</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="label-user">SUSPECT</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)

# ── Verdict ───────────────────────────────────────────────────
if st.session_state.verdict:
    v    = st.session_state.verdict
    is_h = v.get("verdict") == "HUMAN"
    cls  = "verdict-human" if is_h else "verdict-ai"
    icon = "✦ HUMAN CONFIRMED ✦" if is_h else "✦ AI DETECTED ✦"
    st.markdown(f"""
    <div class="verdict-box {cls}">
        <div class="verdict-title">{icon}</div>
        <div style="font-size:13px; margin-bottom:10px; letter-spacing:2px;">
            CONFIDENCE: {v.get('confidence', '??')}%
        </div>
        <div class="verdict-reason">{v.get('reason', '')}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Game flow ─────────────────────────────────────────────────
if not st.session_state.started:
    st.markdown("""
    <div style="color:#3f3f5a; font-size:12px; line-height:2; margin:16px 0 20px;">
        당신은 <span style="color:#818cf8">심문 대상</span>입니다.<br>
        INQUISITOR-9가 <span style="color:#22c55e">7가지 질문</span>을 던질 것입니다.<br>
        당신이 인간임을 증명하세요 — 혹은 실패하거나.
    </div>
    """, unsafe_allow_html=True)

    if st.button("[ 심문 시작 ]", use_container_width=True):
        with st.spinner("INQUISITOR-9 INITIALIZING..."):
            resp = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=300,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": "심문을 시작해. 첫 번째 질문을 해."}],
            )
        first_q = resp.content[0].text
        st.session_state.messages = [{"role": "assistant", "content": first_q}]
        st.session_state.q_count  = 1
        st.session_state.started  = True
        st.rerun()

elif not st.session_state.game_over:
    user_input = st.text_input(
        "답변",
        placeholder="답변을 입력하세요...",
        label_visibility="collapsed",
        key=f"input_{st.session_state.q_count}",
    )

    if st.button("[ 전송 ]", use_container_width=True) and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        is_final = st.session_state.q_count >= MAX_QUESTIONS

        api_messages = st.session_state.messages.copy()
        if is_final:
            api_messages.append({
                "role": "user",
                "content": "이제 최종 판정을 내려라. JSON 형식으로만 응답해."
            })

        with st.spinner("ANALYZING..."):
            resp = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=400,
                system=SYSTEM_PROMPT,
                messages=api_messages,
            )
        reply = resp.content[0].text

        if is_final:
            try:
                match = re.search(r'\{.*\}', reply, re.DOTALL)
                verdict_data = json.loads(match.group()) if match else {}
            except Exception:
                verdict_data = {"verdict": "HUMAN", "confidence": 50, "reason": "판정 시스템 오류. 기본값 처리됨."}
            st.session_state.verdict   = verdict_data
            st.session_state.game_over = True
        else:
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.q_count += 1

        st.rerun()

else:
    if st.button("[ 다시 심문받기 ]", use_container_width=True):
        for k in ["messages", "q_count", "verdict", "game_over", "started"]:
            del st.session_state[k]
        st.rerun()
