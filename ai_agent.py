import streamlit as st
import google.generativeai as genai
from sqlalchemy import create_engine
import pandas as pd
from fpdf import FPDF

# 1. API Setup
gemini_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# 2. Database Connection
# Ensure karein ki 'historical_trends.db' file aapke GitHub repo mein hai
engine = create_engine("sqlite:///historical_trends.db")

def ask_data_analyst(question):
    try:
        # Step A: AI se SQL query likhwana
        sql_prompt = f"""
        You are a SQL Expert. Database has a table 'exam_trends' with columns: 
        exam_year, category, cut_off_marks, total_vacancies, difficulty_level.
        Write ONLY the SQL query (no backticks, no explanation) for this: {question}
        """
        query_response = model.generate_content(sql_prompt).text.strip()
        
        # SQL clean up (agar AI ne ```sql ... ``` likh diya ho)
        clean_query = query_response.replace('```sql', '').replace('```', '').strip()
        
        # Step B: Data Fetch karna
        df_result = pd.read_sql(clean_query, engine)
        
        # Step C: Executive Brief taiyar karna
        analysis_prompt = f"""
        As a Senior UPSC Consultant, analyze this data:
        {df_result.to_string()}
        
        Question: {question}
        
        Provide 3 professional executive bullet points and 1 strategic insight for UPSC aspirants.
        """
        executive_brief = model.generate_content(analysis_prompt).text
        
        return f"**Data Findings:**\n\n{df_result.to_string()}\n\n---\n### 📊 Executive Brief\n{executive_brief}"
    
    except Exception as e:
        if "429" in str(e):
            return "⚠️ Quota limit reached. Please wait 1 minute."
        return f"❌ System Error: {e}"

# 3. Executive PDF Tool
def generate_pdf_report(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="UPSC STRATEGIC ANALYSIS REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    # Cleaning for PDF
    clean_text = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')
