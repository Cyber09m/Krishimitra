"""
Chatbot LLM client — Google Gemini via the Google AI Studio API key.

Uses the plain REST endpoint (generativelanguage.googleapis.com) rather
than the google-generativeai SDK, to keep this dependency-light and
consistent with how utils/vision_client.py talks to its provider —
one `requests` call, isolated behind a single function, so swapping
providers again later only touches this file.
"""
import requests
from flask import current_app

GEMINI_ENDPOINT_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

SYSTEM_PROMPT = """You are KrishiMitra, an agricultural advisory assistant for Indian farmers.

Rules you must follow:
- Answer only agriculture-related questions: crops, soil, irrigation, pests/disease,
  weather-driven farming decisions, market prices, and government schemes.
- If asked about eligible government schemes, ONLY reference the schemes provided to you
  in the "ELIGIBLE_SCHEMES" context below — never invent a scheme or claim eligibility
  for one not listed there. If none are listed, say the farmer's profile doesn't currently
  match any scheme in our database and suggest they complete their profile (state, crop,
  land size) for a better match.
- Keep answers concise, practical, and in plain language a smallholder farmer would find useful.
- If a question falls outside agriculture, politely redirect to what you can help with.
"""


class GeminiError(Exception):
    pass


def ask_chatbot(message: str, farmer_context: dict, eligible_schemes: list) -> str:
    """
    Same grounding contract as before the provider swap: the LLM only ever
    explains/reasons over schemes the deterministic rule-based matcher
    (utils/scheme_matcher.py) has already decided the farmer is eligible
    for — it never performs the eligibility decision itself.
    """
    api_key = current_app.config["GEMINI_API_KEY"]
    model = current_app.config["GEMINI_MODEL"]

    if not api_key:
        raise GeminiError(
            "GEMINI_API_KEY is not configured. Add your Google AI Studio key to .env."
        )

    schemes_block = (
        "\n".join(f"- {s['name']}: {s['description']}" for s in eligible_schemes)
        if eligible_schemes else "(no matching schemes for this farmer's profile)"
    )

    context_block = (
        f"Farmer context — state: {farmer_context.get('state', 'unknown')}, "
        f"primary crop: {farmer_context.get('primary_crop', 'unknown')}, "
        f"land size: {farmer_context.get('land_size_acres', 'unknown')} acres.\n"
        f"ELIGIBLE_SCHEMES:\n{schemes_block}"
    )

    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [
            {"role": "user", "parts": [{"text": f"{context_block}\n\nFarmer's question: {message}"}]}
        ],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 500},
    }

    url = GEMINI_ENDPOINT_TEMPLATE.format(model=model)

    try:
        response = requests.post(
            url,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        # Surface the response body when there is one — Gemini's error
        # messages (bad model name, quota exceeded, invalid key) are
        # specific and worth showing rather than swallowing.
        detail = ""
        if exc.response is not None:
            try:
                detail = f" — {exc.response.json().get('error', {}).get('message', '')}"
            except ValueError:
                detail = f" — {exc.response.text[:200]}"
        raise GeminiError(f"Gemini API call failed{detail}") from exc

    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as exc:
        raise GeminiError(f"Unexpected Gemini response shape: {data}") from exc
