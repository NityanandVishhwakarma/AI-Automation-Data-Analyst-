import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from ai_agent import ask_data_analyst

# --- Database Connection for Graphs ---
# Apna password yahan theek karein agar zaroorat ho
MYSQL_URL = "sqlite:///historical_trends.db"
engine = create_engine(MYSQL_URL)

# --- Page Configuration ---
st.set_page_config(page_title="AI Data Analyst & Dashboard", page_icon="📊", layout="wide")

st.title("📊 UPSC Trends: AI Assistant & Dashboard")

# --- UI Layout: 2 Columns (Chat on left, Dashboard on right) ---
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🤖 Chat with Data")
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("E.g. What was the highest cut-off?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Analyzing data..."):
            answer = ask_data_analyst(prompt)

        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

with col2:
    st.markdown("### 📈 Live Analytics Dashboard")
    try:
        # Database se data load karna Pandas DataFrame mein
        df = pd.read_sql("SELECT * FROM exam_trends", engine)
        
        # 1. Bar Chart: Vacancies over the Years
        st.markdown("**Total Vacancies (Year-wise)**")
        fig1 = px.bar(df, x="exam_year", y="total_vacancies", color="difficulty_level", barmode="group")
        st.plotly_chart(fig1, use_container_width=True)

        # 2. Line Chart: Cut-off Trends
        st.markdown("**Cut-off Marks Trend by Category**")
        fig2 = px.line(df, x="exam_year", y="cut_off_marks", color="category", markers=True)
        st.plotly_chart(fig2, use_container_width=True)
        
    except Exception as e:
        st.error(f"⚠️ Could not load dashboard: {e}")
