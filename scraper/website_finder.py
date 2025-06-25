# scraper/website_finder.py

import streamlit as st
from openai import OpenAI
import json
import requests
from scraper.school_list_scraper import get_school_list
from scraper.principle_parser import parse_principal_info

# Initialize OpenAI client with API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["openai_api_key"])

def find_district_website(district_name: str) -> str:
    """
    Ask ChatGPT for the official website URL of `district_name`.
    Respond with only the URL string.

    Args:
        district_name (str): Full name of the school district.

    Returns:
        str: The official homepage URL.
    """
    prompt = (
        f"What's the official homepage URL of the school district named {district_name!r}? "
        "Respond with only the URL (e.g. https://www.example.k12.state.us)."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You respond with exactly one URL, nothing else."},
            {"role": "user",   "content": prompt}
        ]
    )
    return resp.choices[0].message.content.strip()


def scrape_principals_llm(district_url: str) -> list[dict]:
    """
    Use ChatGPT to extract principal contact info for each high school in the district.

    Args:
        district_url (str): Base URL of the district's official site.

    Returns:
        List[dict]: Each dict contains keys:
            - school_name
            - first_name
            - last_name
            - email
            - phone
            - bio
            - notes
    """
    prompt = (
        f"Given the school district homepage URL: {district_url}, "
        "locate the 'Our Schools' or 'Directory' section, then for each high school, "
        "extract the principal's full name, email address, phone number, any brief bio, and pertinent notes. "
        "Return a JSON array of objects with the following keys: "
        "school_name, first_name, last_name, email, phone, bio, notes."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a JSON-only web-scraping assistant. Output only valid JSON."},
            {"role": "user",   "content": prompt}
        ]
    )
    content = resp.choices[0].message.content.strip()
    if content.startswith("```json"):
        content = content.split("```json")[-1].strip().rstrip("```")
    return json.loads(content)


def get_principals(district_url: str) -> list[dict]:
    """
    Attempt HTML scraping first; on failure, fallback to LLM scraping.

    Args:
        district_url (str): Base URL of the district's official site.

    Returns:
        List[dict]: List of principal info dicts.
    """
    try:
        schools = get_school_list(district_url)
        principals = []
        for sch in schools:
            try:
                html = requests.get(sch['school_url'], timeout=10).text
                info = parse_principal_info(html)
                principals.append({'school_name': sch['school_name'], **info})
            except Exception:
                continue
        return principals
    except requests.exceptions.RequestException:
        st.warning("Could not fetch school list; falling back to LLM-based scraping.")
        return scrape_principals_llm(district_url)
