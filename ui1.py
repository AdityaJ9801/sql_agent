import streamlit as st
import pandas as pd
import os
from agent import app 
from langchain_core.messages import HumanMessage, AIMessage

# --- UI CONFIG ---
st.set_page_config(page_title="SQL Neural Dashboard", layout="wide")

# Futuristic Deep Theme CSS
st.markdown("""
    <style>
    .stApp { background: #0b0d11; color: #e0e0e0; }
    /* Card Styling */
    .dashboard-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .status-text {
        font-family: 'Courier New', monospace;
        color: #00ffcc;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TOP NAVIGATION ---
# Fixed the default value error by matching the string exactly
options = ["1 - SQL", "2 - Insights", "3 - Viz"]
t1, t2, t3 = st.columns([1, 2, 1])
with t2:
    st.markdown("<h2 style='text-align: center; letter-spacing: 5px;'>NEURAL INTERFACE</h2>", unsafe_allow_html=True)
    mode = st.segmented_control(
        "Select Operation Protocol", 
        options, 
        default="3 - Viz"  # FIXED: Matches the list item exactly
    )
    mode_val = mode[0] if mode else "3"

st.divider()

# --- DASHBOARD LAYOUT ---
col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown("#### 📡 Data Stream")
    if os.path.exists("temp_results.csv"):
        df = pd.read_csv("temp_results.csv")
        st.dataframe(df, use_container_width=True, height=400, hide_index=True)
    else:
        st.info("System awaiting command input...")

with col_right:
    st.markdown("#### 📊 Synaptic Projection")
    if os.path.exists("temp_results.csv") and mode_val == "3":
        df = pd.read_csv("temp_results.csv")
        if not df.empty and len(df.columns) >= 2:
            # st.area_chart(df, x=df.columns[0], y=df.columns[1], color="#00ffcc")
            st.area_chart(df, x=df.columns[0], y=df.columns[1], color="#800080")
        else:
            st.warning("Insufficient dimensional data for projection.")
    else:
        st.info("Visual engine in standby mode.")

# --- AGENT INSIGHTS (The "Thinking" area) ---
st.markdown("---")
st.markdown("#### 🧠 Agent Logic & Insights")
insight_box = st.container(border=True)

# Only show the latest AI response to keep it clean
if st.session_state.messages:
    ai_msgs = [m.content for m in st.session_state.messages if isinstance(m, AIMessage)]
    if ai_msgs:
        insight_box.markdown(ai_msgs[-1])

# --- COMMAND INPUT (Fixed at Bottom) ---
if prompt := st.chat_input("Input Command (e.g., 'Show total sales per region')"):
    st.session_state.messages.append(HumanMessage(content=prompt))
    
    with st.spinner("Processing Neural Flow..."):
        # Run the LangGraph agent
        inputs = {"messages": st.session_state.messages, "mode": mode_val}
        final_text = ""
        
        # Values mode ensures we get the state updates correctly
        for event in app.stream(inputs, stream_mode="values"):
            msg = event["messages"][-1]
            if isinstance(msg, AIMessage) and msg.content:
                final_text = msg.content
        
        st.session_state.messages.append(AIMessage(content=final_text))
        st.rerun()