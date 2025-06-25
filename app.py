import os
import json
import streamlit as st
import openai
import pandas as pd

from scraper.district_search import search_districts
from scraper.website_finder import scrape_principals_llm

# Load OpenAI API key
openai.api_key = st.secrets['openai_api_key']


def load_states():
    here = os.path.dirname(__file__)
    path = os.path.join(here, 'data', 'us_states_and_canada_provinces.json')
    with open(path, 'r') as f:
        return json.load(f)


def main():
    st.set_page_config(page_title='School District Principal Scraper')
    st.title('📚 School District Principal Scraper')
    st.write('Search the web to find principal contact info based only on state and district name.')

    states_map = load_states()

    country = st.selectbox('Country', list(states_map.keys()), key='country_select')
    state   = st.selectbox('State/Province', states_map[country], key='state_select')
    district_query = st.text_input('District name (fuzzy search)', key='district_input')

    if st.button('Search Districts', key='search_btn'):
        st.session_state.districts = search_districts(state, district_query)

    districts = st.session_state.get('districts', [])
    if districts:
        district = st.selectbox('Select District', districts, key='district_select')
        if st.button('Scrape Principals', key='scrape_btn'):
            with st.spinner('Gathering principal info…'):
                records = scrape_principals_llm(state, district)
                df = pd.DataFrame(records)
                st.dataframe(df)
                st.download_button('Download CSV', data=df.to_csv(index=False), file_name='principals.csv', key='download_csv')

if __name__ == '__main__':
    main()
