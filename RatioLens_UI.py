import streamlit as st
import os
import pandas as pd
from agentic_functions import *
import matplotlib.image as mpimg
import atexit

# cleanup on shutdown
def cleanup():
    if os.path.exists("plot.png"):
        os.remove("plot.png")

atexit.register(cleanup)

# ── Page config ─────────────────────────────────────
st.set_page_config(page_title="RatioLens", page_icon="📊", layout="wide")

# ── Session state ───────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "session-1"

# ── Agent call (file-based plotting kept) ───────────
def run_agent(user_input: str, thread_id: str):
    try:
        config = {"configurable": {"thread_id": "1"}}#, "user_id": "1"}}
        result = supervisor.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,)
        text = result["messages"][-1].content
        output = {"text": text}
        # File-based plotting (kept but safer)
        plot_path = "plot.png"
        if os.path.exists(plot_path):
            with open(plot_path, "rb") as f:
                img_bytes = f.read()
            os.remove(plot_path)
            output["chart"] = img_bytes
            output["chart_type"] = "image"
        return output
    except Exception as e:
        return {"text": f"Error: {str(e)}"}

# ── Header ──────────────────────────────────────────
st.title("📊 RatioLens")
st.caption("SEC EDGAR · Financial Analysis")

# ── Chat display ─────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "df" in msg:
            st.dataframe(msg["df"], width='stretch')
        if "chart" in msg:
            st.image(msg["chart"], width=300)

# ── Input ───────────────────────────────────────────
user_input = st.chat_input("Ask about a company...")
if user_input:
    # 1. Add user message immediately
    st.session_state.messages.append({
        "role": "user",
        "content": user_input})
    # 2. Rerender chat so it appears instantly
    with st.chat_message("user"):
        st.write(user_input)
    # 3. Show assistant placeholder
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write("Thinking...")
        result = run_agent(user_input, st.session_state.thread_id)
        # Replace placeholder with real response
        placeholder.write(result.get("text", ""))

        agent_msg = {   "role": "assistant",
            "content": result.get("text", "") }
        if result.get("df") is not None:
            agent_msg["df"] = result["df"]
            st.dataframe(result["df"], width="stretch")
        if result.get("chart") is not None:
            agent_msg["chart"] = result["chart"]
            st.image(result["chart"], width=300)

    st.session_state.messages.append(agent_msg)

    # Trim history
    MAX_MSG = 20
    st.session_state.messages = st.session_state.messages[-MAX_MSG:]

    st.rerun()

# ── Sidebar (minimal) ───────────────────────────────
with st.sidebar:
    st.markdown("# 📊 RatioLens")
    st.markdown("## Controls")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown("**Example prompts**")
    st.markdown("- Net income of AAPL")
    st.markdown("- Compare MSFT vs GOOGL margins")
    st.markdown("### Tickers")
    tickers = {
        "AAPL": "Apple",
        "MSFT": "Microsoft",
        "GOOGL": "Google",
        "META": "Meta",
        "AMZN": "Amazon",
        "NFLX": "Netflix",
        "CRM": "Salesforce",
        "ORCL": "Oracle",
        "INTC": "Intel",
        "IBM": "IBM",
        # Semiconductors / hardware
        "NVDA": "NVIDIA",
        "AMD": "AMD",
        "TSM": "TSMC",
        "AVGO": "Broadcom",
        "QCOM": "Qualcomm",
        "TXN": "Texas Instruments",
        # Big tech / platforms
        "ADBE": "Adobe",
        "CSCO": "Cisco",
        "SAP": "SAP",
        "UBER": "Uber",
        "SHOP": "Shopify",
        # Fintech / payments
        "PYPL": "PayPal",
        "SQ": "Block",
        "V": "Visa",
        "MA": "Mastercard",
        # Cloud / data / enterprise
        "SNOW": "Snowflake",
        "PLTR": "Palantir",
        "NOW": "ServiceNow",
        "WDAY": "Workday",
        # Consumer tech / growth
        "TSLA": "Tesla",
        "DIS": "Disney",
        "SPOT": "Spotify",
        # China tech (optional but useful)
        "BABA": "Alibaba",
        "JD": "JD.com",
        "PDD": "PDD Hold"}
    #for ticker, name in tickers.items():
    #    st.markdown(f"`{ticker}` {name}")
    ticker_items = list(tickers.items())
    col1, col2 = st.columns(2)
    for i, (ticker, name) in enumerate(ticker_items):
        col = col1 if i % 2 == 0 else col2
        col.markdown(f"`{ticker}` {name}")
