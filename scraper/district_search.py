# scraper/district_search.py

from rapidfuzz import process

# TODO: Replace with actual data source (e.g., NCES CSV or provincial API)
DISTRICTS = {
    "California": [
        "Los Angeles Unified School District",
        "San Diego Unified School District",
        "San Francisco Unified School District",
    ],
    "Ontario": [
        "Toronto District School Board",
        "Peel District School Board",
        "Ottawa-Carleton District School Board",
    ],
}

def search_districts(state, query, limit=5, threshold=75):
    """
    Fuzzy search for school districts in a given state or province.

    Args:
        state (str): Name of the state or province.
        query (str): Partial or full district name to search.
        limit (int): Max number of results to return.
        threshold (int): Minimum matching score (0-100).

    Returns:
        List[str]: Matching district names.
    """
    districts = DISTRICTS.get(state, [])
    if not districts:
        return []
    matches = process.extract(query, districts, limit=limit)
    return [name for name, score, _ in matches if score >= threshold]

