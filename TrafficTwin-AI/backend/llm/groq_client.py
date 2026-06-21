import json
import os
from typing import Dict, List, Optional

import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/v1/outputs")
GROQ_MODEL = os.getenv("GROQ_MODEL", "groq-llama-3.5-mini")


def build_llm_prompt(
    current_incident: Dict[str, str],
    recommendation: Dict[str, str],
    similar_incidents: List[Dict[str, str]],
) -> str:
    incident_fields = []
    for key, value in current_incident.items():
        incident_fields.append(f"- {key}: {value}")

    similar_text = []
    for index, similar in enumerate(similar_incidents, start=1):
        similar_lines = [f"    {k}: {v}" for k, v in similar.items()]
        similar_text.append(f"Similar incident {index}:\n" + "\n".join(similar_lines))

    recommendation_lines = [f"- {k}: {v}" for k, v in recommendation.items()]

    prompt = (
        "You are a traffic incident response planner. Use the current incident details and the top 3 most similar past incidents "
        "to provide actionable operational suggestions. Include: number of policemen, barricade needs, ground clearance actions, "
        "and any immediate response priorities. Keep the answer concise and practical.\n\n"
        "Current incident details:\n"
        + "\n".join(incident_fields)
        + "\n\nRecommendation summary:\n"
        + "\n".join(recommendation_lines)
        + "\n\nPast similar incidents:\n"
        + "\n\n".join(similar_text)
        + "\n\nProvide a single actionable response for the incident." 
    )
    return prompt


def parse_groq_response(response_json: Dict) -> str:
    if not response_json:
        return "Groq LLM did not return a response."

    if isinstance(response_json, dict):
        if "output" in response_json:
            output = response_json["output"]
            if isinstance(output, list) and output:
                first = output[0]
                if isinstance(first, dict):
                    if "content" in first and isinstance(first["content"], list):
                        content = first["content"]
                        if content and isinstance(content[0], dict) and "text" in content[0]:
                            return content[0]["text"]
                    if "text" in first:
                        return first["text"]
                return str(first)
        if "choices" in response_json:
            choices = response_json["choices"]
            if isinstance(choices, list) and choices:
                choice = choices[0]
                if isinstance(choice, dict) and "text" in choice:
                    return choice["text"]
                return str(choice)

    return json.dumps(response_json)


def get_llm_suggestions(
    current_incident: Dict[str, str],
    recommendation: Dict[str, str],
    similar_incidents: List[Dict[str, str]],
) -> str:
    if not GROQ_API_KEY:
        return (
            "GROQ_API_KEY not configured. Unable to generate LLM suggestions. "
            "Set GROQ_API_KEY in environment variables to enable Groq suggestions."
        )

    prompt = build_llm_prompt(current_incident, recommendation, similar_incidents)
    payload = {
        "model": GROQ_MODEL,
        "input": prompt,
        "temperature": 0.3,
        "max_output_tokens": 256,
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        return parse_groq_response(response.json())
    except requests.RequestException as exc:
        return f"GROQ request failed: {exc}"
    except ValueError:
        return "GROQ response could not be decoded."  
