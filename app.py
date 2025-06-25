import os
import json
import streamlit as st
import openai
import requests
import pandas as pd

from scraper.district_search import search_districts
from scraper.website_finder import find_district_website
from scraper.school_list_scraper import get_school_list
from scraper.principle_parser import parse_principal_info

# Initialize API key
openai.api_key = st.secrets['openai_api_key']

# Session defaults
if 'districts' not in st.session_state:
    st.session_state['districts'] = []
if 'directory_url' not in st.session_state:
    st.session_state['directory_url'] = ''

def load_states():
    here = os.path.dirname(__file__)
    path = os.path.join(here, 'data', 'us_states_and_canada_provinces.json')
    with open(path, 'r') as f:
        return json.load(f)

st.title('📚 School District Principal Scraper')
st.write('Use ChatGPT to find your district, scrape every school page, and pull out principal contact info.')

states_map = load_states()

# Form 1: Search Districts
with st.form('search_form'):
    country = st.selectbox('Country', list(states_map.keys()), key='form_country')
    state   = st.selectbox('State/Province', states_map[country], key='form_state')
    district_input = st.text_input('District name (fuzzy search)', key='form_query')
    go = st.form_submit_button('Search Districts')
    if go:
        st.session_state['districts'] = search_districts(state, district_input)

# Show District choices if available
if st.session_state['districts']:
    st.write('### Select your district:')
    # Form 2: Get Website
    with st.form('website_form'):
        district = st.selectbox('District', st.session_state['districts'], key='form_district')
        go_url = st.form_submit_button('Find District Website')
        if go_url:
            st.session_state['directory_url'] = find_district_website(district)

# Show website if found
if st.session_state['directory_url']:
    st.markdown(f"**Official URL:** [{st.session_state['directory_url']}]({st.session_state['directory_url']})")

    # Form 3: Scrape Principals
    with st.form('scrape_form'):
        go_scrape = st.form_submit_button('Scrape Schools & Principals')
        if go_scrape:
            schools = get_school_list(st.session_state['directory_url'])
            rows = []
            for sch in schools:
                html = requests.get(sch['school_url']).text
                info = parse_principal_info(html)
                rows.append({
                    'School Name': sch['school_name'],
                    'Principal First Name': info.get('first_name'),
                    'Principal Last Name': info.get('last_name'),
                    'Principal Email': info.get('email'),
                    'Principal Phone': info.get('phone'),
                    'Bio': info.get('bio'),
                    'Notes': info.get('notes'),
                })
            df = pd.DataFrame(rows)
            st.dataframe(df)
            st.download_button('Download CSV', data=df.to_csv(index=False), file_name='principals.csv', key='download_csv')

