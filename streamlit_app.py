import streamlit as st
from datetime import datetime, date, timedelta
import json

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="HABIT-OS",
    page_icon="⬛",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=VT323&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0b0b0f !important;
    font-family: 'Share Tech Mono', monospace !important;
}

[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { display: none; }
[data-testid="stBottom"] { display: none; }

h1, h2, h3, p, label, div, span {
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #111118 !important;
    border-radius: 8px !important;
    padding: 14px !important;
    border: 1px solid #2a2a3a !important;
}
[data-testid="stMetricLabel"] > div {
    font-size: 11px !important;
    letter-spacing: 2px !important;
    opacity: 0.55 !important;
}
[data-testid="stMetricValue"] > div {
    font-size: 28px !important;
    font-family: 'VT323', monospace !important;
}

/* ── Checkbox ── */
[data-testid="stCheckbox"] label {
    font-size: 14px !important;
    letter-spacing: 1.5px !important;
    cursor: pointer !important;
}
[data-testid="stCheckbox"] > label > div[data-testid="stMarkdownContainer"] p {
    font-size: 14px !important;
}

/* ── Progress bar ── */
[data-testid="stProgress"] > div > div {
    border-radius: 2px !important;
}

/* ── Divider ── */
hr { border-color: #1e1e2e !important; margin: 8px 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0b0b0f; }
::-webkit-scrollbar-thumb { background: #2a2a3a; border-radius: 2px; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #111118 !important;
    border: 1px solid #2a2a3a !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Color palette per habit ───────────────────────────────────
HABIT_COLORS = [
    {"accent": "#f472b6", "bg": "#2d1424", "border": "#7d2456"},  # pink
    {"accent": "#34d399", "bg": "#0d2620", "border": "#1a5c47"},  # emerald
    {"accent": "#60a5fa", "bg": "#0d1e35", "border": "#1a3d6b"},  # blue
    {"accent": "#fbbf24", "bg": "#2d2008", "border": "#6b4a0f"},  # amber
    {"accent": "#a78bfa", "bg": "#1e1435", "border": "#4a2d7a"},  # violet
    {"accent": "#fb923c", "bg": "#2d1708", "border": "#7a3d10"},  # orange
]

# ── Default habits ────────────────────────────────────────────
DEFAULT_HABITS = [
    {"name": "6AM WAKEUP",       "emoji": "🌅", "target": 7},
    {"name": "EXERCISE 30MIN",   "emoji": "🏃", "target": 5},
    {"name": "READ 20 PAGES",    "emoji": "📖", "target": 7},
    {"name": "NO SOCIAL MEDIA",  "emoji": "📵", "target": 7},
    {"name": "MEDITATE 10MIN",   "emoji": "🧘", "target": 6},
    {"name": "SLEEP BY 11PM",    "emoji": "🌙", "target": 7},
]

# ── Session state ─────────────────────────────────────────────
TODAY = date.today().isoformat()
WEEK = [(date.today() - timedelta(days=6 - i)).isoformat() for i in range(7)]
DAY_LABELS = [(date.today() - timedelta(days=6 - i)).strftime("%a").upper() for i in range(7)]

if "habits" not in st.session_state:
    st.session_state.habits = DEFAULT_HABITS

if "log" not in st.session_state:
    st.session_state.log = [
        {"ts": "08:02", "msg": "Session started. Good morning.", "col": "#34d399"},
        {"ts": "08:05", "msg": "Loading habit profile... OK",    "col": "#34d399"},
    ]

if "records" not in st.session_state:
    # Fake 6-day history + empty today
    import random
    random.seed(42)
    st.session_state.records = {}
    for d in WEEK[:-1]:
        st.session_state.records[d] = {
            i: random.random() > 0.3
            for i in range(len(st.session_state.habits))
        }
    st.session_state.records[TODAY] = {
        i: False for i in range(len(st.session_state.habits))
    }

records = st.session_state.records
today_rec = records.setdefault(TODAY, {i: False for i in range(len(st.session_state.habits))})

def add_log(msg, col="#34d399"):
    ts = datetime.now().strftime("%H:%M")
    st.session_state.log.append({"ts": ts, "msg": msg, "col": col})
    if len(st.session_state.log) > 20:
        st.session_state.log = st.session_state.log[-20:]

# ── Header ────────────────────────────────────────────────────
now_str = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center;
            padding:10px 0 6px; border-bottom:1px solid #1e1e2e; margin-bottom:18px;">
  <span style="color:#6366f1; font-size:22px; font-family:'VT323',monospace; letter-spacing:3px;">
    ⬛ HABIT-OS v2.4.1
  </span>
  <span style="color:#3f3f5a; font-size:11px; letter-spacing:2px;">{now_str}</span>
</div>
""", unsafe_allow_html=True)

# ── Stats row ─────────────────────────────────────────────────
done_today  = sum(1 for v in today_rec.values() if v)
total       = len(st.session_state.habits)
pct_today   = int(done_today / total * 100) if total else 0

all_done = sum(v for d in WEEK for v in records.get(d, {}).values())
all_total = len(WEEK) * total
week_pct = int(all_done / all_total * 100) if all_total else 0

streak = 0
for d in reversed(WEEK):
    day_rec = records.get(d, {})
    if day_rec and all(day_rec.values()):
        streak += 1
    else:
        break

c1, c2, c3, c4 = st.columns(4)
c1.metric("TODAY",   f"{done_today}/{total}")
c2.metric("STREAK",  f"{streak} days")
c3.metric("WEEK %",  f"{week_pct}%")
c4.metric("PERFECT DAYS", f"{sum(1 for d in WEEK if all(records.get(d,{}).values()))}")

st.markdown(f"""
<div style="margin:6px 0 18px;">
  <div style="font-size:10px; color:#3f3f5a; letter-spacing:2px; margin-bottom:4px;">
    TODAY'S PROGRESS — {pct_today}%
  </div>
  <div style="background:#1e1e2e; border-radius:3px; height:6px;">
    <div style="background: linear-gradient(90deg,#6366f1,#f472b6,#34d399);
                width:{pct_today}%; height:6px; border-radius:3px;
                transition: width 0.5s;"></div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Habit checkboxes ──────────────────────────────────────────
st.markdown("""
<div style="font-size:10px; color:#3f3f5a; letter-spacing:3px; margin-bottom:12px;">
  ► TODAY'S TASKS
</div>
""", unsafe_allow_html=True)

cols_left, cols_right = st.columns([3, 2])

with cols_left:
    for i, habit in enumerate(st.session_state.habits):
        col = HABIT_COLORS[i % len(HABIT_COLORS)]
        checked = today_rec.get(i, False)

        # Colored label with emoji
        label_html = f"""
        <div style="display:inline-flex; align-items:center; gap:8px; margin-bottom:2px;">
          <span style="color:{col['accent']}; font-size:14px;">{habit['emoji']}</span>
          <span style="color:{col['accent'] if not checked else '#3f3f5a'};
                       font-size:13px; letter-spacing:1.5px;
                       text-decoration:{'line-through' if checked else 'none'};">
            {habit['name']}
          </span>
        </div>
        """
        st.markdown(label_html, unsafe_allow_html=True)

        new_val = st.checkbox("", value=checked, key=f"habit_{i}_{TODAY}")
        if new_val != checked:
            today_rec[i] = new_val
            if new_val:
                add_log(f"COMPLETED: {habit['name']} [+1]", col["accent"])
            else:
                add_log(f"REVERTED: {habit['name']}", "#6366f1")
            st.rerun()

        st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

# ── Weekly grid ───────────────────────────────────────────────
with cols_right:
    st.markdown("""
    <div style="font-size:10px; color:#3f3f5a; letter-spacing:3px; margin-bottom:10px;">
      ► WEEKLY GRID
    </div>
    """, unsafe_allow_html=True)

    # Day headers
    header_html = '<div style="display:grid; grid-template-columns: 130px repeat(7,1fr); gap:4px; margin-bottom:4px;">'
    header_html += '<div></div>'
    for j, dl in enumerate(DAY_LABELS):
        is_today = j == 6
        header_html += f'<div style="text-align:center; font-size:9px; color:{"#f472b6" if is_today else "#3f3f5a"}; letter-spacing:1px;">{dl}</div>'
    header_html += '</div>'

    # Rows
    for i, habit in enumerate(st.session_state.habits):
        col = HABIT_COLORS[i % len(HABIT_COLORS)]
        row_html = '<div style="display:grid; grid-template-columns: 130px repeat(7,1fr); gap:4px; margin-bottom:4px;">'
        row_html += f'<div style="font-size:10px; color:{col["accent"]}; display:flex; align-items:center; opacity:0.8;">{habit["emoji"]} {habit["name"].split()[0]}</div>'
        for j, d in enumerate(WEEK):
            done = records.get(d, {}).get(i, False)
            is_today = j == 6
            if done:
                bg = col["accent"]
                border = col["accent"]
            elif is_today:
                bg = col["bg"]
                border = col["accent"]
            else:
                bg = "#1a1a28"
                border = "#2a2a3a"
            row_html += f'<div style="height:20px; border-radius:3px; background:{bg}; border:1px solid {border};"></div>'
        row_html += '</div>'
        header_html += row_html

    st.markdown(header_html, unsafe_allow_html=True)

st.markdown("---")

# ── System log ────────────────────────────────────────────────
st.markdown("""
<div style="font-size:10px; color:#3f3f5a; letter-spacing:3px; margin-bottom:8px;">
  ► SYSTEM LOG
</div>
""", unsafe_allow_html=True)

log_html = '<div style="background:#0d0d14; border:1px solid #1e1e2e; border-radius:8px; padding:12px; max-height:160px; overflow-y:auto;">'
for entry in reversed(st.session_state.log[-10:]):
    log_html += f"""
    <div style="font-size:11px; margin-bottom:3px; letter-spacing:0.5px;">
      <span style="color:#3f3f5a;">[{entry['ts']}]</span>
      <span style="color:{entry['col']}; margin-left:8px;">{entry['msg']}</span>
    </div>
    """
log_html += '</div>'
st.markdown(log_html, unsafe_allow_html=True)

# ── Prompt row ────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex; align-items:center; gap:6px; margin-top:14px; color:#3f3f5a; font-size:13px;">
  <span style="color:#6366f1;">root@habitOS:~$</span>
  <span style="display:inline-block; width:8px; height:15px; background:#6366f1; animation: none; vertical-align:middle;"></span>
</div>
""", unsafe_allow_html=True)

# ── Add habit expander ────────────────────────────────────────
with st.expander("[ + ADD NEW HABIT ]"):
    nc1, nc2, nc3 = st.columns([3, 1, 1])
    new_name = nc1.text_input("HABIT NAME", placeholder="e.g. DRINK 2L WATER", label_visibility="collapsed")
    new_emoji = nc2.text_input("EMOJI", value="⚡", label_visibility="collapsed")
    if nc3.button("ADD", use_container_width=True):
        if new_name:
            st.session_state.habits.append({"name": new_name.upper(), "emoji": new_emoji, "target": 7})
            for d in WEEK:
                records.setdefault(d, {})[len(st.session_state.habits) - 1] = False
            add_log(f"NEW HABIT ADDED: {new_name.upper()}", "#fbbf24")
            st.rerun()
