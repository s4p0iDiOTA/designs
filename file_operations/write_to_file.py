import os
import json
from typing import Any, Dict

def save_json(json_object: Dict[str, Any], file_name: str, directory_path: str = "series_containers") -> str:
    """
    Saves a JSON object to a specified directory with proper error handling.

    Args:
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
