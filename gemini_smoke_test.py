import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

MODEL = os.environ.get("GEMINI_MODEL", "models/gemini-flash-latest")
model = genai.GenerativeModel(MODEL)

resp = model.generate_content(
    'Return STRICT JSON only: {"ok": true, "model": "' + MODEL + '"}',
    generation_config={
        "response_mime_type": "application/json",
        "temperature": 0
    }
)

print("=== resp.text repr ===")
print(repr(resp.text))
print("\n=== resp ===")
print(resp)