import os
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types


client = genai.Client()


def generate_answer(system_prompt: str) -> str:
    try:
        resp = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=system_prompt, 
        )
        print(resp.text)
        return resp.text
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "[Local mock] Unable to call Gemini. Provide mock answer."


