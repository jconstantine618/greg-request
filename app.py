import os
import json
import streamlit as st
from scraper.district_search import search_districts
from scraper.website_finder import find_district_website

def load_states():
    """Load list of US states and Canadian provinces from JSON file."""
    file_dir = os.path.dirname(__file__)
    file_path = os.path.join(file_dir, "data", "us_states_and_canada_provinces.json")
    with open(file_path, "r") as f:
        return json.load(f)

def main():
    st.title("School District Principal Contact Finder")

    states = load_states()
    state = st.selectbox("Select a state or province", [""] + states)
    query = st.text_input("Enter district name (fuzzy search)")

    if state and query:
        districts = search_districts(state, query)
        if districts:
            district = st.selectbox("Select the correct district", districts)
            if st.button("Find District Website"):
                website_url = find_district_website(district)
                st.write("District Website:", website_url)
        else:
            st.warning("No matching districts found. Try a different query.")

if __name__ == "__main__":
    main()

