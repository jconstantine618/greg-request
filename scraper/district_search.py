# scraper/district_search.py

import openai
import json

def search_districts(state, query):
    """
    Ask ChatGPT to list up to 5 school-district names in `state`
    matching `query`. Returns a Python list of strings.
    """
    prompt = (
        f"List up to 5 official school district names in {state!r} "
        f"that closely match {query!r}. "
        "Return **ONLY** a JSON array of strings, e.g. [\"Name A\", \"Name B\", ...]."
    )

    resp = openai.ChatCompletion.create(
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
        # Fallback: split on lines
        return [line.strip(" -") for line in text.splitlines() if line.strip()]

