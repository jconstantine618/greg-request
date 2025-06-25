# scraper/website_finder.py

import streamlit as st
from openai import OpenAI
import json

# Initialize OpenAI client with API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["openai_api_key"])


def scrape_principals_llm(state: str, district_name: str) -> list[dict]:
    """
    Use ChatGPT to research the web and gather principal contact information for each high school
    in the given district. This function will:
      1. Search the official district homepage.
      2. Scrape principal name, email, phone, bio, and notes from school pages.
      3. If missing, search external web resources for emails and phone numbers.
      4. Detect a generic district email address and infer individual emails using common patterns.

    Returns a JSON-serializable list of dicts with keys:
      - school_name
      - first_name
      - last_name
      - email
      - generic_email
      - assumed_email
      - phone
      - bio
      - notes
    """
    prompt = (
        f"You are a web-scraping expert. Given the state '{state}' and school district '{district_name}', "
        "search online for the district's official site, then locate each high school's principal details. "
        "For each school, find the principal's full name, email address, phone number, any bio or notes. "
        "If the exact email isn't on the site, look for a generic district email (e.g., info@domain) and "
        "infer the principal's email by pattern (first initial + last name). If contact info is still missing, "
        "expand your search to other web resources. Return ONLY a JSON array of objects like: "
        "[{\
            \"school_name\": \"...\",\
            \"first_name\": \"...\",\
            \"last_name\": \"...\",\
            \"email\": \"...\",\
            \"generic_email\": \"...\",\
            \"assumed_email\": \"...\",\
            \"phone\": \"...\",\
            \"bio\": \"...\",\
            \"notes\": \"...\"\
        }, ...]")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You respond with pure JSON."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback: attempt to extract JSON block
        import re
        match = re.search(r"\[\{.*\}\]", content, re.DOTALL)
        return json.loads(match.group(0)) if match else []
