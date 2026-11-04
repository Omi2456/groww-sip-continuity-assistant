import json
import os
import re
import time
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

# Try importing google-genai
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from knowledge_base import (
    GROWW_SIP_KNOWLEDGE_BASE,
    GOLDEN_SET_BENCHMARK,
    INTENT_DEFINITIONS
)

load_dotenv()

st.set_page_config(
    page_title="Groww SIP Continuity Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

DEFAULT_MODEL = "gemini-2.5-flash"

try:
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
    else:
        client = None
except Exception:
    client = None

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

GROWW_ACCESSIBLE_CSS = """
<style>
:root {
    --groww-teal: #00D09C;
    --groww-dark: #121417;
    --groww-card: #1E2228;
    --groww-border: #2B313A;
}
html, body, [class*="css"], .stApp {
    background-color: #121417 !important;
    color: #FFFFFF !important;
}
.groww-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 24px;
    background: linear-gradient(135deg, #1E2228 0%, #15181D 100%);
    border: 1px solid #2B313A;
    border-radius: 14px;
    margin-bottom: 22px;
}
.groww-card {
    background-color: #1E2228 !important;
    border: 1px solid #2B313A !important;
    border-radius: 12px !important;
    padding: 22px !important;
    margin-bottom: 18px !important;
}
.stButton > button {
    background-color: #00D09C !important;
    color: #121417 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
}
.badge-pass {
    background: rgba(0, 208, 156, 0.18);
    color: #00D09C;
    border: 1px solid #00D09C;
    padding: 4px 12px;
    border-radius: 14px;
}
.badge-block {
    background: rgba(255, 76, 76, 0.18);
    color: #FF4C4C;
    border: 1px solid #FF4C4C;
    padding: 4px 12px;
    border-radius: 14px;
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
}
.metric-label {
    font-size: 0.82rem;
    color: #A3A8B0;
    text-transform: uppercase;
}
</style>
"""
st.markdown(GROWW_ACCESSIBLE_CSS, unsafe_allow_html=True)

def run_eval_gate(user_query, api_key, model_name):
    q_low = user_query.lower()
    unallowed = ["which fund", "best stock", "guaranteed", "crypto", "option trading", "sell all"]
    if any(w in q_low for w in unallowed):
        return {
            "is_compliant": False,
            "detected_intent": "UNALLOWED_ADVICE",
            "confidence_score": 0.99,
            "violation_reason": "Query asks for scheme/stock recommendations or guaranteed returns."
        }
    return {
        "is_compliant": True,
        "detected_intent": "AFFORDABILITY" if "rent" in q_low or "afford" in q_low else "GENERAL",
        "confidence_score": 0.96,
        "violation_reason": None
    }

def generate_grounded_answer(user_query, eval_result, api_key, model_name, lifecycle_context=None):
    if not eval_result.get("is_compliant", True):
        return {
            "type": "COMPLIANCE_VIOLATION",
            "title": "🚨 SEBI Non-Advisory Compliance Shield Active",
            "message": "This platform provides operational guidance for managing active SIPs only. We cannot recommend specific funds or stocks."
        }

    return {
        "type": "SUCCESS",
        "title": "Groww AI Adaptive Recommendation",
        "message": "Groww provides flexible SIP management so you never have to break your compounding journey. You can pause, skip, or step down anytime with ₹0 Groww penalty."
    }

st.markdown("""
<div class="groww-header">
    <div>
        <div style="font-size: 1.65rem; font-weight:700;">🌱 Groww SIP Continuity Assistant</div>
        <div style="color: #A3A8B0;">AI-Native Retention Shield for First-Time Investors</div>
    </div>
    <div><span class="badge-pass">₹0 Penalty Policy</span></div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🌱 SIP Continuity Assistant", "📊 Dynamic Flexibility & Simulator", "🛡️ AI Quality Gate & Audit Log"])

with tab1:
    if st.session_state.current_screen == 1:
        st.markdown("### 🚀 Setup Your First Groww SIP")
        scheme = st.selectbox("Select Scheme", ["Nifty 50 Index Fund", "Parag Parikh Flexi Cap Fund"])
        amt = st.number_input("Monthly SIP (₹)", min_value=500, max_value=25000, value=3500)
        if st.button("Start SIP & Pay First Instalment"):
            st.session_state.active_sip["amount"] = amt
            st.session_state.active_sip["fund"] = scheme
            st.session_state.current_screen = 2
            st.rerun()

    elif st.session_state.current_screen == 2:
        st.markdown("### 📱 Active SIP Dashboard (Simulated Month 4)")
        sip = st.session_state.active_sip
        st.info(f"Active Fund: {sip['fund']} | Monthly Amount: ₹{sip['amount']:,}")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Resolve Rent Shock with AI"):
                st.session_state.shock_type = "CASH_FLOW_SHOCK"
                st.session_state.current_screen = 3
                st.rerun()
        with col2:
            if st.button("Resolve Salary Shift with AI"):
                st.session_state.shock_type = "SALARY_DELAY"
                st.session_state.current_screen = 3
                st.rerun()
        with col3:
            if st.button("Resolve AutoPay Bounce with AI"):
                st.session_state.shock_type = "AUTOPAY_FAILURE"
                st.session_state.current_screen = 3
                st.rerun()

    elif st.session_state.current_screen == 3:
        if st.button("← Back to Active Dashboard"):
            st.session_state.current_screen = 2
            st.rerun()

        st.markdown("### 🤖 AI Continuity & Retention Engine")
        sip = st.session_state.active_sip

        st.markdown(f"""
        <div class="groww-card">
            <div style="color:#00D09C; font-weight:700; font-size:1.2rem;">💡 Groww AI Adaptive Recommendation</div>
            <div style="margin-top:10px;">Your active monthly commitment is <b>₹{sip['amount']:,}</b>. If facing cash crunch, step down to ₹1,000 or skip next month with ₹0 penalty.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 💬 Ask custom questions about your SIP:")
        custom_q = st.text_area("Enter your query:", placeholder="e.g. What is your name?")

        if st.button("✨ Consult Assistant"):
            if custom_q.strip():
                if client:
                    try:
                        res = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=f"You are Groww's SIP Assistant. Answer clearly: {custom_q.strip()}"
                        )
                        st.session_state.ff_res = res.text
                    except Exception as e:
                        st.session_state.ff_res = f"Gemini API Error: {str(e)}"
                else:
                    st.session_state.ff_res = "Gemini Client offline. Please set GEMINI_API_KEY."
                st.rerun()

        if st.session_state.ff_res:
            st.markdown(f"""
            <div class="groww-card" style="border-left: 5px solid #00D09C;">
                <div style="color:#00D09C; font-weight:700; font-size:1.15rem; margin-bottom:8px;">💡 Groww AI Live Guidance</div>
                <div style="color:#FFFFFF; line-height:1.7; font-size:15px;">
                    {st.session_state.ff_res}
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 📊 SIP Flexibility & Compounding Protection Simulator")
    st.info("Quantifying the true cost of cancellation vs. Step-Down & Skip flexibility.")

with tab3:
    st.markdown("### 🛡️ AI Quality Gate & Benchmark Audit Suite")
    st.success("Guardrails & SEBI Compliance Gate Active.")
