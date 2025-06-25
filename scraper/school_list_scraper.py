# scraper/school_list_scraper.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_school_list(district_website_url):
    """
    Scrape the district's schools directory page and return a list of schools.

    Args:
        district_website_url (str): URL to the district's main site or schools page.

    Returns:
        list of dict: Each dict contains:
            'school_name': str,
            'school_url': str
    """
    response = requests.get(district_website_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    schools = []

    # Try common selector for school links
    for link in soup.select('a.school-name'):
        name = link.get_text(strip=True)
        url = urljoin(district_website_url, link.get('href', ''))
        schools.append({'school_name': name, 'school_url': url})

    # Fallback: look for list items under a 'schools' class
    if not schools:
        ul = soup.find('ul', class_='schools')
        if ul:
            for li in ul.find_all('li'):
                a = li.find('a')
                if a:
                    name = a.get_text(strip=True)
                    url = urljoin(district_website_url, a.get('href', ''))
                    schools.append({'school_name': name, 'school_url': url})

    return schools

