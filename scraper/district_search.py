# scraper/district_search.py

import json
import streamlit as st
from openai import OpenAI

# Initialize new OpenAI client with API key from Streamlit secrets
client = OpenAI(api_key=st.secrets['openai_api_key'])

def search_districts(state, query):
    """
    Ask ChatGPT via the new client to list up to 5 school district names.
    Returns a list of strings.
    """
    prompt = (
        f"List up to 5 official school district names in {state!r} "
        f"that closely match {query!r}. "
        "Return ONLY a JSON array of strings."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a JSON-only responder."},
            {"role": "user",   "content": prompt}
        ]
    )
    text = resp.choices[0].message.content.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback splitting lines
        return [line.strip(" -") for line in text.splitlines() if line.strip()]
