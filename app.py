import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from ai_agent import ask_data_analyst, generate_pdf_report

# --- Database Connection ---
MYSQL_URL = "sqlite:///historical_trends.db"
engine = create_engine(MYSQL_URL)

# --- Page Configuration ---
st.set_page_config(page_title="UPSC AI SuperApp", page_icon="🚀", layout="wide")

# Custom CSS for Professional UI
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stAlert { border-radius: 10px; border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .chat-container { border-radius: 15px; padding: 20px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 UPSC Strategic AI Command Center")

# --- UI Layout: 2 Columns ---
col1, col2 = st.columns([1.3, 1])

with col1:
    st.markdown("### 🤖 Hybrid AI Intelligence (SQL + Research)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat history display
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("E.g. Analyze the trend of vacancies and suggest a strategy?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Multi-Agent team is analyzing SQL trends and PDF reports..."):
            answer = ask_data_analyst(prompt)

        with st.chat_message("assistant"):
            st.markdown(answer)
            
            # --- Automated Executive PDF Generator ---
            if "### 📊 Executive Brief" in answer:
                # PDF ke liye sirf analysis wala part extract karna
                brief_content = answer.split("### 📊 Executive Brief")[-1]
                pdf_bytes = generate_pdf_report(brief_content)
                
                st.download_button(
                    label="📥 Download Strategic Briefing (PDF)",
                    data=pdf_bytes,
                    file_name="UPSC_Strategic_Analysis.pdf",
                    mime="application/pdf",
                    key=f"dl_{len(st.session_state.messages)}"
                )

        st.session_state.messages.append({"role": "assistant", "content": answer})

with col2:
    st.markdown("### 📈 Proactive Analytics Dashboard")
    try:
        df = pd.read_sql("SELECT * FROM exam_trends", engine)
        
        # --- SMART ANOMALY DETECTION ENGINE ---
        latest_year = df['exam_year'].max()
        current_data = df[df['exam_year'] == latest_year]
        avg_vacancies = df['total_vacancies'].mean()
        latest_vacancies = current_data['total_vacancies'].iloc[0]

        # Alert 1: Vacancy Drop Anomaly
        if latest_vacancies < (avg_vacancies * 0.8):
            st.error(f"🚨 **Vacancy Alert:** {latest_year} vacancies are {((avg_vacancies-latest_vacancies)/avg_vacancies)*100:.1f}% below the historical average!")
        
        # Alert 2: High Cut-off Trend
        latest_avg_cutoff = current_data['cut_off_marks'].mean()
        if latest_avg_cutoff > 98:
            st.warning(f"⚡ **Cut-off Spike:** Unusual upward trend detected in {latest_year}. Competition index is at an all-time high.")

        # --- VISUALIZATIONS ---
        
        # 1. Bar Chart: Vacancies
        st.markdown("**Recruitment Trends (Year-wise)**")
        fig1 = px.bar(df, x="exam_year", y="total_vacancies", color="difficulty_level", 
                     hover_data=['cut_off_marks'], barmode="group", 
                     template="plotly_white", color_discrete_map={'Hard': '#ef553b', 'Medium': '#636efa', 'Easy': '#00cc96'})
        st.plotly_chart(fig1, use_container_width=True)

        # 2. Line Chart: Category-wise Cut-offs
        st.markdown("**Competitive Benchmark (Cut-offs)**")
        fig2 = px.line(df, x="exam_year", y="cut_off_marks", color="category", markers=True,
                      line_shape="spline", template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)
        
        # 3. Correlation: Vacancy vs Difficulty
        st.markdown("**Impact Analysis: Vacancy vs Difficulty**")
        fig3 = px.scatter(df, x="total_vacancies", y="cut_off_marks", size="total_vacancies", 
                         color="difficulty_level", hover_name="exam_year", 
                         trendline="ols", size_max=15, template="plotly_white")
        st.plotly_chart(fig3, use_container_width=True)
            
    except Exception as e:
        st.info("💡 Tip: Upload your 'historical_trends.db' to see live strategic alerts.")
        st.error(f"System Note: {e}")
