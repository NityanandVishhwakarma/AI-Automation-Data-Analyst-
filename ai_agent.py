import streamlit as st
import google.generativeai as genai
from sqlalchemy import create_engine
import pandas as pd
from fpdf import FPDF

# 1. API Configuration
gemini_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Database Connection
# Ensure 'historical_trends.db' is in your GitHub root folder
engine = create_engine("sqlite:///historical_trends.db")

def ask_data_analyst(question):
    try:
        # Step A: AI writes SQL
        sql_prompt = f"""
        Database table 'exam_trends' has columns: exam_year, category, cut_off_marks, total_vacancies, difficulty_level.
        Write ONLY the SQL query for: {question}. No markdown, no backticks.
        """
        query_response = model.generate_content(sql_prompt).text.strip()
        clean_query = query_response.replace('```sql', '').replace('```', '').strip()
        
        # Step B: Execute Query
        df_result = pd.read_sql(clean_query, engine)
        
        # Step C: Executive Summary
        analysis_prompt = f"Analyze this UPSC data: {df_result.to_string()}. Provide 3 executive bullet points."
        executive_brief = model.generate_content(analysis_prompt).text
        
        return f"**Data Result:**\n\n{df_result.to_string()}\n\n---\n### 📊 Executive Brief\n{executive_brief}"
    
    except Exception as e:
        return f"❌ System Error: {e}"

def generate_pdf_report(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="UPSC STRATEGIC REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    clean_text = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')
