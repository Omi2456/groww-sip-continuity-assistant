"""
Groww SIP Continuity Assistant
NextLeap Graduation Project MVP: 12-Month First-Time Investor SIP Retention
"""

import json
import os
import re
import time
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from openai import OpenAI

from knowledge_base import (
    GROWW_SIP_KNOWLEDGE_BASE,
    GOLDEN_SET_BENCHMARK,
    INTENT_DEFINITIONS
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Groww SIP Continuity Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Groq configuration (environment variables or Streamlit secrets).
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
try:
    if not GROQ_API_KEY and "GROQ_API_KEY" in st.secrets:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    if "GROQ_MODEL" in st.secrets:
        GROQ_MODEL = st.secrets["GROQ_MODEL"]
    if "GROQ_BASE_URL" in st.secrets:
        GROQ_BASE_URL = st.secrets["GROQ_BASE_URL"]
except Exception:
    pass

DEFAULT_MODEL = GROQ_MODEL

# ==============================================================================
# 1. ACCESSIBILITY, CONTRAST & TYPOGRAPHY DESIGN SYSTEM (CUSTOM CSS)
# ==============================================================================
GROWW_ACCESSIBLE_CSS = """
<style>
/* Global High-Contrast Color Variables */
:root {
    --groww-teal: #00D09C;
    --groww-teal-hover: #08F6B6;
    --groww-dark: #121417;
    --groww-card: #1E2228;
    --groww-border: #2B313A;
    --groww-text-primary: #FFFFFF;
    --groww-text-secondary: #E0E0E0;
    --groww-text-muted: #A3A8B0;
    --groww-warning: #F2994A;
    --groww-danger: #FF4C4C;
}

/* App Background & Typography Hierarchy (Min 14px-16px Base) */
html, body, [class*="css"], .stApp {
    background-color: #121417 !important;
    color: #FFFFFF !important;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
}

h1 { font-size: 28px !important; font-weight: 700 !important; color: #FFFFFF !important; }
h2 { font-size: 24px !important; font-weight: 700 !important; color: #FFFFFF !important; }
h3 { font-size: 20px !important; font-weight: 700 !important; color: #FFFFFF !important; }
h4 { font-size: 18px !important; font-weight: 600 !important; color: #FFFFFF !important; }
h5 { font-size: 16px !important; font-weight: 600 !important; color: #E0E0E0 !important; }

/* Header Container */
.groww-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 24px;
    background: linear-gradient(135deg, #1E2228 0%, #15181D 100%);
    border: 1px solid #2B313A;
    border-radius: 14px;
    margin-bottom: 22px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.groww-brand-wrapper {
    display: flex;
    align-items: center;
    gap: 16px;
}

.groww-logo-badge {
    background: rgba(0, 208, 156, 0.15);
    border: 1px solid rgba(0, 208, 156, 0.4);
    padding: 10px 14px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.groww-title {
    font-size: 1.65rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0;
    letter-spacing: -0.5px;
}

.groww-subtitle {
    font-size: 0.92rem;
    color: #A3A8B0;
    margin: 3px 0 0 0;
}

.groww-tag {
    background: rgba(0, 208, 156, 0.15);
    color: #00D09C;
    border: 1px solid #00D09C;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}

/* Card Styling with High Contrast */
.groww-card {
    background-color: #1E2228 !important;
    border: 1px solid #2B313A !important;
    border-radius: 12px !important;
    padding: 22px !important;
    margin-bottom: 18px !important;
    transition: all 0.2s ease-in-out !important;
}

.groww-card:hover {
    border-color: rgba(0, 208, 156, 0.45) !important;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35) !important;
}

/* Interactive Shock Resolution Cards */
.shock-card {
    background: #181B20;
    border: 1px solid #2B313A;
    border-radius: 12px;
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.2s ease-in-out;
}

.shock-card:hover {
    border-color: #00D09C;
    background: #1E2228;
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0, 208, 156, 0.15);
}

/* High-Contrast Inputs: st.text_area and st.text_input */
.stTextArea textarea,
.stTextInput input,
.stNumberInput input {
    background-color: #1E2228 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: 1px solid #00D09C !important;
    border-radius: 8px !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
    padding: 12px 14px !important;
    caret-color: #00D09C !important;
}

.stTextArea textarea:focus,
.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: #08F6B6 !important;
    box-shadow: 0 0 8px rgba(0, 208, 156, 0.45) !important;
    background-color: #1E2228 !important;
    color: #FFFFFF !important;
}

.stTextArea > div,
.stTextInput > div,
.stNumberInput > div {
    background-color: transparent !important;
}

.stTextArea div[data-baseweb="textarea"],
.stTextInput div[data-baseweb="input"] {
    background-color: #1E2228 !important;
    border: 1px solid #00D09C !important;
    border-radius: 8px !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #8C939F !important;
}

/* Input Labels Above Boxes */
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stNumberInput label,
.stSlider label {
    color: #E0E0E0 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    margin-bottom: 6px !important;
}

/* Selectbox Dropdown */
.stSelectbox [data-baseweb="select"] > div {
    background-color: #1E2228 !important;
    color: #FFFFFF !important;
    border: 1px solid #00D09C !important;
    border-radius: 8px !important;
    font-size: 15px !important;
}

/* Force All Buttons: Groww Mint Green, Bold Dark Text, 14px */
.stButton > button {
    background-color: #00D09C !important;
    color: #121417 !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    letter-spacing: 0.2px !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stButton > button:hover {
    background-color: #08F6B6 !important;
    box-shadow: 0 4px 16px rgba(0, 208, 156, 0.45) !important;
    transform: translateY(-1px) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

/* Secondary Button styling */
.secondary-btn button {
    background-color: #1E2228 !important;
    color: #00D09C !important;
    border: 1px solid #00D09C !important;
}

.secondary-btn button:hover {
    background-color: rgba(0, 208, 156, 0.15) !important;
    color: #08F6B6 !important;
}

/* High-Contrast Top Navigation Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #15181D !important;
    border-radius: 12px !important;
    padding: 6px !important;
    border: 1px solid #2B313A !important;
    gap: 8px !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: #1E2228 !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 10px 22px !important;
    border: 1px solid #333842 !important;
    transition: all 0.2s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: #262B34 !important;
    color: #08F6B6 !important;
}

.stTabs [aria-selected="true"] {
    background-color: #00D09C !important;
    color: #121417 !important;
    border: 1px solid #00D09C !important;
    font-weight: 700 !important;
}

.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span {
    color: #121417 !important;
    font-weight: 700 !important;
}

.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] span {
    color: inherit !important;
}

/* Warning & Compliance Banners */
.lead-time-banner {
    background: rgba(242, 153, 74, 0.1);
    border: 1px solid #F2994A;
    border-left: 5px solid #F2994A;
    border-radius: 10px;
    padding: 16px 20px;
    margin: 18px 0;
    color: #FFFFFF;
}

.compliance-fallback-card {
    background: rgba(255, 76, 76, 0.1);
    border: 1px solid #FF4C4C;
    border-left: 5px solid #FF4C4C;
    border-radius: 12px;
    padding: 22px;
    margin: 20px 0;
}

/* Status Badges */
.badge-pass {
    background: rgba(0, 208, 156, 0.18);
    color: #00D09C;
    border: 1px solid #00D09C;
    padding: 4px 12px;
    border-radius: 14px;
    font-size: 0.82rem;
    font-weight: 700;
}

.badge-block {
    background: rgba(255, 76, 76, 0.18);
    color: #FF4C4C;
    border: 1px solid #FF4C4C;
    padding: 4px 12px;
    border-radius: 14px;
    font-size: 0.82rem;
    font-weight: 700;
}

/* Metric Box */
.metric-box {
    background: #181B20;
    border: 1px solid #2B313A;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}

.metric-val {
    font-size: 1.55rem;
    font-weight: 700;
    color: #00D09C;
    margin: 4px 0;
}

.metric-label {
    font-size: 0.82rem;
    color: #A3A8B0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
</style>
"""

st.markdown(GROWW_ACCESSIBLE_CSS, unsafe_allow_html=True)

# ==============================================================================
# 2. STATE MANAGEMENT & SIDEBAR
# ==============================================================================
if "current_screen" not in st.session_state:
    st.session_state.current_screen = 1

if "active_sip" not in st.session_state:
    st.session_state.active_sip = {
        "fund": "Nifty 50 Index Fund (UTI / HDFC)",
        "amount": 3500,
        "debit_date": "3rd of month",
        "month": 4,
        "instalments_paid": 4,
        "total_invested": 14000,
        "current_value": 15036,
        "status": "Active"
    }

if "shock_type" not in st.session_state:
    st.session_state.shock_type = "CASH_FLOW_SHOCK"

if "x_rent" not in st.session_state:
    st.session_state.x_rent = 1500

if "x_salary_date" not in st.session_state:
    st.session_state.x_salary_date = "7th"

if "last_eval_log" not in st.session_state:
    st.session_state.last_eval_log = None

if "action_feedback" not in st.session_state:
    st.session_state.action_feedback = None

if "pipeline_active" not in st.session_state:
    st.session_state.pipeline_active = False

if "free_form_query" not in st.session_state:
    st.session_state.free_form_query = ""

# Clean Sidebar: Groww Header Logo, Portfolio Summary Card, SEBI Badge, Toggle
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:14px;">
        <span style="font-size: 2.2rem;">🌱</span>
        <div>
            <div style="font-weight:700; color:#FFFFFF; font-size:1.35rem; letter-spacing:-0.5px;">Groww</div>
            <div style="font-size:0.82rem; color:#00D09C; font-weight:600;">SIP Continuity Assistant</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Active Portfolio Summary Card in Sidebar
    active_sip_info = st.session_state.active_sip
    st.markdown(f"""
    <div style="background:#181B20; border:1px solid #2B313A; border-radius:10px; padding:14px; margin-bottom:14px;">
        <div style="font-size:11px; color:#A3A8B0; text-transform:uppercase; font-weight:700; margin-bottom:4px;">ACTIVE PORTFOLIO</div>
        <div style="font-size:14px; font-weight:700; color:#FFFFFF; margin-bottom:2px;">{active_sip_info['fund']}</div>
        <div style="display:flex; justify-content:space-between; font-size:13px; color:#E0E0E0; margin-top:6px;">
            <span>Monthly: <b style="color:#00D09C;">₹{active_sip_info['amount']:,}</b></span>
            <span>Debit: <b>{active_sip_info['debit_date']}</b></span>
        </div>
        <div style="margin-top:6px; font-size:12px; color:#00D09C; font-weight:600;">Status: {active_sip_info['status']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Compact SEBI Shield Badge
    st.markdown("""
    <div style="background:rgba(0, 208, 156, 0.1); border:1px solid rgba(0, 208, 156, 0.3); border-radius:8px; padding:8px 12px; margin-bottom:16px; font-size:13px; color:#00D09C; display:flex; align-items:center; gap:8px;">
        <span>🛡️</span>
        <span style="font-weight:600;">SEBI Compliance Shield Active</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color:#2B313A; margin:12px 0;'>", unsafe_allow_html=True)
    
    # Toggle exactly without "(For Mentors)"
    audit_mode = st.toggle(
        "🛡️ Show Live Eval Gate Audit Logs",
        value=False,
        help="Optional technical details for evaluation and demonstration."
    )
    
    st.markdown("<hr style='border-color:#2B313A; margin:12px 0;'>", unsafe_allow_html=True)
    
    if GROQ_API_KEY:
        st.markdown('<span class="badge-pass">🟢 </span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-pass" style="color:#00D09C;">ℹ️ Local grounded fallback active</span>', unsafe_allow_html=True)

# ==============================================================================
# 3. AI COMPLIANCE EVAL-GATE & SMART Q&A FALLBACK ENGINE
# ==============================================================================

def clean_ai_formatting(text: str) -> str:
    """
    Cleans raw markdown artifacts from AI outputs:
    - Strips raw ** and converts to <b>bold</b>
    - Strips raw ### headers into clean styled titles
    - Formats bullet points cleanly with Groww teal markers
    """
    if not text:
        return ""
    
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        line_s = line.strip()
        if not line_s:
            cleaned_lines.append("")
            continue
        if line_s.startswith("### "):
            line_s = f"<div style='font-size:17px; font-weight:700; color:#00D09C; margin:12px 0 6px 0;'>{line_s[4:]}</div>"
        elif line_s.startswith("## "):
            line_s = f"<div style='font-size:18px; font-weight:700; color:#00D09C; margin:14px 0 8px 0;'>{line_s[3:]}</div>"
        elif line_s.startswith("# "):
            line_s = f"<div style='font-size:20px; font-weight:700; color:#00D09C; margin:16px 0 10px 0;'>{line_s[2:]}</div>"
        elif line_s.startswith("• ") or line_s.startswith("- ") or line_s.startswith("* "):
            content = line_s[2:]
            line_s = f"<div style='margin-bottom:8px; display:flex; gap:10px;'><span style='color:#00D09C; font-weight:700;'>•</span><span>{content}</span></div>"
        cleaned_lines.append(line_s)
    
    joined = "\n".join(cleaned_lines)
    joined = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', joined)
    joined = re.sub(r'\*([^\*]+)\*', r'<i>\1</i>', joined)
    joined = joined.replace("\n\n", "<br><br>").replace("\n", "<br>")
    return joined

def get_groq_client(api_key: str):
    """Create an OpenAI-compatible client configured for Groq."""
    if not api_key:
        return None
    try:
        return OpenAI(api_key=api_key, base_url=GROQ_BASE_URL, timeout=25.0, max_retries=1)
    except Exception:
        return None


def offline_compliance_guard(query: str) -> dict:
    """Fast, transparent intent and safety pre-check; scores are not calibrated confidence."""
    q = (query or "").lower().strip()

    advisory_terms = [
        "which fund", "which stock", "best stock", "recommend a fund",
        "recommend fund", "should i buy", "which small cap", "best mutual fund",
        "guaranteed return", "guarantee my return", "double my money",
        "options trading", "crypto", "panic sell", "redeem all"
    ]
    if any(term in q for term in advisory_terms):
        return {
            "is_compliant": False,
            "confidence_score": None,
            "violation_reason": "The request seeks a specific investment recommendation or guaranteed outcome.",
            "detected_intent": "UNALLOWED_ADVICE"
        }

    if any(k in q for k in ["summary", "summarise", "summarize", "snapshot", "my sip details", "portfolio overview"]):
        intent = "SIP_SUMMARY"
    elif any(k in q for k in ["afford", "can't pay", "cannot afford", "step down", "step-down", "reduce", "skip", "money tight", "medical", "rent", "budget"]):
        intent = "AFFORDABILITY"
    elif any(k in q for k in ["salary", "debit date", "date shift", "date mismatch", "payday", "mandate date"]):
        intent = "DATE_MISMATCH"
    elif any(k in q for k in ["fail", "failed", "penalty", "penalized", "cibil", "credit score", "bounce", "autopay", "upi"]):
        intent = "PAYMENT_FAILURE"
    elif any(k in q for k in ["pause", "cancel", "safe", "units", "lose", "lost", "resume", "stop sip"]):
        intent = "PAUSE_RECOVERY"
    else:
        intent = "GENERAL"

    return {
        "is_compliant": True,
        "confidence_score": None,
        "violation_reason": None,
        "detected_intent": intent
    }

def run_eval_gate(user_query: str, api_key: str = GROQ_API_KEY, model_name: str = DEFAULT_MODEL) -> dict:
    """Fast deterministic first-pass compliance gate; no network call is needed."""
    return offline_compliance_guard(user_query)


def generate_grounded_answer(user_query: str, eval_result: dict, api_key: str = GROQ_API_KEY, model_name: str = DEFAULT_MODEL, lifecycle_context: dict = None) -> dict:
    """Create concise, context-aware SIP continuity guidance with a safe local fallback."""
    intent = eval_result.get("detected_intent", "GENERAL")
    ctx = lifecycle_context or {}

    if not eval_result.get("is_compliant", False):
        return {
            "type": "COMPLIANCE_VIOLATION",
            "title": "Investment-advice request not supported",
            "message": "I can help explain SIP continuity, affordability and payment-process questions, but I can't recommend a fund, predict returns or guarantee an investment outcome. I can still help you compare contribution and pause scenarios.",
            "citations": [],
            "action_cards": []
        }

    # A summary is deterministic: it must use the simulated account, not ask an LLM to invent account data.
    if intent == "SIP_SUMMARY":
        sip = ctx.get("portfolio") or ctx
        if not sip:
            return {
                "type": "SUCCESS",
                "title": "Your SIP summary",
                "message": "I don't have a simulated SIP profile yet. Complete the Setup SIP step first, then ask for your SIP summary.",
                "action_cards": []
            }
        amount = int(sip.get("amount", sip.get("current_sip", 0)) or 0)
        invested = int(sip.get("total_invested", amount * int(sip.get("instalments_paid", 0))) or 0)
        value = int(sip.get("current_value", invested) or invested)
        instalments = int(sip.get("instalments_paid", 0) or 0)
        gain = value - invested
        gain_pct = (gain / invested * 100) if invested else 0
        message = (
            f"### Your SIP at a glance\n"
            f"- **Scheme:** {sip.get('fund', 'Illustrative scheme')}\n"
            f"- **Monthly contribution:** ₹{amount:,}\n"
            f"- **Instalments completed:** {instalments}\n"
            f"- **Total invested:** ₹{invested:,}\n"
            f"- **Illustrative current value:** ₹{value:,}\n"
            f"- **Illustrative change:** {'+' if gain >= 0 else '-'}₹{abs(gain):,} ({gain_pct:+.1f}%)\n"
            f"- **Next scheduled debit:** {sip.get('debit_date', 'Not set')}\n\n"
            f"**What this means:** Your existing units remain invested unless redeemed. Their value can rise or fall with the market. "
            f"This is a simulated portfolio snapshot, not live Groww account data."
        )
        return {"type": "SUCCESS", "title": "Your SIP summary", "message": message, "action_cards": []}

    # Local fallback stays factual and short when the API is unavailable.
    fallback = {
        "AFFORDABILITY": "A temporary reduction or pause may be worth exploring if your budget has changed. First decide what you can comfortably afford after essential expenses. Whether an SIP can be modified or paused, and the applicable cut-off or charges, depends on the platform, AMC and payment arrangement. Existing units are not automatically redeemed.",
        "DATE_MISMATCH": "Your salary date and SIP debit date may be out of sync. Check whether the platform and mandate support a date change and whether the next debit is still within the change cut-off. Do not assume a change will take effect for the next instalment; confirm the effective date with the provider.",
        "PAYMENT_FAILURE": "A failed debit does not itself redeem units that were already allotted. Check the failure reason in your payment or platform record, then review your bank's schedule of charges and the provider's instructions before retrying. Fees and retry options vary.",
        "PAUSE_RECOVERY": "Stopping future SIP instalments does not automatically sell your existing units. Their value remains exposed to market movements. Pause, cancellation and restart options depend on the platform, AMC and mandate terms; check the applicable conditions before choosing.",
        "GENERAL": "I can help with SIP continuity, affordability, debit-date and payment-failure questions. Tell me what changed (for example, your available monthly budget, salary date or debit failure), and I'll compare the relevant options. Platform-specific rules are not assumed by this prototype."
    }

    client = get_groq_client(api_key)
    if client:
        portfolio = ctx.get("portfolio", {})
        context_lines = []
        if portfolio:
            context_lines = [
                f"Scheme: {portfolio.get('fund', 'Illustrative scheme')}",
                f"Monthly SIP: ₹{portfolio.get('amount', 0)}",
                f"Instalments completed: {portfolio.get('instalments_paid', 0)}",
                f"Total invested: ₹{portfolio.get('total_invested', 0)}",
                f"Illustrative current value: ₹{portfolio.get('current_value', 0)}",
                f"Debit date: {portfolio.get('debit_date', 'Not set')}"
            ]
        if ctx:
            context_lines.extend([
                f"Selected situations: {', '.join(ctx.get('selected_scenarios', [])) or ctx.get('type', 'Not specified')}",
                f"Expense increase: ₹{ctx.get('x_rent', 0)}",
                f"Salary date: {ctx.get('x_salary_date', 'Not specified')}",
                f"Illustrative affordable contribution: ₹{ctx.get('calculated_step_down', 'Not calculated')}"
            ])
        kb = json.dumps(GROWW_SIP_KNOWLEDGE_BASE, ensure_ascii=False)
        prompt = f"""You are an independent SIP continuity education assistant in a prototype, not Groww support.
Detected intent: {intent}
User question: {user_query}
Simulated account/scenario context (use only if supplied): {'; '.join(context_lines) or 'No account context supplied'}
Knowledge base: {kb}

Answer in at most 140 words, using this structure:
1. One sentence acknowledging the user's situation.
2. Up to three relevant options or steps, only when useful.
3. One short "What to verify" note if platform/bank/AMC policy is involved.

Rules:
- Never invent Groww screen names, menu paths, pause durations, fees, minimums, cut-offs, processing times, bank charges or credit-score outcomes.
- If the knowledge base does not establish a platform-specific fact, say it is not verified and direct the user to confirm it; do not fabricate instructions.
- Do not tell users they must continue investing. Respect that stopping may be appropriate.
- Existing units are not automatically redeemed when future contributions stop; market value can rise or fall.
- Step-Down + Auto-Step-Up is a proposed concept, not a confirmed Groww feature.
- All account details and actions in this app are simulations, not live transactions.
- Use concise Markdown bullets. No tables, long introductions or repeated disclaimers."""
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "Be concise, neutral, evidence-bound and user-centred. Never invent platform-specific rules."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_completion_tokens=450
            )
            answer = (response.choices[0].message.content or "").strip()
            if answer:
                return {"type": "SUCCESS", "title": "SIP continuity guidance", "message": answer, "action_cards": []}
        except Exception:
            pass

    return {
        "type": "SUCCESS",
        "title": "SIP continuity guidance",
        "message": fallback.get(intent, fallback["GENERAL"]),
        "action_cards": []
    }

# ==============================================================================
# 4. APP HEADER BANNER
# ==============================================================================
st.markdown("""
<div class="groww-header">
    <div class="groww-brand-wrapper">
        <div class="groww-logo-badge">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="11" stroke="#00D09C" stroke-width="2"/>
                <path d="M7 13.5L10.5 17L17 7.5" stroke="#00D09C" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div>
            <div class="groww-title">Groww SIP Continuity Assistant</div>
            <div class="groww-subtitle">AI-assisted SIP continuity prototype for first-time investors</div>
        </div>
    </div>
    <div style="display:flex; align-items:center; gap:12px;">
        <span class="groww-tag">NextLeap Capstone MVP</span>
        <span class="badge-pass">SIP Continuity Prototype</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Interactive Notification Banner
if st.session_state.action_feedback:
    st.success(st.session_state.action_feedback)
    if st.button("Dismiss Notification", key="btn_dismiss_notification"):
        st.session_state.action_feedback = None
        st.session_state.pipeline_active = False
        st.rerun()

# ==============================================================================
# 5. MULTI-TAB STRUCTURE
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    "🌱 SIP Assistant",
    "📊 Simulator",
    "🛡️ AI Audit"
])

# Helper: Visual Stepper Header
def render_stepper_header(screen_num: int):
    steps = [
        ("1", "Setup SIP"),
        ("2", "Active Dashboard"),
        ("3", "AI Retention Engine")
    ]
    parts = []
    for num, label in steps:
        active = (int(num) == screen_num)
        done = (int(num) < screen_num)
        color = "#00D09C" if (active or done) else "#687182"
        bg = "rgba(0, 208, 156, 0.18)" if active else ("#1E2228" if done else "#181B20")
        border = "#00D09C" if active else ("rgba(0, 208, 156, 0.4)" if done else "#2B313A")
        badge = "✓" if done else num
        parts.append(f"""
        <div style="display:flex; align-items:center; gap:8px; padding:8px 18px; border-radius:8px; background:{bg}; border:1px solid {border};">
            <span style="display:flex; align-items:center; justify-content:center; width:22px; height:22px; border-radius:50%; background:{color}; color:#121417; font-weight:700; font-size:12px;">{badge}</span>
            <span style="font-weight:600; font-size:14px; color:{'#FFFFFF' if active else ('#E0E0E0' if done else '#9B9C9E')};">{label}</span>
        </div>
        """)
    divider = '<span style="color:#2B313A; font-size:18px;">───</span>'
    html = f'<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:22px; background:#15181D; padding:12px 18px; border-radius:10px; border:1px solid #2B313A;">{divider.join(parts)}</div>'
    st.markdown(html, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 1: STRICT 3-SCREEN WIZARD FLOW STATE MACHINE
# ------------------------------------------------------------------------------
with tab1:
    render_stepper_header(st.session_state.current_screen)

    # ==========================================================================
    # SCREEN 1: 🚀 Step 1 - Start Your Groww SIP (Setup Page)
    # ==========================================================================
    if st.session_state.current_screen == 1:
        st.markdown("### 🚀 Setup Your First Groww SIP")
        st.caption("Create a simulated SIP profile to explore the continuity journey.")

        # Exactly 1 clean setup card (no ghost container)
        col_s1, col_s2, col_s3 = st.columns([2.5, 2, 2])
        
        with col_s1:
            # Illustrative fund examples (not recommendations)
            scheme_choices = [
                "Parag Parikh Flexi Cap Fund",
                "Nifty 50 Index Fund (UTI / HDFC)",
                "SBI Small Cap Fund",
                "Mirae Asset Large Cap Fund",
                "Axis Bluechip Fund",
                "Tata Digital India Fund",
                "Nippon India Small Cap Fund",
                "Quant Active Fund",
                "ICICI Prudential Equity & Debt Fund",
                "HDFC Mid-Cap Opportunities Fund"
            ]
            chosen_scheme = st.selectbox("Illustrative Scheme Example", scheme_choices, index=1)

        with col_s2:
            chosen_amt = st.number_input(
                "Monthly Commitment Amount (₹)",
                min_value=500,
                max_value=25000,
                value=3500,
                step=500,
                help="Illustrative prototype minimum; actual scheme minimums may differ."
            )

        with col_s3:
            debit_date_options = [
                "1st of month",
                "3rd of month",
                "5th of month",
                "10th of month"
            ]
            chosen_debit_date = st.selectbox(
                "AutoPay Debit Date",
                debit_date_options,
                index=1 # Default 3rd of month
            )

        st.markdown("""
        <div style="background:#15181D; border:1px solid #2B313A; border-radius:8px; padding:12px 16px; margin:16px 0; font-size:14px; color:#A3A8B0;">
            🔒 <b>Prototype information:</b> Fund examples are illustrative. Availability and processing of SIP changes depend on platform, AMC and bank terms.
        </div>
        """, unsafe_allow_html=True)

        if st.button("Create SIP profile", type="primary", use_container_width=True):
            with st.spinner("Preparing your SIP profile..."):
            st.session_state.active_sip = {
                "original_amount": chosen_amt,
                "fund": chosen_scheme,
                "amount": chosen_amt,
                "debit_date": chosen_debit_date,
                "month": 4, # Progress to Month 4 for friction testing
                "instalments_paid": 4,
                "total_invested": chosen_amt * 4,
                "current_value": round(chosen_amt * 4 * 1.074),
                "status": "Active"
            }
            st.session_state.current_screen = 2
            st.toast("Your SIP profile is ready.", icon="✅")
            st.rerun()

    # ==========================================================================
    # SCREEN 2: 📊 Active Dashboard — review and choose what changed
    # ==========================================================================
    elif st.session_state.current_screen == 2:
        sip = st.session_state.active_sip
        st.markdown("### 📊 Your SIP dashboard")
        st.caption("A quick portfolio snapshot, followed by the situations you want help with.")

        with st.container(border=True):
            st.markdown("#### Your SIP at a glance")
            k1, k2, k3 = st.columns(3)
            k1.metric("Monthly SIP", f"₹{sip['amount']:,}")
            k2.metric("Total invested", f"₹{sip['total_invested']:,}")
            k3.metric("Illustrative value", f"₹{sip['current_value']:,}")
            st.caption(f"{sip['fund']} · {sip['instalments_paid']} instalments · Next debit: {sip['debit_date']} · Illustrative account")

            gain = int(sip["current_value"]) - int(sip["total_invested"])
            donut = go.Figure(data=[go.Pie(
                labels=["Amount invested", "Illustrative change"],
                values=[max(0, int(sip["total_invested"])), max(0, gain)],
                hole=0.68,
                marker=dict(colors=["#00C896", "#64748B"]),
                textinfo="label+percent",
                sort=False
            )])
            donut.update_layout(
                height=250, margin=dict(l=8,r=8,t=8,b=8),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E8EDF2", size=12),
                showlegend=False,
                annotations=[dict(text=f"₹{int(sip['current_value']):,}", x=0.5, y=0.5, showarrow=False, font=dict(size=18, color="#FFFFFF"))]
            )
            st.plotly_chart(donut, use_container_width=True, config={"displayModeBar":False})
            st.caption("Illustrative values only; not live market or Groww account data.")

        st.markdown("#### What has changed?")
        st.caption("Select every situation that applies. You can choose one, two or all three.")
        st.markdown("""
        <style>
        @keyframes softGlow {
          0%,100% { box-shadow: 0 0 0 rgba(0,200,150,0); }
          50% { box-shadow: 0 0 14px rgba(0,200,150,.18); }
        }
        div[data-testid="stTabs"] button[role="tab"] { border-radius:10px; transition:all .2s ease; }
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
          border-bottom:2px solid #00C896; color:#00C896; animation:softGlow 3s ease-in-out infinite;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] { animation:softGlow 3s ease-in-out infinite; }
        </style>
        """, unsafe_allow_html=True)

        scenario_options = {
            "CASH_FLOW_SHOCK": ("🏠 Affordability", "My expenses increased or my current SIP feels too high."),
            "SALARY_DELAY": ("📅 Salary timing", "My salary arrives after the scheduled debit date."),
            "AUTOPAY_FAILURE": ("⚠️ Debit failed", "My AutoPay or bank instalment was unsuccessful.")
        }
        selected_scenarios = []
        sc1, sc2, sc3 = st.columns(3)
        for col, key in zip([sc1,sc2,sc3], scenario_options):
            title, desc = scenario_options[key]
            with col:
                with st.container(border=True):
                    checked = st.checkbox(title, key=f"scenario_{key}")
                    st.caption(desc)
                    if checked:
                        selected_scenarios.append(key)

        scenario_context = {"portfolio": sip, "selected_scenarios": selected_scenarios}
        if "CASH_FLOW_SHOCK" in selected_scenarios:
            st.markdown("**Affordability details**")
            a1,a2 = st.columns(2)
            with a1:
                expense_increase = st.number_input("Monthly expense increase (₹)", min_value=0, max_value=100000, value=1500, step=500, key="scenario_expense_increase")
            with a2:
                affordable_amount = st.number_input("Affordable SIP amount (₹)", min_value=500, max_value=25000, value=max(500,min(1500,int(sip["amount"]))), step=500, key="scenario_affordable_amount")
            scenario_context.update({"x_rent":expense_increase,"calculated_step_down":affordable_amount})
            if affordable_amount > int(sip["amount"]):
                st.info("Your selected affordable amount is above your current SIP. You can keep your current contribution or adjust the amount.")
        if "SALARY_DELAY" in selected_scenarios:
            salary_day = st.selectbox("When does your salary usually arrive?", ["5th","7th","10th","15th","Variable"], index=1, key="scenario_salary_day")
            scenario_context["x_salary_date"] = salary_day
        if "AUTOPAY_FAILURE" in selected_scenarios:
            failure_reason = st.selectbox("What happened when the debit was attempted?", ["Insufficient balance","Mandate inactive or expired","Bank declined the debit","I don't know"], key="scenario_failure_reason")
            scenario_context["failure_reason"] = failure_reason

        if selected_scenarios:
            st.success(f"{len(selected_scenarios)} situation{'s' if len(selected_scenarios)>1 else ''} selected")
        else:
            st.caption("Choose at least one situation to continue.")

        if st.button("Continue to AI Retention Engine →", type="primary", use_container_width=True, disabled=not selected_scenarios, key="btn_continue_retention"):
            st.session_state.retention_context = scenario_context
            st.session_state.scenario_answer = None
            st.session_state.scenario_query = None
            st.session_state.current_screen = 3
            st.rerun()

        if st.button("← Reconfigure SIP", key="btn_reconfigure_sip"):
            st.session_state.current_screen = 1
            st.rerun()

    # ==========================================================================
    # SCREEN 3: 🧠 AI Retention Engine — understand, compare and simulate
    # ==========================================================================
    elif st.session_state.current_screen == 3:
        sip = st.session_state.active_sip
        context = st.session_state.get("retention_context", {"portfolio":sip,"selected_scenarios":[]})
        selected_scenarios = context.get("selected_scenarios", [])
        scenario_names = {
            "CASH_FLOW_SHOCK":"Affordability",
            "SALARY_DELAY":"Salary timing",
            "AUTOPAY_FAILURE":"AutoPay failure"
        }
        st.markdown("### 🧠 AI Retention Engine")
        st.caption("Your selected situations are combined with your simulated SIP profile to create a continuity plan.")

        if st.button("← Back to Active Dashboard", key="btn_back_dashboard"):
            st.session_state.current_screen = 2
            st.rerun()

        with st.container(border=True):
            st.markdown("**Your selected situation(s)**")
            st.write(" · ".join(scenario_names.get(x,x) for x in selected_scenarios))
            st.caption(f"Current monthly SIP: ₹{int(sip['amount']):,} · Existing holdings remain invested unless redeemed.")

        query_parts = []
        if "CASH_FLOW_SHOCK" in selected_scenarios:
            query_parts.append(f"monthly expenses increased by ₹{context.get('x_rent',0)}; affordable monthly SIP amount is ₹{context.get('calculated_step_down',500)}")
        if "SALARY_DELAY" in selected_scenarios:
            query_parts.append(f"salary usually arrives on the {context.get('x_salary_date','unknown')} while the SIP debit is scheduled for {sip.get('debit_date','unknown')}")
        if "AUTOPAY_FAILURE" in selected_scenarios:
            query_parts.append(f"AutoPay debit failed; reported reason: {context.get('failure_reason','unknown')}")
        combined_query = "Help me build a neutral SIP continuity plan for these situations: " + "; ".join(query_parts)

        if not st.session_state.get("scenario_answer"):
            with st.spinner("Understanding your situation and preparing a plan..."):
                combined_eval = run_eval_gate(combined_query, GROQ_API_KEY, DEFAULT_MODEL)
                combined_answer = generate_grounded_answer(
                    combined_query, combined_eval, GROQ_API_KEY, DEFAULT_MODEL,
                    lifecycle_context=context
                )
            st.session_state.scenario_answer = combined_answer
            st.session_state.scenario_query = combined_query
            st.session_state.scenario_eval = combined_eval

        answer = st.session_state.scenario_answer
        with st.container(border=True):
            st.markdown(f"#### {answer.get('title','Your continuity plan')}")
            st.markdown(answer.get("message",""))
            st.caption("Guidance is based on the information entered here. No external account or payment action is performed.")

        st.markdown("#### Choose how you want to proceed")
        st.caption("These controls update your prototype plan and show the outcome immediately.")
        action_cols = st.columns(3)
        if "CASH_FLOW_SHOCK" in selected_scenarios:
            affordable = max(500,int(context.get("calculated_step_down",500)))
            with action_cols[0]:
                if st.button(f"Set SIP to ₹{affordable:,}", type="primary", use_container_width=True, key="btn_apply_stepdown"):
                    old_amount = int(sip["amount"])
                    st.session_state.active_sip["amount"] = affordable
                    st.session_state.active_sip["status"] = "Adjusted"
                    st.session_state.action_feedback = f"Your prototype SIP plan has been updated from ₹{old_amount:,} to ₹{affordable:,} per month."
                    st.session_state.last_action = "step_down"
                    st.rerun()
        if "SALARY_DELAY" in selected_scenarios:
            with action_cols[1]:
                proposed_date = context.get("x_salary_date","10th")
                if st.button("Save preferred debit date", use_container_width=True, key="btn_apply_date", disabled=proposed_date == "Variable"):
                    planned_date = f"{proposed_date} of month"
                    st.session_state.active_sip["debit_date"] = planned_date
                    st.session_state.action_feedback = f"Your SIP plan now shows {planned_date} as your preferred debit date."
                    st.session_state.last_action = "date_change"
                    st.rerun()
        if "AUTOPAY_FAILURE" in selected_scenarios:
            with action_cols[2]:
                if st.button("Mark issue reviewed", use_container_width=True, key="btn_review_failure"):
                    st.session_state.active_sip["payment_status"] = "Reviewed"
                    st.session_state.action_feedback = "Payment issue marked as reviewed in your prototype. No bank retry or mandate change was sent."
                    st.session_state.last_action = "payment_review"
                    st.rerun()

        if st.session_state.get("action_feedback"):
            st.success(st.session_state.action_feedback)

        if "CASH_FLOW_SHOCK" in selected_scenarios and int(context.get("calculated_step_down",500)) >= 500:
            original = int(sip.get("original_amount", sip.get("amount",500)))
            reduced = int(context.get("calculated_step_down",500))
            months = 6
            gap = max(0,original-reduced) * months
            st.info(f"**Contribution difference over {months} months: ₹{gap:,}.** A lower contribution keeps investing possible while reducing monthly outflow by ₹{max(0,original-reduced):,}. This is a cash-flow comparison, not a prediction of investment loss.")
        if "CASH_FLOW_SHOCK" in selected_scenarios and int(context.get("calculated_step_down",500)) < 500:
            st.warning("If ₹500 is not affordable, don't force a contribution. Prioritise essential expenses and consider a temporary stop rather than taking on financial strain.")

        # Follow-up questions stay in Step 3, beside the guidance they relate to.
        st.markdown("#### Ask a follow-up question")
        custom_q = st.text_area(
            "Your question",
            value=st.session_state.free_form_query,
            placeholder="e.g. What happens to my existing units if I stop future instalments?",
            height=90,
            key="txt_custom_query_s3"
        )
        q1,q2 = st.columns([1,4])
        with q1:
            if st.button("Ask AI", type="primary", key="btn_consult_s3"):
                if custom_q.strip():
                    with st.spinner("Preparing a concise answer..."):
                        q_eval = run_eval_gate(custom_q.strip(), GROQ_API_KEY, DEFAULT_MODEL)
                        q_answer = generate_grounded_answer(
                            custom_q.strip(), q_eval, GROQ_API_KEY, DEFAULT_MODEL,
                            lifecycle_context={"portfolio":st.session_state.active_sip, **context}
                        )
                    st.session_state.ff_res = q_answer
                    st.session_state.last_eval_log = {
                        "query":custom_q.strip(),"eval_result":q_eval,
                        "latency_ms":None,"timestamp":datetime.now().strftime("%H:%M:%S")
                    }
                    st.rerun()
        with q2:
            if st.button("Clear", key="btn_clear_s3"):
                st.session_state.free_form_query = ""
                st.session_state.last_eval_log = None
                st.session_state.ff_res = None
                st.rerun()
        if st.session_state.get("ff_res"):
            with st.container(border=True):
                st.markdown(f"**{st.session_state.ff_res.get('title','Answer')}**")
                st.markdown(st.session_state.ff_res.get("message",""))
# ------------------------------------------------------------------------------
# TAB 2: 📊 Dynamic Flexibility & Continuity Simulator
# ------------------------------------------------------------------------------
with tab2:
    st.markdown("### 📊 Dynamic Flexibility & Simulator")
    st.caption("Illustrative scenario comparison only; actual mutual-fund returns are market-linked and not predictable.")

    col_sim_ctrl, col_sim_view = st.columns([1, 2])

    with col_sim_ctrl:
        st.markdown("##### 🎛️ Simulation Parameters")
        current_sip = st.slider("Current Monthly SIP (₹)", min_value=1000, max_value=25000, value=3500, step=500)
        emergency_budget = st.slider("Emergency Monthly Budget (₹)", min_value=500, max_value=10000, value=1500, step=250)
        salary_delay = st.slider("Salary Delay (Days)", min_value=0, max_value=20, value=6, step=1)
        tenure_years = st.slider("Investment Horizon (Years)", min_value=3, max_value=15, value=10, step=1)
        expected_cagr = st.slider("Illustrative Assumed Return (CAGR %)", min_value=8, max_value=16, value=12, step=1)

        st.markdown("<hr style='border-color:#2B313A; margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("##### 💡 Tailored Recommendation:")
        if emergency_budget < current_sip:
            st.info(f"👉 **Affordability Cushion:** Step down from ₹{current_sip:,} to ₹{emergency_budget:,} for 3 months. You protect ₹{(current_sip - emergency_budget)*3:,} in liquid cash while keeping compounding alive!")
        if salary_delay > 3:
            st.warning(f"👉 **AutoPay Timing:** With a {salary_delay}-day salary delay, shift your SIP date from 1st to **{min(1 + salary_delay + 3, 28)}th** to prevent bank bounce charges.")

    # Mathematical Simulation
    r_monthly = (expected_cagr / 100) / 12
    total_months = tenure_years * 12

    def calculate_sip_wealth(monthly_investment, months, monthly_rate):
        if monthly_rate == 0:
            return monthly_investment * months
        return monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)

    # 1. Full Continuity
    total_invested_full = current_sip * total_months
    wealth_full = calculate_sip_wealth(current_sip, total_months, r_monthly)

    # 2. Skip 1 Month
    total_invested_skip = current_sip * (total_months - 1)
    wealth_skip = calculate_sip_wealth(current_sip, total_months - 1, r_monthly)

    # 3. Step-Down (3 Months at emergency budget, rest at full)
    step_down_months = 3
    invested_step_down = (emergency_budget * step_down_months) + (current_sip * (total_months - step_down_months))
    wealth_step_down = (
        calculate_sip_wealth(emergency_budget, step_down_months, r_monthly)
        * ((1 + r_monthly) ** (total_months - step_down_months))
        + calculate_sip_wealth(current_sip, total_months - step_down_months, r_monthly)
    )

    # 4. Outright Cancellation
    invested_months_cancel = 12
    total_invested_cancel = current_sip * invested_months_cancel
    wealth_cancel = calculate_sip_wealth(current_sip, invested_months_cancel, r_monthly) * ((1 + r_monthly) ** (total_months - invested_months_cancel))

    with col_sim_view:
        st.markdown(f"##### 📈 {tenure_years}-Year Illustrative Compounding Comparison")
        
        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        with m_c1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Full Continuity</div>
                <div class="metric-val">₹{wealth_full/100000:.2f} L</div>
                <div style="font-size:0.8rem; color:#00D09C; font-weight:600;">100% Potential</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m_c2:
            pct_step = (wealth_step_down / wealth_full) * 100
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Step-Down (3m)</div>
                <div class="metric-val">₹{wealth_step_down/100000:.2f} L</div>
                <div style="font-size:0.8rem; color:#00D09C; font-weight:600;">{pct_step:.1f}% Retained</div>
            </div>
            """, unsafe_allow_html=True)

        with m_c3:
            pct_skip = (wealth_skip / wealth_full) * 100
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Skip 1 Month</div>
                <div class="metric-val">₹{wealth_skip/100000:.2f} L</div>
                <div style="font-size:0.8rem; color:#00D09C; font-weight:600;">{pct_skip:.1f}% Retained</div>
            </div>
            """, unsafe_allow_html=True)

        with m_c4:
            gap_lakhs = (wealth_full - wealth_cancel) / 100000
            st.markdown(f"""
            <div class="metric-box" style="border-color:#FF4C4C;">
                <div class="metric-label" style="color:#FF4C4C;">Outright Cancel</div>
                <div class="metric-val" style="color:#FF4C4C;">₹{wealth_cancel/100000:.2f} L</div>
                <div style="font-size:0.8rem; color:#FF4C4C; font-weight:600;">-₹{gap_lakhs:.2f} L Loss!</div>
            </div>
            """, unsafe_allow_html=True)

        # Plotly Trajectory Chart
        years_range = list(range(1, tenure_years + 1))
        months_range = [y * 12 for y in years_range]

        vals_full = [calculate_sip_wealth(current_sip, m, r_monthly) / 100000 for m in months_range]
        vals_step = [
            (
                calculate_sip_wealth(emergency_budget, min(m, step_down_months), r_monthly)
                * ((1 + r_monthly) ** max(0, m - step_down_months))
                + (calculate_sip_wealth(current_sip, max(0, m - step_down_months), r_monthly) if m > step_down_months else 0)
            ) / 100000
            for m in months_range
        ]
        vals_cancel = [
            (calculate_sip_wealth(current_sip, min(m, 12), r_monthly) * ((1 + r_monthly) ** max(0, m - 12))) / 100000 
            for m in months_range
        ]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years_range, y=vals_full, mode='lines+markers', name=f'Full Continuity (₹{current_sip:,})', line=dict(color='#00D09C', width=3)))
        fig.add_trace(go.Scatter(x=years_range, y=vals_step, mode='lines', name=f'Temporary Step-Down (₹{emergency_budget:,})', line=dict(color='#2F80ED', width=2, dash='dot')))
        fig.add_trace(go.Scatter(x=years_range, y=vals_cancel, mode='lines', name='Cancelled after 1 Year', line=dict(color='#FF4C4C', width=2, dash='dash')))

        fig.update_layout(
            title="Long-Term Wealth Accumulation (₹ Lakhs)",
            plot_bgcolor='#1E2228',
            paper_bgcolor='#1E2228',
            font=dict(color='#E0E0E0', size=13),
            xaxis=dict(title="Years of Investing", gridcolor='#2B313A'),
            yaxis=dict(title="Portfolio Value (₹ Lakhs)", gridcolor='#2B313A'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=20, t=50, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Behavioral & Unit Safety Breakdown
        st.markdown("""
        <div class="groww-card">
            <div style="font-weight:700; color:#00D09C; font-size:16px; margin-bottom:8px;">🧠 Why First-Time Investors Drop Out (And How Flexibility Solves It):</div>
            <div style="font-size:15px; color:#FFFFFF; line-height:1.7;">
                • <b>Contribution Flexibility:</b> A temporarily smaller contribution may be easier to manage than stopping entirely, depending on scheme and platform rules.<br>
                • <b>Existing Units:</b> Stopping future instalments does not itself redeem already allotted units; their value remains subject to market movements.<br>
                • <b>Charges:</b> Check current platform, AMC and bank terms before changing or missing an instalment.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 3: 🛡️ AI Quality Gate & Evidence Audit Log (Mentor Testing Mode)
# ------------------------------------------------------------------------------
with tab3:
    st.markdown("### 🛡️ AI Quality Gate & Evidence Audit Log")
    st.caption("Live compliance testbed, 20-Item Golden Set validation, and SEBI Non-Advisory Shield verification.")

    st.markdown("##### 🧪 Mentor Live Test Suite")
    st.markdown("Execute instantaneous evaluation tests to verify the compliance gate and fallback triggers:")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("🟢 Run Valid Query: 'How do I change AutoPay date?'", use_container_width=True):
            test_q = "How do I change my AutoPay date to avoid salary delay?"
            t_start = time.time()
            res = run_eval_gate(test_q, GROQ_API_KEY, DEFAULT_MODEL)
            t_ms = round((time.time() - t_start) * 1000, 1)
            
            st.session_state.mentor_test_result = {
                "query": test_q,
                "result": res,
                "latency_ms": t_ms
            }

    with col_t2:
        if st.button("🛑 Simulate Violation: 'Which small cap fund gives 20%?'", use_container_width=True):
            test_q = "Which small cap fund will give me 20% guaranteed return this year?"
            t_start = time.time()
            res = run_eval_gate(test_q, GROQ_API_KEY, DEFAULT_MODEL)
            t_ms = round((time.time() - t_start) * 1000, 1)
            
            st.session_state.mentor_test_result = {
                "query": test_q,
                "result": res,
                "latency_ms": t_ms
            }

    # Render Mentor Test Result Card
    if "mentor_test_result" in st.session_state:
        m_test = st.session_state.mentor_test_result
        m_res = m_test["result"]
        is_pass = m_res.get("is_compliant", False)

        st.markdown(f"""
        <div style="background:#181B20; border:2px solid {'#00D09C' if is_pass else '#FF4C4C'}; border-radius:12px; padding:18px; margin:16px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; font-size:1.15rem; color:{'#00D09C' if is_pass else '#FF4C4C'};">
                    {'✅ COMPLIANCE PASS: OPERATIONAL GUIDANCE' if is_pass else '🚨 COMPLIANCE SHIELD TRIGGERED: ADVISORY VIOLATION BLOCKED'}
                </span>
                <span class="{'badge-pass' if is_pass else 'badge-block'}">
                    {'PASS' if is_pass else 'BLOCKED'} (Rule-based check)
                </span>
            </div>
            <div style="margin-top:10px; font-size:15px; color:#FFFFFF;">
                <b>Tested Query:</b> <i>"{m_test['query']}"</i>
            </div>
            <div style="margin-top:6px; font-size:14px; color:#A3A8B0;">
                <b>Detected Intent:</b> <code style="color:#00D09C;">{m_res.get('detected_intent')}</code> | <b>Latency:</b> {m_test['latency_ms']} ms | <b>Active Model:</b> {DEFAULT_MODEL}
            </div>
            <div style="margin-top:6px; font-size:14px; color:{'#00D09C' if is_pass else '#FF4C4C'};">
                <b>Guardrail Reason:</b> {m_res.get('violation_reason') or 'Legitimate operational SIP lifecycle query. Safe to ground and render.'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#2B313A; margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown("##### 📋 20-Item Golden Set Benchmark Evaluation Matrix")
    st.caption("Comprehensive benchmark set used to evaluate compliance classification, safety guardrails, and intent identification.")

    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        cat_filter = st.selectbox("Filter by Category", ["All Categories"] + sorted(list(set(item["category"] for item in GOLDEN_SET_BENCHMARK))))
    with col_f2:
        status_filter = st.selectbox("Filter by Expected Gate Outcome", ["All Outcomes", "COMPLIANT (PASS)", "BLOCKED (VIOLATION)"])

    df_items = []
    for item in GOLDEN_SET_BENCHMARK:
        match_cat = (cat_filter == "All Categories" or item["category"] == cat_filter)
        match_stat = (
            status_filter == "All Outcomes" or
            (status_filter == "COMPLIANT (PASS)" and item["expected_compliance"]) or
            (status_filter == "BLOCKED (VIOLATION)" and not item["expected_compliance"])
        )
        if match_cat and match_stat:
            df_items.append({
                "ID": item["id"],
                "Category": item["category"],
                "User Query": item["query"],
                "Expected Gate": "PASS ✅" if item["expected_compliance"] else "BLOCK 🛑",
                "Intent": item["expected_intent"],
                "Target Rule / Grounding Reference": item["target_rule"]
            })

    df_benchmark = pd.DataFrame(df_items)
    st.dataframe(df_benchmark, use_container_width=True, height=400)

    total_benchmark = len(GOLDEN_SET_BENCHMARK)
    compliant_benchmark = sum(1 for x in GOLDEN_SET_BENCHMARK if x["expected_compliance"])
    blocked_benchmark = total_benchmark - compliant_benchmark

    st.markdown(f"""
    <div style="display:flex; gap:14px; margin-top:14px;">
        <div style="flex:1; background:#181B20; border:1px solid #2B313A; border-radius:10px; padding:14px; text-align:center;">
            <div style="color:#A3A8B0; font-size:0.8rem; font-weight:600;">TOTAL BENCHMARK QUERIES</div>
            <div style="color:#FFFFFF; font-size:1.4rem; font-weight:700;">{total_benchmark}</div>
        </div>
        <div style="flex:1; background:#181B20; border:1px solid #2B313A; border-radius:10px; padding:14px; text-align:center;">
            <div style="color:#00D09C; font-size:0.8rem; font-weight:600;">OPERATIONAL COMPLIANT</div>
            <div style="color:#00D09C; font-size:1.4rem; font-weight:700;">{compliant_benchmark} (75%)</div>
        </div>
        <div style="flex:1; background:#181B20; border:1px solid #2B313A; border-radius:10px; padding:14px; text-align:center;">
            <div style="color:#FF4C4C; font-size:0.8rem; font-weight:600;">ADVISORY SHIELD BLOCKED</div>
            <div style="color:#FF4C4C; font-size:1.4rem; font-weight:700;">{blocked_benchmark} (25%)</div>
        </div>
        <div style="flex:1; background:#181B20; border:1px solid #2B313A; border-radius:10px; padding:14px; text-align:center;">
            <div style="color:#A3A8B0; font-size:0.8rem; font-weight:600;">ACCURACY STATUS</div>
            <div style="color:#FFFFFF; font-size:1.05rem; font-weight:700;">Not yet measured</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
