"""JSON persistence helpers for the gradebook.

The app stores all data in a single JSON file (`data/gradebook.json`) to keep
the project small, inspectable, and easy to reset.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

DEFAULT_PATH = "data/gradebook.json"


def load_data(path: str = DEFAULT_PATH) -> dict:
    """Load gradebook data from a JSON file.

    Args:
        path: Location of the JSON file.

    Returns:
        A dictionary with the keys ``students``, ``courses``, and
        ``enrollments``. If the file doesn't exist, an empty structure is
        returned.

    Notes:
        If the JSON is corrupted, the function prints a warning to stdout and
        returns an empty structure so the CLI can continue running.
    """
    empty = {"students": [], "courses": [], "enrollments": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info("Data loaded successfully from %s", path)
            return data
    except FileNotFoundError:
        logger.info("No data file found at %s. Starting fresh.", path)
        return empty
    except json.JSONDecodeError as e:
        logger.error("Could not parse JSON from %s: %s", path, e)
        print(f"  Warning: '{path}' is corrupted and could not be read. Starting fresh.")
        return empty


def save_data(data: dict, path: str = DEFAULT_PATH) -> None:
    """Save gradebook data to a JSON file.

    Args:
        data: The in-memory gradebook data structure.
        path: Output JSON file path.

    Notes:
        If a filesystem error occurs, the function logs it and prints a
        message to the terminal instead of raising the exception.

    Returns:
        None
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            logger.info("Data saved successfully to %s", path)
    except OSError as e:
        logger.error("Failed to save data to %s: %s", path, e)
        print(f"  Error: Could not save data — {e}")