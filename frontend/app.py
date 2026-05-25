# =============================================================================
# CRITICAL PLATFORM PATCHES — must run before all other imports
# =============================================================================
import os, sys
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
try:
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

from dotenv import load_dotenv
load_dotenv()

import re
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.engine import ZeravaneEngine

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(page_title="ZeravaneAI", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    :root {
        --neon-cyan: #00D9FF;
        --neon-green: #00FF41;
        --neon-orange: #FF6B35;
        --dark-bg: #0A0E27;
        --text-primary: #E0E6FF;
    }
    .main { background-color: #0F1419; color: var(--text-primary); }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stButton > button {
        border: 1.5px solid var(--neon-cyan) !important;
        background-color: rgba(0, 20, 40, 0.8) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        box-shadow: 0 0 8px rgba(0, 217, 255, 0.3) !important;
    }
    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.7) !important;
    }
    @keyframes pulse-green {
        0%, 100% { box-shadow: 0 0 8px rgba(0,255,65,0.4); border-color: rgba(0,255,65,0.6); }
        50% { box-shadow: 0 0 20px rgba(0,255,65,0.8); border-color: rgba(0,255,65,1); }
    }
    @keyframes pulse-cyan {
        0%, 100% { box-shadow: 0 0 8px rgba(0,217,255,0.4); border-color: rgba(0,217,255,0.6); }
        50% { box-shadow: 0 0 20px rgba(0,217,255,0.8); border-color: rgba(0,217,255,1); }
    }
    @keyframes pulse-orange {
        0%, 100% { box-shadow: 0 0 8px rgba(255,107,53,0.4); border-color: rgba(255,107,53,0.6); }
        50% { box-shadow: 0 0 20px rgba(255,107,53,0.8); border-color: rgba(255,107,53,1); }
    }
    .badge-green {
        display: inline-block; padding: 8px 16px; border-radius: 6px;
        border: 1.5px solid rgba(0,255,65,0.6); background: rgba(0,50,30,0.7);
        color: #00FF41; font-weight: 600; font-size: 14px;
        animation: pulse-green 2s ease-in-out infinite; margin: 8px 0;
    }
    .badge-cyan {
        display: inline-block; padding: 8px 16px; border-radius: 6px;
        border: 1.5px solid rgba(0,217,255,0.6); background: rgba(0,30,60,0.7);
        color: #00D9FF; font-weight: 600; font-size: 14px;
        animation: pulse-cyan 2s ease-in-out infinite; margin: 8px 0;
    }
    .badge-orange {
        display: inline-block; padding: 8px 16px; border-radius: 6px;
        border: 1.5px solid rgba(255,107,53,0.6); background: rgba(60,20,0,0.7);
        color: #FF6B35; font-weight: 600; font-size: 14px;
        animation: pulse-orange 2s ease-in-out infinite; margin: 8px 0;
    }
    .bd-banner {
        background: linear-gradient(135deg, rgba(0,20,50,0.9), rgba(0,40,80,0.9));
        border: 1px solid rgba(0,217,255,0.3);
        border-radius: 10px; padding: 12px 20px; margin: 10px 0;
        text-align: center;
    }
    .cache-hit-banner {
        background: rgba(0, 40, 20, 0.6);
        border: 1px solid rgba(0, 255, 65, 0.3);
        border-radius: 8px; padding: 8px 16px; margin: 6px 0;
        font-size: 13px; color: #00FF41;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<h1 style='text-align:center; color:#00D9FF; text-shadow: 0 0 16px rgba(0,217,255,0.6);
           letter-spacing:2px; margin-bottom:2px;'>
⚡ ZeravaneAI — Web Data UNLOCKED
</h1>
<p style='text-align:center; color:#00D9FF; font-size:11px; letter-spacing:2px;
          opacity:0.7; margin-top:0;'>
POWERED BY BRIGHT DATA × GEMINI 2.5 FLASH | SINGLETON VANGUARD | LABLAB.AI HACKATHON 2026
</p>
""", unsafe_allow_html=True)

st.markdown("""
<div class='bd-banner'>
    <span style='color:#00D9FF; font-weight:700; letter-spacing:1px;'>
        🌐 BRIGHT DATA INTEGRATION ACTIVE
    </span>
    <span style='color:#aaa; font-size:12px; margin-left:12px;'>
        Web Unlocker · SERP API · Bot-Proof Scraping · Geo-Unblocked Access
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =============================================================================
# ENGINE + SESSION STATE
# =============================================================================

@st.cache_resource
def get_engine():
    return ZeravaneEngine()

engine = get_engine()

# Initialise session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_url" not in st.session_state:
    st.session_state.last_url = ""

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Agent Config")
    st.markdown(f"""
    <div style='background:rgba(0,20,40,0.6); border:1px solid rgba(0,217,255,0.2);
                border-radius:8px; padding:12px; font-size:12px; color:#aaa;'>
    <b style='color:#00D9FF;'>Bright Data Stack</b><br>
    • Web Unlocker (Tier 1)<br>
    • SERP API (Tier 2)<br>
    • Standard Fallback (Tier 3)<br><br>
    <b style='color:#00D9FF;'>AI Engine</b><br>
    • Model: gemini-2.5-flash<br>
    • Vector DB: ChromaDB<br>
    • Chunks: 3000 chars / 300 overlap<br>
    • 2MB stream cap per URL
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    bd_status = "🟢 Active" if engine.bd_enabled else "🟡 Demo Mode"
    st.write(f"**Bright Data:** {bd_status}")

    if engine._cached_url:
        st.markdown(f"""
        <div class='cache-hit-banner'>
        ✅ Cached: <code style='font-size:11px;'>{engine._cached_url[:50]}{'...' if len(engine._cached_url) > 50 else ''}</code>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🗑️ Clear Cache", use_container_width=True):
        try:
            engine.chroma_client.delete_collection(name=engine._cached_collection)
        except Exception:
            pass
        engine._cached_url = None
        st.session_state.last_url = ""
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='font-size:11px; color:#555; text-align:center;'>
    Built for<br><b style='color:#00D9FF;'>Web Data UNLOCKED Hackathon</b><br>
    Bright Data × Lablab.ai 2026<br>
    Team: Singleton Vanguard
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# MAIN LAYOUT
# =============================================================================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🌐 Ingestion Target")
    target_url = st.text_input(
        "Target URL (Bright Data bypasses bot detection on any public site)",
        placeholder="https://docs.github.com/en/rest",
        value=st.session_state.last_url,
    )

with col2:
    st.subheader("🔧 System Context")
    url_changed = target_url.strip() != st.session_state.last_url.strip()
    if url_changed and target_url.strip():
        st.info("🔄 New URL detected — will scrape fresh on next query.")
    elif engine._cached_url and not url_changed:
        st.success("✅ URL cached — skipping re-scrape for this query.")
    else:
        st.caption(
            "ZeravaneAI uses Bright Data's Web Unlocker to access any public URL — "
            "including JavaScript-heavy and geo-blocked pages."
        )

# Agent status
st.markdown("#### 📊 Agent Status")
col_s1, col_s2 = st.columns([2, 1])

with col_s1:
    if not target_url or not target_url.strip():
        st.markdown(
            "<div class='badge-cyan'>🔵 [Standby] Core Engine Ready — Enter URL to activate Web Intelligence</div>",
            unsafe_allow_html=True,
        )
    elif engine.bd_enabled:
        st.markdown(
            "<div class='badge-green'>🟢 [Active] Bright Data Web Intelligence Online — Bot-Proof Scraping Ready</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='badge-orange'>🟡 [Demo Mode] Standard Scraping — Add Bright Data credentials for full power</div>",
            unsafe_allow_html=True,
        )

with col_s2:
    if engine.bd_enabled:
        st.markdown(
            "<div class='badge-green'>🛡️ Bot Detection: BYPASSED</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='badge-cyan'>ℹ️ Demo Mode Active</div>",
            unsafe_allow_html=True,
        )

# Query input
user_query = st.text_area(
    "💬 Ask any technical or development question",
    placeholder="How does authentication work on this platform? Explain the API endpoints...",
    height=100,
)

force_rescrape = st.checkbox(
    "🔄 Force re-scrape (bypass URL cache)",
    value=False,
    help="Tick this to re-scrape the URL even if it was already cached.",
)

st.markdown("---")

# =============================================================================
# EXECUTE
# =============================================================================
if st.button("🚀 Execute Agent Search", use_container_width=True):
    if not user_query.strip():
        st.error("Please enter a query before executing the agent search.")
    else:
        url_to_use = target_url.strip() if target_url and target_url.strip() else None

        spinner_msg = (
            "🌐 Bright Data fetching live web data... parsing nodes... updating vector index..."
            if url_to_use else
            "🧠 ZeravaneAI processing query on base model weights..."
        )

        with st.spinner(spinner_msg):
            response_text, context_payload, scrape_method = engine.execute_live_agent_query(
                user_query=user_query,
                target_url=url_to_use,
                force_rescrape=force_rescrape,
            )

        # Update session cache tracker
        if url_to_use:
            st.session_state.last_url = url_to_use

        # Append to chat history
        st.session_state.chat_history.append({
            "query": user_query,
            "response": response_text,
            "scrape_method": scrape_method,
            "url": url_to_use,
        })

        st.markdown("### 🤖 ZeravaneAI Response")

        if url_to_use:
            st.markdown(
                f"<small style='color:#555;'>Data Source: "
                f"<b style='color:#00D9FF;'>{scrape_method}</b></small>",
                unsafe_allow_html=True,
            )

        st.markdown(response_text)

        # Context auditor
        with st.expander("🔍 Inspect Retrieved Vector Context (Bright Data Payload)"):
            st.text_area(
                "Raw context injected into Gemini:",
                value=(
                    context_payload
                    if context_payload
                    else "[No context retrieved — running on base model weights]"
                ),
                disabled=True,
                height=180,
            )

# =============================================================================
# CHAT HISTORY
# =============================================================================
if st.session_state.chat_history:
    st.markdown("---")
    with st.expander(f"📜 Session History ({len(st.session_state.chat_history)} queries)"):
        for i, entry in enumerate(reversed(st.session_state.chat_history), 1):
            st.markdown(
                f"**Q{i}:** {entry['query']}  \n"
                f"<small style='color:#555;'>Source: {entry['scrape_method']} | "
                f"URL: {entry['url'] or 'None'}</small>",
                unsafe_allow_html=True,
            )
            st.markdown(entry["response"][:400] + "..." if len(entry["response"]) > 400 else entry["response"])
            st.markdown("---")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<p style='text-align:center; font-size:11px; color:#333;'>
ZeravaneAI — Built by <b style='color:#00D9FF;'>Franklin Josva</b> |
Team: Singleton Vanguard |
Bright Data × Lablab.ai Web Data UNLOCKED Hackathon 2026
</p>
""", unsafe_allow_html=True)
