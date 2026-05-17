from app.config import settings
from groq import Groq

print(f"API Key (first 20 chars): {settings.GROQ_API_KEY[:20]}...")
print(f"Model: {settings.LLM_MODEL}")

try:
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "user", "content": "Say hello in one short sentence."}
        ],
        max_tokens=50
    )
    
    print("✅ Groq works!")
    print("Response:", response.choices[0].message.content)
    print(f"Tokens used: {response.usage.total_tokens}")
    
except Exception as e:
    print(f"❌ Groq failed: {e}")