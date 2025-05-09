import json
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("player_universe_trx.utils")


def load_json_data(file_path: str) -> List[Dict]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of dictionaries from the JSON file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file isn't valid JSON
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        logger.info(f"Successfully loaded {len(data)} records from {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        raise


def save_json_data(data: List[Dict], file_path: str, indent: int = 2) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path where to save the JSON file
        indent: Indentation level for JSON formatting (default: 2)
        
    Raises:
        IOError: If there's an error writing to the file
    """
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=indent)
        logger.info(f"Successfully saved data to {file_path}")
    except IOError:
        logger.error(f"Error writing to file: {file_path}")
        raise