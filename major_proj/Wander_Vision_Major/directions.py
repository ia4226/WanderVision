# direction.py #dependencies
import requests
from config import GOOGLE_MAPS_BASE_URL, GOOGLE_API_KEY

def fetch_directions_from_google_maps(start_coords, end_coords, mode='driving'):
    params = {
        "origin": f"{start_coords[0]},{start_coords[1]}",
        "destination": f"{end_coords[0]},{end_coords[1]}",
        "mode": mode,  #preferred mode
        "key": GOOGLE_API_KEY
    }
    response = requests.get(GOOGLE_MAPS_BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            route_data = data["routes"][0]["legs"][0]

            route_coordinates = [] #extract route data
            for step in route_data["steps"]:
                route_coordinates.append({"lat": step["start_location"]["lat"], "lon": step["start_location"]["lng"]})

            return {
                "coordinates": route_coordinates,
                "distance": route_data["distance"]["value"],
                "time_estimate": route_data["duration"]["value"] // 60,  #time(minutes)
                "directions": [step["html_instructions"] for step in route_data["steps"]],
            }
        else:
            raise Exception(f"Google Maps API Error: {data['status']}")
    else:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")
