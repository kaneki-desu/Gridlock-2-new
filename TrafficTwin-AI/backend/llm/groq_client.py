import os
import requests
from typing import Dict, List

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"


def build_llm_prompt(current_incident, recommendation, similar_incidents):
    llm_prompt= f"""
You are a traffic incident response planner.

Current Incident:
{current_incident}

Recommendation:
{recommendation}

Similar Incidents:
{similar_incidents}


Provide:
1.Infer from past similar incidents(if any)and forecast event-related traffic impact , duration of congestion , etc
2. Required policemen(if any)
3. Barricade needs(if any)
4. Or any other recommendation...

Keep it concise and operational.
"""
    print("LLM i/p:", llm_prompt,'\n')
    return llm_prompt


def get_llm_suggestions(
    current_incident: Dict,
    recommendation: Dict,
    similar_incidents: List[Dict]
):
    if not GROQ_API_KEY:
        return "Missing GROQ_API_KEY"

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "user",
                "content": build_llm_prompt(
                    current_incident,
                    recommendation,
                    similar_incidents
                )
            }
        ],
        "temperature": 0.3,
        "max_tokens": 256
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Groq error: {str(e)}"