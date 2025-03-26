# safe_point.py <- #dependencies
import json
from geocoding import get_geocode

SAFE_POINTS_FILE = "safe_points.json"
def load_safe_points():

    try:
        with open(SAFE_POINTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_safe_points(safe_points):

    with open(SAFE_POINTS_FILE, 'w') as f:
        json.dump(safe_points, f, indent=4)

def add_safe_point(name, address):

    latitude, longitude = get_geocode(address)
    safe_points = load_safe_points() #load
    safe_points.append({ #append
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
    })
    save_safe_points(safe_points) #save points
    print(f"Safe point {name} added successfully!")

def list_safe_points():
    safe_points = load_safe_points()
    if not safe_points:
        print("No safe points available.")
    else:
        print("List of Safe Points:")
        for i, point in enumerate(safe_points, start=1):
            print(f"{i}. {point['name']} - {point['latitude']}, {point['longitude']}")
