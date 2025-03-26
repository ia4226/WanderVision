# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_GEOCODING_URL = os.getenv("GOOGLE_GEOCODING_URL")
GOOGLE_MAPS_BASE_URL = os.getenv("GOOGLE_MAPS_BASE_URL")

# schemas
schemas = [
    {
        "class": "Place",
        "properties": [
            {"name": "name", "dataType": ["text"]},
            {"name": "latitude", "dataType": ["number"]},
            {"name": "longitude", "dataType": ["number"]},
            {"name": "description", "dataType": ["text"]},
            {"name": "type", "dataType": ["text"]},
        ]
    }
]
