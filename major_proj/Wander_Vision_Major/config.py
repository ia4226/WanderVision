# config.py
#Google
GOOGLE_API_KEY = "AIzaSyCpBxrwDuqFE2Amrcaa4Dng9gfAyrNoVtQ"
GOOGLE_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
GOOGLE_MAPS_BASE_URL = "https://maps.googleapis.com/maps/api/directions/json"

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
