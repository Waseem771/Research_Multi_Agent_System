# --- STREAMLIT CLOUD SQLITE PATCH ---
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import streamlit as st
import os
import sys
import re
import threading
from coordinator import run_research_system
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# ==========================================
# 1. PAGE SETUP
# ==========================================
st.set_page_config(
    page_title="AI Research Team",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"   # sidebar collapsed by default — API key is hidden
)

# ==========================================
# 2. DESIGN SYSTEM — Swiss Modernism 2.0 / Dark
#    Colors: #0F172A bg | #111827 card | #1E3A5F primary
#    Typography: Inter (system-safe modern substitute for clean SaaS look)
# ==========================================
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root tokens ── */
:root {
    --color-background:       #0F172A;
    --color-card:             #111827;
    --color-card-alt:         #1E293B;
    --color-primary:          #1E3A5F;
    --color-secondary:        #2563EB;
    --color-accent:           #38BDF8;
    --color-foreground:       #F8FAFC;
    --color-muted:            #94A3B8;
    --color-border:           #334155;
    --color-success:          #10B981;
    --color-warning:          #F59E0B;
    --color-error:            #EF4444;
    --font-sans:              'Inter', system-ui, sans-serif;
    --font-mono:              'JetBrains Mono', monospace;
    --radius:                 10px;
    --radius-sm:              6px;
}

/* ── Global base ── */
html, body, [class*="css"] {
    font-family: var(--font-sans) !important;
    background-color: var(--color-background) !important;
    color: var(--color-foreground) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 3rem; max-width: 1400px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--color-card) !important;
    border-right: 1px solid var(--color-border);
}
section[data-testid="stSidebar"] * { color: var(--color-foreground) !important; }
section[data-testid="stSidebar"] input {
    background: var(--color-card-alt) !important;
    border: 1px solid var(--color-border) !important;
    color: var(--color-foreground) !important;
    border-radius: var(--radius-sm) !important;
}

/* ── Hero header ── */
.hero-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 60%, #2563EB22 100%);
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    padding: 2.5rem 2rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, #2563EB33, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--color-foreground);
    letter-spacing: -0.03em;
    margin: 0 0 0.4rem;
    line-height: 1.15;
}
.hero-subtitle {
    font-size: 1.0rem;
    color: var(--color-muted);
    margin: 0;
    font-weight: 400;
}

/* ── Agent badge pills ── */
.team-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1.2rem;
}
.agent-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--color-card-alt);
    border: 1px solid var(--color-border);
    border-radius: 999px;
    padding: 0.3rem 0.85rem;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--color-muted);
    white-space: nowrap;
}
.agent-pill .dot {
    width: 7px; height: 7px;
    background: var(--color-accent);
    border-radius: 50%;
    display: inline-block;
}

/* ── Input ── */
.stTextInput > div > div > input {
    background: var(--color-card) !important;
    border: 1.5px solid var(--color-border) !important;
    border-radius: var(--radius) !important;
    color: var(--color-foreground) !important;
    font-size: 1rem !important;
    padding: 0.7rem 1rem !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: var(--color-secondary) !important;
    box-shadow: 0 0 0 3px #2563EB22 !important;
}
.stTextInput label { color: var(--color-muted) !important; font-size: 0.85rem !important; }

/* ── Launch button ── */
.stButton > button {
    background: linear-gradient(135deg, #1E3A5F, #2563EB) !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 0.7rem 2rem !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s !important;
    letter-spacing: 0.01em;
    width: auto !important;
    min-width: 180px;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* ── Section headings ── */
.section-heading {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--color-foreground);
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--color-border);
}

/* ── Activity card ── */
.activity-card {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    padding: 1.2rem;
    min-height: 240px;
}

/* ── Status badge ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.88rem;
    font-weight: 600;
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    margin-bottom: 0.75rem;
}
.status-idle    { background: #1E293B; color: var(--color-muted); border: 1px solid var(--color-border); }
.status-running { background: #1E3A5F33; color: var(--color-accent); border: 1px solid var(--color-accent)33; }
.status-done    { background: #10B98122; color: var(--color-success); border: 1px solid #10B98144; }
.status-error   { background: #EF444422; color: var(--color-error);   border: 1px solid #EF444444; }

/* ── Log output ── */
.stCode, .stCodeBlock, code, pre {
    background: #0A0F1E !important;
    border: 1px solid var(--color-border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.78rem !important;
    color: #94D4FF !important;
}

/* ── Report card ── */
.report-card {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    padding: 2rem 2.5rem;
}

/* ── Report markdown typography ── */
.report-card h1 { font-size: 1.8rem; font-weight: 800; color: var(--color-foreground); margin-top: 0; border-bottom: 2px solid var(--color-secondary); padding-bottom: 0.5rem; }
.report-card h2 { font-size: 1.35rem; font-weight: 700; color: var(--color-accent); margin-top: 1.8rem; }
.report-card h3 { font-size: 1.1rem; font-weight: 600; color: var(--color-foreground); }
.report-card p  { font-size: 1rem; line-height: 1.75; color: #CBD5E1; }
.report-card ul, .report-card ol { color: #CBD5E1; line-height: 1.8; padding-left: 1.4rem; }
.report-card li::marker { color: var(--color-accent); }
.report-card strong { color: var(--color-foreground); }
.report-card blockquote {
    border-left: 3px solid var(--color-secondary);
    margin: 1rem 0; padding: 0.5rem 1rem;
    background: var(--color-card-alt);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    color: var(--color-muted);
    font-style: italic;
}

/* ── Markdown general ── */
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: var(--color-foreground) !important; }
.stMarkdown p, .stMarkdown li { color: #CBD5E1 !important; line-height: 1.75; }
.stMarkdown strong { color: var(--color-foreground) !important; }
.stMarkdown a { color: var(--color-accent) !important; }

/* ── Expander (API key) ── */
.streamlit-expanderHeader {
    background: var(--color-card) !important;
    border: 1px solid var(--color-border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--color-muted) !important;
    font-size: 0.85rem !important;
}
.streamlit-expanderContent {
    background: var(--color-card-alt) !important;
    border: 1px solid var(--color-border) !important;
    border-top: none !important;
}

/* ── Alert/error boxes ── */
.stAlert { border-radius: var(--radius) !important; }

/* ── Columns gap ── */
[data-testid="stHorizontalBlock"] { gap: 1.5rem; }

/* ── Divider ── */
hr { border-color: var(--color-border) !important; }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. LIVE LOG CAPTURE
# ==========================================
class StreamToExpander:
    def __init__(self, status_placeholder, log_placeholder):
        self.status_placeholder = status_placeholder
        self.log_placeholder = log_placeholder
        self.logs = []
        self.ctx = get_script_run_ctx()

    def write(self, text):
        if text.strip():
            if self.ctx:
                add_script_run_ctx(threading.current_thread(), self.ctx)
            self.logs.append(text)
            # show last 30 lines
            self.log_placeholder.code("".join(self.logs[-30:]), language="markdown")
            if "Agent:" in text:
                agent_name = text.split("Agent:")[-1].strip().split("\n")[0]
                self.status_placeholder.markdown(
                    f'<div class="status-badge status-running">'
                    f'<span style="width:8px;height:8px;background:#38BDF8;border-radius:50%;display:inline-block;animation:pulse 1.5s infinite"></span>'
                    f'🤖 {agent_name}</div>'
                    f'<style>@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}</style>',
                    unsafe_allow_html=True
                )

    def flush(self):
        pass


# ==========================================
# 4. SIDEBAR — API key (collapsed by default)
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    st.markdown("**☁️ Provider:** Azure OpenAI")
    st.markdown("---")
    st.markdown("**Your AI Team**")
    agents_info = [
        ("🕵️", "Researcher",   "gpt-4.1-nano-2025-04-14",  "Web search & facts"),
        ("📚", "Lit Reviewer", "gpt-4.1-nano-2025-04-14",  "Academic papers"),
        ("📊", "Analyst",      "gpt-5.2-2025-12-11",       "Deep analysis"),
        ("🔍", "Fact Checker", "gpt-4.1-mini-2025-04-14",  "Verification"),
        ("👔", "Orchestrator", "gpt-5.2-2025-12-11",       "Final synthesis"),
    ]
    for icon, name, model, role in agents_info:
        st.markdown(
            f"**{icon} {name}**  \n"
            f"<span style='font-size:0.75rem;color:#64748B'>`{model}`  •  {role}</span>",
            unsafe_allow_html=True
        )
        st.markdown("")


# ==========================================
# 5. HERO HEADER
# ==========================================
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🔬 AI Research Team</div>
    <p class="hero-subtitle">
        Powered by 5 specialized AI agents — Research · Literature Review · Analysis · Fact-Check · Synthesis
    </p>
    <div class="team-row">
        <span class="agent-pill"><span class="dot"></span>🕵️ Researcher</span>
        <span class="agent-pill"><span class="dot"></span>📚 Lit Reviewer</span>
        <span class="agent-pill"><span class="dot"></span>📊 Analyst</span>
        <span class="agent-pill"><span class="dot"></span>🔍 Fact Checker</span>
        <span class="agent-pill"><span class="dot"></span>👔 Orchestrator</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 6. INPUT AREA
# ==========================================
col_input, col_btn = st.columns([5, 1])
with col_input:
    topic = st.text_input(
        "Research topic",
        placeholder="e.g.  The future of quantum computing in drug discovery",
        label_visibility="collapsed"
    )
with col_btn:
    launch = st.button("🚀 Launch", use_container_width=True)

st.markdown("---")


# ==========================================
# 7. MAIN LOGIC
# ==========================================
if launch:
    if not os.environ.get("GROQ_API_KEY"):
        st.error("⚠️ Please enter your Groq API Key above or in the sidebar before launching.")
    elif not topic.strip():
        st.warning("⚠️ Please enter a research topic first.")
    else:
        # ── Layout: activity log left | report right ──
        left, right = st.columns([1, 2], gap="large")

        with left:
            st.markdown('<div class="section-heading">📡 Live Agent Activity</div>', unsafe_allow_html=True)
            with st.container():
                status_placeholder = st.empty()
                status_placeholder.markdown(
                    '<div class="status-badge status-running">'
                    '<span style="width:8px;height:8px;background:#38BDF8;border-radius:50%;display:inline-block"></span>'
                    '⏳ Initialising agents…</div>',
                    unsafe_allow_html=True
                )
                log_placeholder = st.empty()

        with right:
            st.markdown('<div class="section-heading">📑 Final Report</div>', unsafe_allow_html=True)
            report_placeholder = st.empty()
            report_placeholder.markdown(
                '<div style="color:#475569;font-size:0.95rem;padding:2rem 0">Report will appear here once the team finishes…</div>',
                unsafe_allow_html=True
            )

        # ── Run the crew ──
        saved_stdout = sys.stdout
        sys.stdout = StreamToExpander(status_placeholder, log_placeholder)

        result = None
        try:
            result = run_research_system(topic.strip())
            status_placeholder.markdown(
                '<div class="status-badge status-done">✅ Research complete</div>',
                unsafe_allow_html=True
            )
        except Exception as e:
            status_placeholder.markdown(
                f'<div class="status-badge status-error">❌ Error: {e}</div>',
                unsafe_allow_html=True
            )
        finally:
            sys.stdout = saved_stdout

        # ── Render report ──
        if result:
            report_text = str(result)
            with right:
                report_placeholder.empty()
                st.markdown('<div class="report-card">', unsafe_allow_html=True)
                st.markdown(report_text)
                st.markdown('</div>', unsafe_allow_html=True)

                # Download button
                st.download_button(
                    label="⬇️ Download Report (.md)",
                    data=report_text,
                    file_name=f"research_{topic[:40].replace(' ','_')}.md",
                    mime="text/markdown"
                )
