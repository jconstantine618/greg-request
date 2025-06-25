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

# Initialize OpenAI (ChatGPT) API key
openai.api_key = st.secrets['openai_api_key']

def load_states():
    """Load US states and Canadian provinces from JSON."""
    here = os.path.dirname(__file__)
    path = os.path.join(here, 'data', 'us_states_and_canada_provinces.json')
    with open(path, 'r') as f:
        return json.load(f)

def main():
    st.title('📚 School District Principal Scraper')
    st.write('Use ChatGPT to find your district, scrape every school page, and pull out principal contact info.')

    # Load selection data
    states_map = load_states()

    # Selection widgets
    country = st.selectbox('Country', list(states_map.keys()), key='country_select')
    state = st.selectbox('State/Province', states_map[country], key='state_select')

    # District search
    district_query = st.text_input('District name (fuzzy search)', key='district_input')
    if st.button('Search Districts', key='search_btn'):
        with st.spinner('Consulting ChatGPT…'):
            districts = search_districts(state, district_query)
        st.session_state['districts'] = districts
    else:
        districts = st.session_state.get('districts', [])

    # District and website
    if districts:
        district = st.selectbox('Select District', districts, key='district_select')
        if st.button('Find District Website', key='find_website_btn'):
            with st.spinner('Looking up website…'):
                directory_url = find_district_website(district)
            st.session_state['directory_url'] = directory_url
        else:
            directory_url = st.session_state.get('directory_url', '')

        if directory_url:
            st.markdown(f"**Official URL:** [{directory_url}]({directory_url})")

            # Scrape schools & principals
            if st.button('Scrape Schools & Principals', key='scrape_btn'):
                with st.spinner('Gathering schools…'):
                    schools = get_school_list(directory_url)
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

if __name__ == '__main__':
    main()
