# scraper/website_finder.py

import openai

def find_district_website(district_name):
    """
    Ask ChatGPT for the official website URL of `district_name`.
    Returns the URL string.
    """
    prompt = (
        f"What's the official homepage URL of the school district named {district_name!r}? "
        "Respond with only the URL (e.g. https://www.example.k12.state.us)."
    )

    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You answer with exactly one URL, nothing else."},
            {"role": "user",   "content": prompt}
        ]
    )
    return resp.choices[0].message.content.strip()
