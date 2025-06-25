# scraper/principle_parser.py

import re
from bs4 import BeautifulSoup
from nameparser import HumanName


def parse_principal_info(html):
    """
    Extract principal details from a school's contact or staff page HTML.

    Args:
        html (str): Raw HTML of the page.

    Returns:
        dict: {
            'first_name': str or None,
            'last_name': str or None,
            'email': str or None,
            'phone': str or None,
            'bio': str or None,
            'notes': str or None
        }
    """
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ')  

    # Email
    email_match = re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", text)
    email = email_match.group(0) if email_match else None

    # Phone
    phone_match = re.search(r"\(?\d{3}\)?[-\s\.]?\d{3}[-\s\.]?\d{4}", text)
    phone = phone_match.group(0) if phone_match else None

    # Name
    name_tag = soup.find(['h1', 'h2'], text=re.compile(r'Principal', re.I))
    name_text = name_tag.get_text() if name_tag else ''
    human = HumanName(name_text)
    first_name = human.first or None
    last_name = human.last or None

    # Bio (paragraph under "About the Principal")
    bio = None
    about_tag = soup.find(lambda tag: tag.name in ['h3', 'h2'] and 'about the principal' in tag.text.lower())
    if about_tag:
        p = about_tag.find_next_sibling('p')
        bio = p.get_text(strip=True) if p else None

    # Notes (keywords: retiring, moving, replacement)
    notes_list = []
    for tag in soup.find_all(['p', 'li']):
        if re.search(r'retir|moving|replace', tag.get_text(), re.I):
            notes_list.append(tag.get_text(strip=True))
    notes = ' '.join(notes_list) if notes_list else None

    return {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'phone': phone,
        'bio': bio,
        'notes': notes
    }

