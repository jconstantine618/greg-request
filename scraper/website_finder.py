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
    Use ChatGPT to extract principal contact info for each high school in the district,
    including fallback search across the web if details are missing.

    Args:
        district_url (str): Base URL of the district's official site.

    Returns:
        List[dict]: Each dict contains keys:
            - school_name
            - first_name
            - last_name
            - email              # found on site
            - generic_email      # generic district-level address
            - assumed_email      # generated pattern-based email
            - phone              # school-specific or district number
            - bio
            - notes
    """
    prompt = (
        f"Given the school district homepage URL: {district_url}, "
        "first locate the 'Our Schools' or 'Directory' section and identify each high school. "
        "For each high school principal, extract: full name, official email address (if on the site), "
        "generic district-level email (e.g. info@…), "
        "and phone number for that school or a main district line. "
        "If an individual email isn't available, look at existing email patterns for the district "
        "and generate an assumed email (e.g. first initial + last name@...). "
        "Also capture any brief bio or pertinent notes (retirement, transitions, etc.). "
        "Return a JSON array of objects with these exact keys: "
        "school_name, first_name, last_name, email, generic_email, assumed_email, phone, bio, notes."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a JSON-only web-scraping assistant. Output only valid JSON."},
            {"role": "user",   "content": prompt}
        ]
    )
    content = resp.choices[0].message.content.strip()
    # strip fences if present
    if content.startswith("```json"):
        content = content.split("```json")[-1].strip().rstrip("```")
    return json.loads(content)


def get_principals(district_url: str) -> list[dict]:
    """
    Attempt HTML scraping first; on failure or missing fields, fallback to LLM scraping.
    """
    principals = []
    try:
        schools = get_school_list(district_url)
        for sch in schools:
            try:
                html = requests.get(sch['school_url'], timeout=10).text
                info = parse_principal_info(html)
                # merge with new fields placeholder
                principals.append({
                    'school_name': sch['school_name'],
                    'first_name': info.get('first_name'),
                    'last_name': info.get('last_name'),
                    'email': info.get('email'),
                    'generic_email': info.get('generic_email'),
                    'assumed_email': info.get('assumed_email'),
                    'phone': info.get('phone'),
                    'bio': info.get('bio'),
                    'notes': info.get('notes'),
                })
            except Exception:
                continue
        # if some principals lack email/phone, use LLM to fill
        incomplete = [p for p in principals if not p.get('email') or not p.get('phone')]
        if incomplete:
            st.info("Some contact info missing; invoking fallback LLM enrichment.")
            enriched = scrape_principals_llm(district_url)
            return enriched
        return principals
    except requests.exceptions.RequestException:
        st.warning("Could not fetch school list; falling back to LLM-based scraping.")
        return scrape_principals_llm(district_url)
