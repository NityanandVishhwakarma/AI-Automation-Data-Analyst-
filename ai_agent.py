import os
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import create_sql_agent

# 1. Apni Gemini API Key yahan daalein
os.environ["GOOGLE_API_KEY"] = "AIzaSyCbpIY4YjmtRDqZyw4RWE5kHDXtg_NBfuU"

# 2. Database Connection (Apna password zaroor update karein)
MYSQL_URL = "sqlite:///historical_trends.db"

# LangChain ko database connect karne ke liye
db = SQLDatabase.from_uri(MYSQL_URL)

# 3. Initialize the AI Model (Gemini)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0)

# 4. Create the SQL AI Agent
# 'verbose=True' rakhne se hum terminal me dekh payenge ki AI kya soch raha hai aur kaunsi SQL query likh raha hai
agent_executor = create_sql_agent(
    llm=llm, 
    db=db, 
    agent_type="zero-shot-react-description", 
    verbose=True
)

# Purane ask_data_analyst function ko is se replace karein
def ask_data_analyst(question):
    try:
        response = agent_executor.invoke({"input": question})
        return response['output']
    except Exception as e:
        return f"❌ Sorry, an error occurred: {e}"

# Is line ke aage ka hissa (if __name__ == "__main__":) aap delete kar sakte hain, 
# kyunki ab hum isey terminal se nahi, UI se chalayenge.

if __name__ == "__main__":
    print("🤖 AI Data Analyst is waking up...\n")
    
    # Hum ek test question pooch rahe hain apne historical data se
    test_question = "What was the cut off marks for the General category in 2023 Prelims?"
    
    ask_data_analyst(test_question)
