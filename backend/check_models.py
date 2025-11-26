import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load your existing environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env")
    exit()

print(f"🔑 Using API Key ending in: ...{api_key[-4:]}")
print("📡 Connecting to Google to list available models...")

try:
    genai.configure(api_key=api_key)
    
    found_any = False
    for m in genai.list_models():
        # We only care about models that can generate content (text/images)
        if 'generateContent' in m.supported_generation_methods:
            found_any = True
            print(f"✅ AVAILABLE: {m.name}")
            
    if not found_any:
        print("❌ No models found. Your API key might differ from the region or project settings.")

except Exception as e:
    print(f"❌ Error: {str(e)}")