# scraper/website_finder.py

import streamlit as st
from openai import OpenAI

# Initialize new OpenAI client with API key from Streamlit secrets
client = OpenAI(api_key=st.secrets['openai_api_key'])

def find_district_website(district_name):
    """
    Ask ChatGPT for the official website URL of `district_name`.
    Respond with only the URL string.
    """
    prompt = (
        f"What's the official homepage URL of the school district named {district_name!r}? "
        "Respond with only the URL."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Return only the URL, nothing else."},
            {"role": "user",   "content": prompt}
        ]
    )
    return resp.choices[0].message.content.strip()
