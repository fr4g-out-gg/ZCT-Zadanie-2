import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

def ask_gemini(activities):
    formatted = ", ".join([f"{a['topic']}: {a['study_time']} min" for a in activities])
    prompt = (
        f"Používateľ sa učil tieto témy: {formatted}. "
        "Porovnaj čas strávený na jednotlivých témach a odporuč, ktorým by sa mal venovať viac a prečo."
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
    params={"key": API_KEY},
    json=payload
)


    if response.status_code != 200:
        raise Exception("Gemini API chyba: " + response.text)

    result = response.json()
    return result['candidates'][0]['content']['parts'][0]['text']

