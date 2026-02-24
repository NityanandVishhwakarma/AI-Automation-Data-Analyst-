import streamlit as st
import os
import google.generativeai as genai
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import create_sql_agent
from fpdf import FPDF
from pypdf import PdfReader # Simple library for PDF
import io

# 1. Configuration
gemini_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=gemini_key)

# Database Connection
MYSQL_URL = "sqlite:///historical_trends.db"
db = SQLDatabase.from_uri(MYSQL_URL)

# 2. LLM Setup
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# 3. Simple PDF Reader Function (No Database Needed)
def get_pdf_text():
    pdf_text = ""
    pdf_path = "data/upsc_notification.pdf" # Apni PDF ka naam yahan sahi karein
    if os.path.exists(pdf_path):
        reader = PdfReader(pdf_path)
        for page in reader.pages[:5]: # Sirf pehle 5 pages read karega
            pdf_text += page.extract_text()
    return pdf_text

# 4. SQL Agent
agent_executor = create_sql_agent(llm=llm, db=db, agent_type="zero-shot-react-description", verbose=True)

# 5. Executive PDF Generator
def generate_pdf_report(analysis_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="UPSC EXECUTIVE REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    clean_text = analysis_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# 6. Hybrid Logic (Direct PDF Text + SQL)
def ask_data_analyst(question):
    try:
        # Step A: Get SQL Data
        raw_data = agent_executor.invoke({"input": question})
        fetched_info = raw_data['output']
        
        # Step B: Get PDF Content directly
        pdf_content = get_pdf_text()
        
        # Step C: Executive Analyst combines everything
        summary_prompt = f"""
        Analyze this UPSC data: {fetched_info}
        Context from Official PDF: {pdf_content[:2000]} 
        Question: {question}
        Provide 3 Executive Insights and a strategic advice.
        """
        executive_brief = llm.invoke(summary_prompt).content
        
        return f"{fetched_info}\n\n---\n### 📊 Executive Brief\n{executive_brief}"
    except Exception as e:
        if "429" in str(e): return "❌ Quota limit! Wait 1 min."
        return f"❌ Error: {e}"
