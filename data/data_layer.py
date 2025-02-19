from data.models import Series
from typing import List, Dict, Any
import unittest
import json
import os

# Get series
#   - Args: content_options
#   - Returns: list of Series objects

# content_options = {
#    "country": "Albania",
#    "year_range": [1951, 1960]
#}
#   - Description: This function retrieves a list of Series objects based on the provided content options. 
#                  It reads data from a JSON file, validates it, and creates Series objects for each entry in the data.

def get_series(content_options: dict, directory_path: str) -> List[Series]:
    """Returns a list of Series objects based on the provided content options."""
    # Read data from JSON file
    
    #data= read_json(content_options, directory_path)
    with open("./_test_samples/multi_country_series_1950-1960.json", "r") as file:  # resolver!!
        data = json.load(file)

    # Create Series objects
    series_list = [Series(item) for item in data]
    
    # Filter Series objects based on content options
    if content_options.get("country"):
        series_list = [series for series in series_list if series.country == content_options["country"]]
    if content_options.get("year_range"):
        series_list = [series for series in series_list if series.year in range(content_options["year_range"][0], content_options["year_range"][1] + 1)]
    
    return series_list


def read_json(file_name: str, directory_path: str = ""): # current dir by default
    # Reads a JSON file from the specified file path and returns its contents as a Python variable.
    # file_path: The path to the JSON file. 
    file_path = os.path.join(directory_path, file_name + ".json")
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    return json_data


def save_json(json_object: Dict[str, Any], file_name: str, directory_path: str = "series_containers") -> str:
    # Saves a JSON object to a specified directory with proper error handling.
    """ Args:
        json_object (Dict[str, Any]): The JSON data to save.
        file_name (str): The name of the JSON file (without extension).
        directory_path (str, optional): The folder where the file will be stored. Defaults to "series_containers".
    Returns:
        str: The full path to the saved file.
    """
    try:
        # Ensure the directory exists
        os.makedirs(directory_path, exist_ok=True)
        # Define the full path
        path = os.path.join(directory_path, file_name + ".json")
        # Write the JSON file
        with open(path, "w", encoding="utf-8") as f:
            json.dump(json_object, f, indent=4)
        return path  # Return the file path for reference
    except (OSError, IOError) as e:
        print(f"Error saving JSON to {path}: {e}")
        return ""

def validate_json_file(file_name, directory_path: str = "") -> bool:
    """
    Validates the JSON file for correct use of commas, parentheses, and brackets.
    Args: file_path (str): The path to the JSON file.
    Returns: bool: True if the JSON file is valid, False otherwise.
    """
    file_path = os.path.join(directory_path, file_name + ".json")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json.load(file)
        return True
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        return False

class TestReadJson(unittest.TestCase):
    def setUp(self):
        # Set up the path to the JSON file you want to test
        self.file_path = "path/to/your/test_data.json"
    def test_read_json(self):
        # Read the JSON file
        data = read_json(self.file_path)
        # Check if the data is a list
        self.assertIsInstance(data, list, "The JSON data should be a list")
        # Check if each item in the list is a dictionary
        for item in data:
            self.assertIsInstance(item, dict, "Each item in the JSON data should be a dictionary")
        # Check if each dictionary has the required keys
        required_keys = {"name", "year", "stamps"}
        for item in data:
            self.assertTrue(required_keys.issubset(item.keys()), "Each dictionary should contain the required keys")
        # Check if the "stamps" key contains a list of dictionaries with "height" and "width" keys
        for item in data:
            self.assertIsInstance(item["stamps"], list, "The 'stamps' key should contain a list")
            for stamp in item["stamps"]:
                self.assertIsInstance(stamp, dict, "Each stamp should be a dictionary")
                self.assertIn("height", stamp, "Each stamp should have a 'height' key")
                self.assertIn("width", stamp, "Each stamp should have a 'width' key")

if __name__ == "__main__":
    unittest.main()