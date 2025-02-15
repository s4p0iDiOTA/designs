import json
from typing import List

from models import Series
# Get series
#   - Args: content_options
#   - Returns: list of Series objects

# content_options = {
#    "country": "Albania",
#    "year_range": [1951, 1960]
#}
#   - Description: This function retrieves a list of Series objects based on the provided content options. 
#                  It reads data from a JSON file, validates it, and creates Series objects for each entry in the data.

def get_series(content_options: dict) -> List[Series]:
    """Returns a list of Series objects based on the provided content options."""
    # Read data from JSON file
    with open("./data_samples_for_testing/five_series_of_stamps_samples.json", "r") as file:
        data = json.load(file)

    # Create Series objects
    series_list = [Series(item) for item in data]
    
    # Filter Series objects based on content options
    if content_options.get("country"):
        series_list = [series for series in series_list if series.country == content_options["country"]]
    if content_options.get("year_range"):
        series_list = [series for series in series_list if series.year in range(content_options["year_range"][0], content_options["year_range"][1] + 1)]
    
    return series_list
