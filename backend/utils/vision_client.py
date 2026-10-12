"""
Disease detection via Gemini's multimodal vision input — needs only the
same Gemini API key used for the chatbot, no separate computer-vision
account, dataset annotation, or model training.

Trade-off worth stating plainly in an interview: this is a general-purpose
multimodal model reasoning over an image with a text prompt, not a model
specifically trained on a labeled leaf-disease dataset the way a dedicated
image-classification model would be. It's faster to stand up and
genuinely works, but a purpose-trained CV model — trained on thousands of
labeled leaf photos for exactly this task — is still the more rigorous
answer for a production system at scale. This is the pragmatic "one
provider, working end-to-end" choice for a project at this stage, not a
claim that it's the more sophisticated approach.

The class list is pulled from data/treatments.json and passed to Gemini as
an enum constraint on the response schema — Gemini is structurally
prevented from returning a class name outside that list, so this can't
silently drift out of sync with the treatment lookup table.
"""
import json
import os
import requests
from flask import current_app

GEMINI_ENDPOINT_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

_TREATMENTS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "treatments.json")
with open(_TREATMENTS_PATH) as f:
    _KNOWN_CLASSES = list(json.load(f).keys())

VISION_PROMPT = (
    "You are an expert plant pathologist. Look at this leaf photo and identify "
    "which of the following disease classes it most closely matches: "
    f"{', '.join(_KNOWN_CLASSES)}. "
    "If the leaf looks healthy with no visible disease symptoms, choose 'Healthy'. "
    "Also estimate your confidence in this diagnosis as a number between 0 and 1, "
    "based on how clear and unambiguous the visual symptoms are — use a LOW "
    "confidence (below 0.5) if the image is blurry, poorly lit, doesn't show "
    "the leaf clearly, or the symptoms could plausibly match more than one class."
)

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "class": {"type": "STRING", "enum": _KNOWN_CLASSES},
        "confidence": {"type": "NUMBER"},
        "reasoning": {"type": "STRING"},
    },
    "required": ["class", "confidence"],
}

_MIME_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
}


class VisionError(Exception):
    pass


def _mime_type_for(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return _MIME_TYPES.get(ext, "image/jpeg")


def detect_disease(image_bytes: bytes, filename: str) -> dict:
    """
    Returns {"class": str, "confidence": float, "raw": dict} — routes/disease.py
    reads this shape without needing to know it came from Gemini specifically.
    """
    import base64

    api_key = current_app.config["GEMINI_API_KEY"]
    model = current_app.config["GEMINI_MODEL"]

    if not api_key:
        raise VisionError(
            "GEMINI_API_KEY is not configured. Add your Google AI Studio key to .env."
        )

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = _mime_type_for(filename)

    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"inline_data": {"mime_type": mime_type, "data": encoded_image}},
                {"text": VISION_PROMPT},
            ],
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
            "temperature": 0.2,
        },
    }

    url = GEMINI_ENDPOINT_TEMPLATE.format(model=model)

    try:
        response = requests.post(
            url,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=25,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        detail = ""
        if exc.response is not None:
            try:
                detail = f" — {exc.response.json().get('error', {}).get('message', '')}"
            except ValueError:
                detail = f" — {exc.response.text[:200]}"
        raise VisionError(f"Gemini vision call failed{detail}") from exc

    data = response.json()
    try:
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(raw_text)
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        raise VisionError(f"Unexpected Gemini response shape: {data}") from exc

    return {
        "class": parsed["class"],
        "confidence": float(parsed["confidence"]),
        "raw": parsed,
    }
