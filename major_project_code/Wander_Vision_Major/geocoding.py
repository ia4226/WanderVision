# geocoding.py #dependencies
import requests
from config import GOOGLE_API_KEY, GOOGLE_GEOCODING_URL

def get_geocode(address):
    params = {"address": address, "key": GOOGLE_API_KEY}
    response = requests.get(GOOGLE_GEOCODING_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK" and len(data["results"]) > 0:
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            raise Exception(f"Geocoding failed: {data['status']}. Error Message: {data.get('error_message', 'No message')}")
    else:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")

def add_place_with_geocoding(client, name, description, address, place_type):
    latitude, longitude = get_geocode(address)
    place_data = {
        "name": name,
        "description": description,
        "latitude": latitude,
        "longitude": longitude,
        "type": place_type,
    }
    client.data_object.create(place_data, "Place")
    print(f"Place {name} added successfully!")

def get_current_location():
    """Fetches the user's current location using IP-based geolocation."""
    try:
        response = requests.get("https://ipinfo.io/json")
        if response.status_code == 200:
            data = response.json()
            lat, lon = map(float, data["loc"].split(","))
            return {"lat": lat, "lng": lon}
        else:
            print(f"Failed to fetch location: {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching location: {e}")
        return None