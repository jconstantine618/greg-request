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
openai.api_key = st.secrets["openai_api_key"]

def load_states():
    here = os.path.dirname(__file__)
    path = os.path.join(here, "data", "us_states_and_canada_provinces.json")
    with open(path, "r") as f:
        return json.load(f)

def main():
    st.title("📚 School District Principal Scraper")
    st.write("Use ChatGPT to find your district, scrape every school page, and pull out principal contact info.")

    # -- State / Province selection --
    country = st.selectbox("Country", list(load_states().keys()), key="country_select")
    state   = st.selectbox("State/Province", load_states()[country], key="state_select")

    # -- District search input --
    district_query = st.text_input("District name (fuzzy search)", key="district_input")
    if st.button("Search Districts", key="search_btn"):
        with st.spinner("Consulting ChatGPT…"):
            districts = search_districts(state, district_query)
    else:
        districts = []

    # -- District selection & website lookup --
    if districts:
        district = st.selectbox("Select District", districts, key="district_select")
        if st.button("Find District Website", key="find_website_btn"):
            with st.spinner("Looking up website…"):
                directory_url = find_district_website(district)
            st.markdown(f"**Official URL:** [{directory_url}]({directory_url})")
        else:
            directory_url = None

        # -- Scrape schools & principals --
        if directory_url and st.button("Scrape Schools & Principals", key="scrape_btn"):
            with st.spinner("Gathering schools…"):
                schools = get_school_list(directory_url)
                records = []
                for sch in schools:
                    html = requests.get(sch["school_url"]).text
                    info = parse_principal_info(html)
                    records.append({
                        "School Name": sch["school_name"],
                        "Principal First Name": info.get("first_name"),
                        "Principal Last Name": info.get("last_name"),
                        "Principal Email": info.get("email"),
                        "Principal Phone": info.get("phone"),
                        "Bio": info.get("bio"),
                        "Notes": info.get("notes"),
                    })
                df = pd.DataFrame(records)
                st.dataframe(df)
                st.download_button("Download CSV", data=df.to_csv(index=False), file_name="principals.csv", key="download_csv")

if __name__ == "__main__":
    main()

