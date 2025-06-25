# scraper/website_finder.py

import requests
from urllib.parse import urlencode

def find_district_website(district_name):
    """
    Construct a Google search URL for the district's official website.
    Replace with a real API integration or scraper in production.

    Args:
        district_name (str): Full name of the school district.

    Returns:
        str: URL to perform the search.
    """
    query = f"{district_name} official website"
    search_url = f"https://www.google.com/search?{urlencode({'q': query})}"
    return search_url

