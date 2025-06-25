# scraper/district_search.py

import json
import re
import streamlit as st
from openai import OpenAI

# Initialize OpenAI client with API key from Streamlit secrets
client = OpenAI(api_key=st.secrets['openai_api_key'])

def search_districts(state: str, query: str) -> list[str]:
    """
    Use ChatGPT to list up to 5 official school district names in the given state.
    Response must be a JSON array. Strips markdown fences before parsing.

    Args:
        state: US state or Canadian province name.
        query: Fuzzy name to search for.
    Returns:
        List of matching district names.
    """
    prompt = (
        f"List up to 5 official school district names in {state!r} "
        f"that closely match {query!r}. "
        "Respond with **only** a JSON array of strings, e.g.: [\"Name A\", \"Name B\"]."
    )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You output only JSON."},
            {"role": "user", "content": prompt},
        ],
    )
    raw = resp.choices[0].message.content.strip()
    # Remove Markdown fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```[\s\S]*?\n", "", raw)
        raw = re.sub(r"\n```$", "", raw)
        raw = raw.strip()
    # Parse JSON
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: split lines and strip
        lines = [l.strip(' "-,') for l in raw.splitlines() if l.strip()]
        return lines
