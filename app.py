import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from ai_agent import ask_data_analyst, generate_pdf_report # generate_pdf_report ko import kiya

# --- Database Connection ---
MYSQL_URL = "sqlite:///historical_trends.db"
engine = create_engine(MYSQL_URL)

# --- Page Configuration ---
st.set_page_config(page_title="AI Data Analyst & Dashboard", page_icon="📊", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 5px; background-color: #28a745; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 UPSC SuperApp: AI Analyst & Strategic Dashboard")

# --- UI Layout: 2 Columns ---
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("### 🤖 Multi-Agent AI Analyst")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat history display
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("E.g. Compare 2023 vacancies with 2022?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Agents collaborating on your request..."):
            answer = ask_data_analyst(prompt)

        with st.chat_message("assistant"):
            st.markdown(answer)
            
            # --- Executive PDF Feature ---
            # Agar AI ne Executive Brief generate kiya hai, toh download button dikhao
            if "### 📊 Executive Brief" in answer:
                brief_content = answer.split("---")[-1]
                pdf_bytes = generate_pdf_report(brief_content)
                
                st.download_button(
                    label="📥 Download Executive Brief (PDF)",
                    data=pdf_bytes,
                    file_name="UPSC_Strategic_Report.pdf",
                    mime="application/pdf",
                    key=f"dl_{len(st.session_state.messages)}"
                )

        st.session_state.messages.append({"role": "assistant", "content": answer})

with col2:
    st.markdown("### 📈 Strategic Analytics Dashboard")
    try:
        df = pd.read_sql("SELECT * FROM exam_trends", engine)
        
        # --- Proactive Anomaly Detection Alert ---
        # Agar cut-off 100 ke upar hai (Just an example logic), toh alert dikhao
        latest_avg_cutoff = df[df['exam_year'] == df['exam_year'].max()]['cut_off_marks'].mean()
        if latest_avg_cutoff > 95:
            st.warning(f"🚨 **Anomaly Detected:** Current year cut-off trends ({latest_avg_cutoff:.1f}) are significantly higher than historical averages.")

        # 1. Bar Chart: Vacancies
        st.markdown("**Total Vacancies (Year-wise)**")
        fig1 = px.bar(df, x="exam_year", y="total_vacancies", color="difficulty_level", 
                     barmode="group", template="plotly_white", color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig1, use_container_width=True)

        # 2. Line Chart: Cut-off Trends
        st.markdown("**Cut-off Marks Trend by Category**")
        fig2 = px.line(df, x="exam_year", y="cut_off_marks", color="category", markers=True,
                      template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)
        
        # 3. New Insight: Difficulty vs Vacancy (Bubble Chart)
        st.markdown("**Difficulty vs Vacancy Correlation**")
        fig3 = px.scatter(df, x="total_vacancies", y="cut_off_marks", size="total_vacancies", 
                         color="difficulty_level", hover_name="exam_year", log_x=True, size_max=20)
        st.plotly_chart(fig3, use_container_width=True)
            
    except Exception as e:
        st.error(f"⚠️ Could not load dashboard: {e}")
