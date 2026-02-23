import google.generativeai as genai

# Yahan apni actual Gemini API key daalein
API_KEY = "AIzaSyCbpIY4YjmtRDqZyw4RWE5kHDXtg_NBfuU"

genai.configure(api_key=API_KEY)

print("🔍 Aapki API Key in models ko support karti hai:\n")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ {m.name}")
except Exception as e:
    print(f"❌ Error: {e}")