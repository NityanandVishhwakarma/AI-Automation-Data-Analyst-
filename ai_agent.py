import streamlit as st
import os
import google.generativeai as genai
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.agent_toolkits import create_sql_agent
from fpdf import FPDF
import io

# Naya Error-Free Vector DB (FAISS)
from langchain_community.vectorstores import FAISS

# 1. Configuration & Key Setup
gemini_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=gemini_key)

# Database Connection (Ensure historical_trends.db is in GitHub)
MYSQL_URL = "sqlite:///historical_trends.db"
db = SQLDatabase.from_uri(MYSQL_URL)

# 2. Multi-Agent & Hybrid Setup
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Safe FAISS Initialization
vector_db = None
if os.path.exists("./faiss_index"):
    try:
        vector_db = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"FAISS Load Error: {e}")

# 3. Data Engineer Agent
agent_executor = create_sql_agent(llm=llm, db=db, agent_type="zero-shot-react-description", verbose=True)

# 4. Executive PDF Tool
def generate_pdf_report(analysis_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="UPSC DATA ANALYST - EXECUTIVE BRIEF", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    clean_text = analysis_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# 5. Hybrid Logic (SQL + FAISS Context)
def ask_data_analyst(question):
    try:
        # Step A: SQL Data fetch
        raw_data = agent_executor.invoke({"input": question})
        fetched_info = raw_data['output']
        
        pdf_info = ""
        # Step B: PDF Data fetch (RAG)
        if vector_db is not None:
            docs = vector_db.similarity_search(question, k=1)
            if docs:
                pdf_info = "\n\n**Official Insight:** " + docs[0].page_content

        # Step C: Executive Analyst Summary
        summary_prompt = f"Analyze this UPSC data and provide 3 executive bullet points: {fetched_info} {pdf_info}"
        executive_brief = llm.invoke(summary_prompt).content
        
        return f"{fetched_info}{pdf_info}\n\n---\n### 📊 Executive Brief\n{executive_brief}"
    except Exception as e:
        if "429" in str(e): return "❌ Quota Exhausted! Wait 1 min."
        return f"❌ System Error: {e}"
