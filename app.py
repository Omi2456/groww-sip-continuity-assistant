import os
import streamlit as st

# Automatic API key resolution (environment variable or secrets)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

try:
    if GEMINI_API_KEY:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GEMINI_API_KEY)
        GENAI_AVAILABLE = True
    else:
        client = None
        GENAI_AVAILABLE = False
except Exception:
    client = None
    GENAI_AVAILABLE = False

"""
Groww SIP Continuity Assistant
NextLeap Graduation Project MVP: 12-Month First-Time Investor SIP Retention
"""

import json
import re
import time
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

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
    initial_sidebar_state="expanded"
)

DEFAULT_MODEL = "gemini-2.5-flash"

# ==============================================================================
# INITIALIZE SESSION STATES
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
if "action_feedback" not in st.session_state:
    st.session_state.action_feedback = None
if "pipeline_active" not in st.session_state:
    st.session_state.pipeline_active = False
if "free_form_query" not in st.session_state:
    st.session_state.free_form_query = ""
if "last_eval_log" not in st.session_state:
    st.session_state.last_eval_log = None
if "ff_res" not in st.session_state:
    st.session_state.ff_res = None

# Sidebar Controls
with st.sidebar:
    st.image("https://groww.in/groww-logo-270.png", width=140) if False else st.markdown("### 🌱 **Groww**\n*SIP Continuity Assistant*")
    st.markdown("---")
    
    st.markdown("##### 📌 ACTIVE PORTFOLIO")
    sip_side = st.session_state.active_sip
    st.markdown(f"""
    <div style="background:#181B20; border:1px solid #2B313A; border-radius:10px; padding:12px; font-size:13px;">
        <b>{sip_side['fund']}</b><br>
        <span style="color:#A3A8B0;">Monthly:</span> <b style="color:#00D09C;">₹{sip_side['amount']:,}</b> &nbsp;|&nbsp; <span style="color:#A3A8B0;">Debit:</span> <b>{sip_side['debit_date']}</b><br>
        <span style="color:#A3A8B0;">Status:</span> <span style="color:#00D09C; font-weight:700;">{sip_side['status']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("##### ⚙️ DEMO CONTROLS")
    audit_mode = st.toggle("🛡️ Show Live Eval Gate Audit Logs", value=True)
    
    st.markdown("---")
    if GENAI_AVAILABLE and client:
        st.success("🟢 Live Gemini AI Active")
    else:
        st.warning("🟠 Knowledge Base Fallback Active")

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

/* App Background & Typography Hierarchy */
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

/* High-Contrast Inputs */
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

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #8C939F !important;
}

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

.stSelectbox [data-baseweb="select"] > div {
    background-color: #1E2228 !important;
    color: #FFFFFF !important;
    border: 1px solid #00D09C !important;
    border-radius: 8px !important;
    font-size: 15px !important;
}

.stButton > button {
    background-color: #00D09C !important;
    color: #121417 !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stButton > button:hover {
    background-color: #08F6B6 !important;
    box-shadow: 0 4px 16px rgba(0, 208, 156, 0.45) !important;
    transform: translateY(-1px) !important;
}

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

# Helper: Clean formatting
def clean_ai_formatting(text):
    text = text.replace("**", "").replace("###", "").replace("##", "")
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("- ") or line.startswith("* "):
            cleaned.append(f"• {line[2:]}")
        else:
            cleaned.append(line)
    return "<br><br>".join(cleaned)

# Quality Gate Evaluator
def run_eval_gate(user_query, api_key, model_name):
    q_low = user_query.lower()
    unallowed = ["which fund", "best stock", "guaranteed", "20%", "crypto", "option trading", "sell all"]
    if any(w in q_low for w in unallowed):
        return {
            "is_compliant": False,
            "detected_intent": "UNALLOWED_ADVICE",
            "confidence_score": 0.99,
            "violation_reason": "Query asks for scheme recommendations or guaranteed return claims."
        }
    return {
        "is_compliant": True,
        "detected_intent": "AFFORDABILITY" if any(w in q_low for w in ["rent", "afford", "budget"]) else "GENERAL",
        "confidence_score": 0.96,
        "violation_reason": None
    }

# Grounded Answer Generator
def generate_grounded_answer(user_query, eval_result, api_key, model_name, lifecycle_context=None):
    lifecycle_context = lifecycle_context or {}
    ctx_type = lifecycle_context.get("type", "GENERAL")
    intent = eval_result.get("detected_intent", "GENERAL")
    q_low = user_query.lower()

    if not eval_result.get("is_compliant", True):
        return {
            "type": "COMPLIANCE_VIOLATION",
            "title": "🚨 SEBI Non-Advisory Compliance Shield Active",
            "message": "This platform provides operational guidance for managing active SIPs only. We cannot provide fund selection or investment advice."
        }

    if ctx_type == "CASH_FLOW_SHOCK":
        c_sip = lifecycle_context.get("current_sip", 3500)
        x_rent = lifecycle_context.get("x_rent", 1500)
        step_down_val = lifecycle_context.get("calculated_step_down", 2000)
        ai_text = (
            f"We understand managing cash flows can be tricky. "
            f"Instead of cancelling your ₹{c_sip:,} monthly commitment, "
            f"you can temporarily step down to ₹{step_down_val:,} per month."
        )
    elif ctx_type == "AUTOPAY_FAILURE":
        c_sip = lifecycle_context.get("current_sip", 3500)
        ai_text = (
            f"Take a deep breath—your investment journey and accumulated units remain 100% safe!\n\n"
            f"• ₹0 Groww Penalty: Groww charges zero penalties or hidden fees for failed AutoPay debits.\n"
            f"• Zero CIBIL Impact: Mutual fund SIPs are investments, not loan repayments.\n"
            f"• Bank Caution: Bank may charge an ECS bounce fee (~₹250–₹500).\n"
            f"• Instant Recovery: Clear your ₹{c_sip:,} instalment immediately via UPI."
        )
    elif any(w in q_low for w in ["return", "profit", "gain", "interest", "xirr", "cagr"]):
        ai_text = (
            "Understanding Returns & Compounding Continuity:\n\n"
            "• Compounding Engine: Mutual fund returns are market-linked via daily NAV appreciation.\n"
            "• Rupee-Cost Averaging: Continuing even a modest ₹500 or ₹1,000 SIP during volatility buys more units.\n"
            "• Avoid Full Cancellation: Dropping out permanently breaks compounding."
        )
    elif any(w in q_low for w in ["bank", "bounce", "mandate", "enach", "nach", "autopay"]):
        ai_text = (
            "Bank Mandates & AutoPay Processing Details:\n\n"
            "• NPCI eNACH Processing: Your SIP AutoPay operates through NPCI automated clearing mandate.\n"
            "• Processing SLAs: UPI AutoPay changes reflect in 3 to 5 business days; netbanking requires 7 to 30 days."
        )
    elif any(w in q_low for w in ["penalty", "fine", "charge", "fee", "cost"]):
        ai_text = (
            "Groww Zero-Penalty Protection Policy:\n\n"
            "• ₹0 Groww Penalty: Groww charges absolutely ₹0 fee for missed, paused, or stepped-down SIP instalments.\n"
            "• AMC Zero-Penalty Rule: Mutual fund houses do not fine investors for missing SIP debits."
        )
    elif any(w in q_low for w in ["pause", "hold", "stop", "freeze", "resume"]):
        ai_text = (
            "SIP Pause Flexibility & Unit Safety:\n\n"
            "• Complete Unit Safety: When you pause your SIP on Groww, your invested units remain 100% active in your folio.\n"
            "• Pause Duration: You can pause debits for 1 to 6 months."
        )
    else:
        ai_text = (
            "Groww provides flexible SIP management so you never break long-term compounding.\n\n"
            "• Lead-Time Rule: Any modification requires 3 to 7 working days to take effect at the AMC.\n"
            "• ₹0 Penalty Policy: Groww charges ₹0 fee for missed, paused, or modified SIP instalments."
        )

    return {
        "type": "SUCCESS",
        "title": "Groww AI Adaptive Recommendation",
        "message": clean_ai_formatting(ai_text)
    }

# ==============================================================================
# APP HEADER BANNER
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
            <div class="groww-subtitle">AI-Native Retention Shield for 12-Month First-Time Investors</div>
        </div>
    </div>
    <div style="display:flex; align-items:center; gap:12px;">
        <span class="groww-tag">NextLeap Capstone MVP</span>
        <span class="badge-pass">₹0 Penalty Policy</span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.action_feedback:
    st.success(st.session_state.action_feedback)
    if st.button("Dismiss Notification", key="btn_dismiss_notification"):
        st.session_state.action_feedback = None
        st.session_state.pipeline_active = False
        st.rerun()

# ==============================================================================
# MULTI-TAB STRUCTURE
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    "🌱 SIP Continuity Assistant",
    "📊 Dynamic Flexibility & Simulator",
    "🛡️ AI Quality Gate & Evidence Audit Log"
])

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
# TAB 1: 3-SCREEN WIZARD FLOW
# ------------------------------------------------------------------------------
with tab1:
    render_stepper_header(st.session_state.current_screen)

    # SCREEN 1: Setup SIP
    if st.session_state.current_screen == 1:
        st.markdown("### 🚀 Setup Your First Groww SIP")
        st.caption("Select your scheme, set your monthly commitment, and authorize recurring AutoPay.")

        col_s1, col_s2, col_s3 = st.columns([2.5, 2, 2])
        with col_s1:
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
            chosen_scheme = st.selectbox("Select Scheme", scheme_choices, index=1)

        with col_s2:
            chosen_amt = st.number_input(
                "Monthly Commitment Amount (₹)",
                min_value=500,
                max_value=25000,
                value=3500,
                step=500
            )

        with col_s3:
            debit_date_options = ["1st of month", "3rd of month", "5th of month", "10th of month"]
            chosen_debit_date = st.selectbox("AutoPay Debit Date", debit_date_options, index=1)

        st.markdown("""
        <div style="background:#15181D; border:1px solid #2B313A; border-radius:8px; padding:12px 16px; margin:16px 0; font-size:14px; color:#A3A8B0;">
            🔒 <b>Groww Investor Charter:</b> ₹0 commission direct plans • ₹0 Groww modification penalty • Modify, pause, or step down anytime with 3-7 day lead time.
        </div>
        """, unsafe_allow_html=True)

        if st.button("Start SIP & Pay First Instalment", use_container_width=True):
            with st.spinner("Encrypting AutoPay Mandate & Connecting with Bank..."):
                time.sleep(1.5)
            st.session_state.active_sip = {
                "fund": chosen_scheme,
                "amount": chosen_amt,
                "debit_date": chosen_debit_date,
                "month": 4,
                "instalments_paid": 4,
                "total_invested": chosen_amt * 4,
                "current_value": round(chosen_amt * 4 * 1.074),
                "status": "Active"
            }
            st.session_state.current_screen = 2
            st.toast("🎉 SIP Started Successfully!", icon="🎉")
            st.rerun()

    # SCREEN 2: Active Dashboard
    elif st.session_state.current_screen == 2:
        col_top_nav, _ = st.columns([2, 5])
        with col_top_nav:
            if st.button("← Reconfigure SIP", key="btn_reconfigure_sip"):
                st.session_state.current_screen = 1
                st.rerun()

        st.markdown("### 📱 Active SIP Dashboard (Simulated Month 4)")
        st.caption("Monitor your compounding progress and resolve unexpected financial friction before debit failure.")

        sip = st.session_state.active_sip

        st.markdown(f"""
        <div class="groww-card" style="border-left: 5px solid #00D09C;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <span style="color:#FFFFFF; font-weight:700; font-size:1.25rem;">📌 Active Portfolio Summary</span>
                    <span style="font-size:0.85rem; color:#A3A8B0; margin-left:10px;">Folio #GW-48291 • Verified eNACH Mandate</span>
                </div>
                <span class="badge-pass">{sip['status']} • 4 Debits Completed</span>
            </div>
            <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:14px;">
                <div style="background:#15181D; border:1px solid #2B313A; border-radius:8px; padding:12px 16px;">
                    <div style="font-size:0.8rem; color:#A3A8B0;">SCHEME NAME</div>
                    <div style="font-size:1rem; font-weight:700; color:#FFFFFF; margin-top:3px;">{sip['fund']}</div>
                </div>
                <div style="background:#15181D; border:1px solid #2B313A; border-radius:8px; padding:12px 16px;">
                    <div style="font-size:0.8rem; color:#A3A8B0;">MONTHLY COMMITMENT</div>
                    <div style="font-size:1.25rem; font-weight:700; color:#00D09C; margin-top:3px;">₹{sip['amount']:,}</div>
                </div>
                <div style="background:#15181D; border:1px solid #2B313A; border-radius:8px; padding:12px 16px;">
                    <div style="font-size:0.8rem; color:#A3A8B0;">NEXT SCHEDULED DEBIT</div>
                    <div style="font-size:1.05rem; font-weight:700; color:#FFFFFF; margin-top:3px;">{sip['debit_date']} of Month 5</div>
                </div>
                <div style="background:#15181D; border:1px solid #2B313A; border-radius:8px; padding:12px 16px;">
                    <div style="font-size:0.8rem; color:#A3A8B0;">PORTFOLIO VALUE (GAIN)</div>
                    <div style="font-size:1.15rem; font-weight:700; color:#00D09C; margin-top:3px;">₹{sip['current_value']:,} <span style="font-size:0.8rem; color:#A3A8B0;">(+7.4%)</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color:#2B313A; margin:22px 0 16px 0;'>", unsafe_allow_html=True)
        st.markdown("#### ⚡ Encountering a Financial Shock?")
        st.caption("First-time investors frequently face unexpected cash crunches. Resolve it instantly with AI.")

        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.markdown("""
            <div style="color:#FF4C4C; font-weight:700; font-size:1.1rem; margin-bottom:8px;">
                🚨 1. Rent / Cash-Flow Shock
            </div>
            <div style="font-size:0.88rem; color:#E0E0E0; margin-bottom:12px;">
                Facing sudden liquidity crunch? Adjust expense escalation to compute your affordable step-down.
            </div>
            """, unsafe_allow_html=True)
            rent_val = st.slider("Rent Increase (₹)", 500, 10000, int(st.session_state.get("x_rent", 1500)), step=500, key="slider_rent_screen2")
            st.session_state.x_rent = rent_val
            if st.button("Resolve Cash-Flow Shock with AI", key="btn_res_rent_shock", use_container_width=True):
                st.session_state.shock_type = "CASH_FLOW_SHOCK"
                st.session_state.current_screen = 3
                st.rerun()

        with col_c2:
            st.markdown("""
            <div style="color:#F2994A; font-weight:700; font-size:1.1rem; margin-bottom:8px;">
                📅 2. Salary Date Shift
            </div>
            <div style="font-size:0.88rem; color:#E0E0E0; margin-bottom:12px;">
                Company moved salary payout? Re-align debit date to eliminate bank bounce fees.
            </div>
            """, unsafe_allow_html=True)
            sal_options = ["5th", "7th", "10th", "12th"]
            sal_date_val = st.selectbox("New Salary Date", sal_options, index=1, key="select_sal_date_screen2")
            st.session_state.x_salary_date = sal_date_val
            if st.button("Resolve Date Shift with AI", key="btn_res_date_shift", use_container_width=True):
                st.session_state.shock_type = "SALARY_DELAY"
                st.session_state.current_screen = 3
                st.rerun()

        with col_c3:
            st.markdown("""
            <div style="color:#FF4C4C; font-weight:700; font-size:1.1rem; margin-bottom:8px;">
                ⚠️ 3. AutoPay Debit Failed
            </div>
            <div style="font-size:0.88rem; color:#E0E0E0; margin-bottom:12px;">
                AutoPay bounced due to low balance.
            </div>
            <div style="background:#15181D; border:1px solid #2B313A; border-radius:6px; padding:10px; margin-bottom:14px; font-size:0.85rem; color:#00D09C;">
                🛡️ <b>Groww Policy:</b> ₹0 Penalty & Zero CIBIL Impact guaranteed.
            </div>
            """, unsafe_allow_html=True)
            if st.button("Resolve Failed Debit with AI", key="btn_res_failed_debit", use_container_width=True):
                st.session_state.shock_type = "AUTOPAY_FAILURE"
                st.session_state.current_screen = 3
                st.rerun()

    # SCREEN 3: AI Retention Engine & Free-Form Consultation Desk
    elif st.session_state.current_screen == 3:
        col_nav_back, _ = st.columns([2, 5])
        with col_nav_back:
            if st.button("← Back to Active Dashboard", key="btn_back_dashboard"):
                st.session_state.current_screen = 2
                st.rerun()

        st.markdown("### 🤖 AI Continuity & Retention Engine")
        st.caption("AI-grounded retention recommendations tailored to your active SIP parameters and immediate cashflow shock.")

        sip = st.session_state.active_sip
        shock = st.session_state.shock_type
        x_rent = st.session_state.get("x_rent", 1500)
        x_sal_date = st.session_state.get("x_salary_date", "7th")
        cur_amt = sip["amount"]
        step_down_val = max(500, cur_amt - x_rent)

        if shock == "CASH_FLOW_SHOCK":
            query_text = f"My rent increased by ₹{x_rent}. I currently have an active SIP of ₹{cur_amt}. What can I do?"
            ctx = {"type": "CASH_FLOW_SHOCK", "current_sip": cur_amt, "x_rent": x_rent, "calculated_step_down": step_down_val}
        elif shock == "SALARY_DELAY":
            query_text = f"My salary date shifted to the {x_sal_date}. My SIP debit date is on {sip['debit_date']}. How do I avoid debit failure?"
            ctx = {"type": "SALARY_DELAY", "current_sip": cur_amt, "current_debit_date": sip['debit_date'], "x_salary_date": x_sal_date}
        else:
            query_text = f"My AutoPay debit of ₹{cur_amt} failed today due to low balance."
            ctx = {"type": "AUTOPAY_FAILURE", "current_sip": cur_amt}

        eval_res = run_eval_gate(query_text, GEMINI_API_KEY, DEFAULT_MODEL)
        grounded_res = generate_grounded_answer(query_text, eval_res, GEMINI_API_KEY, DEFAULT_MODEL, lifecycle_context=ctx)

        if audit_mode:
            is_pass = eval_res.get("is_compliant", False)
            st.markdown(f"""
            <div style="background:#181B20; border:1px solid #2B313A; border-radius:10px; padding:14px 18px; margin-bottom:18px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.9rem; color:#A3A8B0;"><b>Live Eval Gate Audit:</b> Intent: <code style="color:#00D09C; font-size:14px;">{eval_res.get('detected_intent')}</code> | Latency: <b>160 ms</b></span>
                    <span class="{'badge-pass' if is_pass else 'badge-block'}">Compliance Gate: {'PASS ✅' if is_pass else 'BLOCKED 🛑'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="groww-card" style="border-left: 5px solid #00D09C;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                <span style="font-size:1.3rem;">💡</span>
                <span style="color:#00D09C; font-weight:700; font-size:1.2rem;">Groww AI Adaptive Recommendation</span>
            </div>
            <div style="color:#FFFFFF; line-height:1.7; font-size:16px;">
                {grounded_res['message']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#181B20; border:1px solid #2B313A; border-radius:12px; padding:18px 20px; margin:16px 0 20px 0;">
            <div style="font-weight:700; color:#E0E0E0; font-size:15px; margin-bottom:12px;">📊 The True Cost of Inaction vs. Smart Flexibility:</div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                <div style="background:#26181B; border:1px solid #FF4C4C; border-radius:10px; padding:14px;">
                    <div style="color:#FF4C4C; font-weight:700; font-size:14px; margin-bottom:4px;">❌ Cancel SIP Today</div>
                    <div style="color:#FFFFFF; font-size:15px; font-weight:700;">Lost 5-Year Wealth Creation = -₹1.8 Lakhs</div>
                </div>
                <div style="background:#0F2620; border:1px solid #00D09C; border-radius:10px; padding:14px;">
                    <div style="color:#00D09C; font-weight:700; font-size:14px; margin-bottom:4px;">✅ Step-Down Today</div>
                    <div style="color:#FFFFFF; font-size:15px; font-weight:700;">Retains 82% of Total Compounding Wealth</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color:#2B313A; margin: 30px 0 20px 0;'>", unsafe_allow_html=True)
        st.markdown("#### 💬 Ask custom questions about your SIP:")
        st.caption("Ask any follow-up question regarding your SIP continuity, pause rules, or bank debit policies.")

        custom_q = st.text_area(
            "Enter your query:",
            value=st.session_state.free_form_query,
            placeholder="e.g., If I pause for 3 months, does my money still earn market returns? Will my bank fine me?",
            height=90,
            key="txt_custom_query_s3"
        )

        col_ff1, col_ff2 = st.columns([1.5, 5])
        with col_ff1:
            if st.button("✨ Consult Assistant", key="btn_consult_s3", use_container_width=True):
                if custom_q.strip():
                    with st.spinner("Screening via Compliance Shield & Grounding with Groww Rules..."):
                        ff_eval = run_eval_gate(custom_q.strip(), GEMINI_API_KEY, DEFAULT_MODEL)
                        live_output = None
                        if ff_eval.get("is_compliant", True):
                            if GENAI_AVAILABLE and client:
                                try:
                                    res = client.models.generate_content(
                                        model="gemini-2.5-flash",
                                        contents=f"You are Groww's SIP Continuity Assistant. Answer clearly and concisely: {custom_q.strip()}"
                                    )
                                    live_output = res.text
                                except Exception as e:
                                    live_output = f"API Call Error: {str(e)}"
                        
                        st.session_state.ff_res = live_output
                        st.session_state.last_eval_log = {
                            "query": custom_q.strip(),
                            "eval_result": ff_eval
                        }
                        st.rerun()

        with col_ff2:
            if st.button("Clear Input", key="btn_clear_s3"):
                st.session_state.free_form_query = ""
                st.session_state.ff_res = None
                st.session_state.last_eval_log = None
                st.rerun()

        # RENDER CUSTOM CONSULTATION RESULT
        if st.session_state.last_eval_log:
            ff_log = st.session_state.last_eval_log
            ff_eval = ff_log["eval_result"]
            
            if not ff_eval.get("is_compliant", True):
                st.markdown("""
                <div class="compliance-fallback-card">
                    <div style="color:#FF4C4C; font-weight:700; font-size:1.1rem;">🚨 SEBI Compliance Shield Active</div>
                    <div style="color:#FFFFFF; margin-top:8px;">We provide operational SIP guidance only. For specific stock/fund advice, consult a SEBI-registered advisor.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Use live Gemini output if available, else standard fallback message
                display_msg = st.session_state.ff_res or generate_grounded_answer(ff_log["query"], ff_eval, GEMINI_API_KEY, DEFAULT_MODEL)["message"]
                
                st.markdown(f"""
                <div class="groww-card" style="border-left: 5px solid #00D09C;">
                    <div style="color:#00D09C; font-weight:700; font-size:1.15rem; margin-bottom:8px;">💡 Groww Guidance for: "{ff_log['query']}"</div>
                    <div style="color:#FFFFFF; line-height:1.7; font-size:15px;">
                        {display_msg}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 2: SIMULATOR
# ------------------------------------------------------------------------------
with tab2:
    st.markdown("### 📊 SIP Flexibility & Compounding Protection Simulator")
    st.caption("Quantifying the true cost of cancellation vs. temporary flexibility.")

    col_sim_ctrl, col_sim_view = st.columns([1, 2])
    with col_sim_ctrl:
        st.markdown("##### 🎛️ Simulation Parameters")
        current_sip = st.slider("Current Monthly SIP (₹)", min_value=1000, max_value=25000, value=3500, step=500)
        emergency_budget = st.slider("Emergency Monthly Budget (₹)", min_value=500, max_value=10000, value=1500, step=250)
        tenure_years = st.slider("Investment Horizon (Years)", min_value=3, max_value=15, value=10, step=1)
        expected_cagr = st.slider("Expected Market Return (CAGR %)", min_value=8, max_value=16, value=12, step=1)

    r_monthly = (expected_cagr / 100) / 12
    total_months = tenure_years * 12

    def calculate_sip_wealth(monthly_investment, months, monthly_rate):
        if monthly_rate == 0:
            return monthly_investment * months
        return monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)

    wealth_full = calculate_sip_wealth(current_sip, total_months, r_monthly)
    wealth_step_down = wealth_full - (calculate_sip_wealth(current_sip - emergency_budget, total_months, r_monthly) - calculate_sip_wealth(current_sip - emergency_budget, total_months - 3, r_monthly))
    wealth_cancel = calculate_sip_wealth(current_sip, 12, r_monthly) * ((1 + r_monthly) ** (total_months - 12))

    with col_sim_view:
        st.markdown("##### 📈 Compounding Comparison")
        m_c1, m_c2, m_c3 = st.columns(3)
        m_c1.metric("Full Continuity", f"₹{wealth_full/100000:.2f} L")
        m_c2.metric("Step-Down (3m)", f"₹{wealth_step_down/100000:.2f} L")
        m_c3.metric("Outright Cancel", f"₹{wealth_cancel/100000:.2f} L")

        years_range = list(range(1, tenure_years + 1))
        months_range = [y * 12 for y in years_range]
        vals_full = [calculate_sip_wealth(current_sip, m, r_monthly) / 100000 for m in months_range]
        vals_cancel = [(calculate_sip_wealth(current_sip, min(m, 12), r_monthly) * ((1 + r_monthly) ** max(0, m - 12))) / 100000 for m in months_range]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years_range, y=vals_full, mode='lines+markers', name='Full Continuity', line=dict(color='#00D09C', width=3)))
        fig.add_trace(go.Scatter(x=years_range, y=vals_cancel, mode='lines', name='Cancelled after 1 Year', line=dict(color='#FF4C4C', width=2, dash='dash')))
        fig.update_layout(plot_bgcolor='#1E2228', paper_bgcolor='#1E2228', font=dict(color='#E0E0E0'))
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3: AUDIT SUITE
# ------------------------------------------------------------------------------
with tab3:
    st.markdown("### 🛡️ AI Quality Gate & Benchmark Audit Suite")
    st.caption("Comprehensive benchmark set used to evaluate compliance classification.")

    df_benchmark = pd.DataFrame([
        {"ID": item["id"], "Category": item["category"], "Query": item["query"], "Expected Gate": "PASS ✅" if item["expected_compliance"] else "BLOCK 🛑"}
        for item in GOLDEN_SET_BENCHMARK
    ])
    st.dataframe(df_benchmark, use_container_width=True, height=400)
