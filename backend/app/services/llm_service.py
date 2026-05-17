import json
from app.config import settings

client = None


def get_client():
    global client
    if client is None:
        if not settings.GROQ_API_KEY:
            print("WARNING: No Groq API key configured.")
            return None

        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
        except Exception as e:
            print(f"Failed to initialize Groq client: {e}")
            return None

    return client


def call_llm(system_prompt, user_prompt, temperature=0.1, max_tokens=4000, json_mode=False):
    groq_client = get_client()
    if groq_client is None:
        raise Exception("Groq API key not configured.")

    try:
        kwargs = {
            "model": settings.LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = groq_client.chat.completions.create(**kwargs)
        result = response.choices[0].message.content
        
        print(f"Groq tokens used: {response.usage.total_tokens}")
        return result

    except Exception as e:
        print(f"Groq call failed: {e}")
        raise


def call_llm_json(system_prompt, user_prompt, **kwargs):
    result = call_llm(system_prompt, user_prompt, json_mode=True, **kwargs)

    try:
        return json.loads(result)
    except json.JSONDecodeError:
        try:
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
        except Exception:
            pass
        raise ValueError(f"LLM did not return valid JSON:\n{result}")