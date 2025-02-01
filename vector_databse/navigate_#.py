# Import dependencies
import weaviate
from weaviate.auth import AuthClientPassword
import requests
import re
#define schemas
def create_class_schema(class_name, description, properties):

    return {
        "class": class_name,
        "description": description,
        "properties": properties,
    }

# google API
GOOGLE_API_KEY = "<Enter API key>"  # Replace with your Google Maps API Key
GOOGLE_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
GOOGLE_MAPS_BASE_URL = "https://maps.googleapis.com/maps/api/directions/json"

schemas = [
    create_class_schema(
        class_name="Place",
        description="Details about a specific place or location",
        properties=[
            {"name": "name", "dataType": ["text"], "description": "Name of the place"},
            {"name": "description", "dataType": ["text"], "description": "Description of the place"},
            {"name": "latitude", "dataType": ["number"], "description": "Latitude of the place"},
            {"name": "longitude", "dataType": ["number"], "description": "Longitude of the place"},
            {"name": "type", "dataType": ["text"], "description": "Type of place (e.g., park, hospital)"},
        ],
    ),
    create_class_schema(
        class_name="Route",
        description="Details about a route and directions between two places",
        properties=[
            {"name": "start_place", "dataType": ["Place"], "description": "Starting place of the route"},
            {"name": "end_place", "dataType": ["Place"], "description": "Ending place of the route"},
            {"name": "path_coordinates", "dataType": ["text[]"], "description": "List of coordinates in the route"},
            {"name": "distance", "dataType": ["number"], "description": "Distance of the route in meters"},
            {"name": "time_estimate", "dataType": ["number"], "description": "Estimated time in minutes"},
            {"name": "directions", "dataType": ["text[]"], "description": "Step-by-step directions"},
        ],
    ),
]
# weaviate instance
def connect_to_weaviate():

    url = "<ADD_URL>"  #  actual Weaviate URL
    auth = AuthClientPassword(
        username="<ADD_USERNAME>",
        password="<ADD_PASSWORD>",
    )
    return weaviate.Client(url=url, auth_client_secret=auth)

# Geocoding
def get_geocode(address):

    params = {
        "address": address,
        "key": GOOGLE_API_KEY
    }

    response = requests.get(GOOGLE_GEOCODING_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK" and len(data["results"]) > 0:
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            raise Exception(
                f"Geocoding failed: {data['status']}. Error Message: {data.get('error_message', 'No message')}")
    else:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")


def initialize_schemas(client, reset=False):

    if reset:
        for schema in schemas:
            try:
                client.schema.delete_class(schema["class"])
                print(f"Deleted existing class: {schema['class']}.")
            except Exception as e:
                print(f"Could not delete class {schema['class']}: {e}")

    for schema in schemas:
        try:
            client.schema.create_class(schema)
            print(f"Class {schema['class']} created successfully.")
        except Exception as e:
            print(f"Error creating class {schema['class']}: {e}")

#directions from Google Maps
def fetch_directions_from_google_maps(start_coords, end_coords):

    params = {
        "origin": f"{start_coords[0]},{start_coords[1]}",
        "destination": f"{end_coords[0]},{end_coords[1]}",
        "key": GOOGLE_API_KEY
    }

    response = requests.get(GOOGLE_MAPS_BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            route_data = data["routes"][0]["legs"][0]
            return {
                "coordinates": [
                    {"lat": step["start_location"]["lat"], "lon": step["start_location"]["lng"]}
                    for step in route_data["steps"]
                ],
                "distance": route_data["distance"]["value"],
                "time_estimate": route_data["duration"]["value"] // 60,
                "directions": [step["html_instructions"] for step in route_data["steps"]],
            }
        else:
            raise Exception(f"Google Maps API Error: {data['status']}")
    else:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")

# remove unnecessary words
def clean_direction_text(direction):

    clean_text = re.sub(r"<.*?>", "", direction)
    clean_text = re.sub(r"Pass by.*?(?=\(|$)", "", clean_text).strip()

    return clean_text

# add a place with geocoding
def add_place_with_geocoding(client, name, description, address, place_type):

    try:
        latitude, longitude = get_geocode(address)

        client.data_object.create(
            {
                "name": name,
                "description": description,
                "latitude": latitude,
                "longitude": longitude,
                "type": place_type,
            },
            "Place",
        )
        print(f"Place '{name}' added successfully with resolved coordinates: ({latitude}, {longitude}).")
    except Exception as e:
        print(f"Failed to add place '{name}': {e}")

# stored places
def fetch_all_places(client):

    results = client.query.get("Place", ["name", "latitude", "longitude", "description", "_additional { id }"]).do()
    return results.get("data", {}).get("Get", {}).get("Place", [])

# add route, display navigation
def navigate_with_directions(client):

    places = fetch_all_places(client)
    if len(places) < 2:
        print("Not enough places stored to calculate routes. Add more places first.")
        return

    print("\nAvailable places:")
    for idx, place in enumerate(places):
        print(f"{idx + 1}. {place['name']} (Lat: {place['latitude']}, Lon: {place['longitude']})")

    try:
        start_idx = int(input("Select the starting place (enter number): ")) - 1
        end_idx = int(input("Select the ending place (enter number): ")) - 1

        if start_idx == end_idx:
            print("Start and end must be different places.")
            return

        start_coords = (places[start_idx]["latitude"], places[start_idx]["longitude"])
        end_coords = (places[end_idx]["latitude"], places[end_idx]["longitude"])
        # fetch raw directions from Google Maps API
        directions_data = fetch_directions_from_google_maps(start_coords, end_coords)

        print("\nRoute Directions:")
        for idx, step in enumerate(directions_data["directions"], start=1):
            clean_text = clean_direction_text(step)
            print(f"{idx}. {clean_text}")

        print(f"\nTotal Distance: {directions_data['distance']} meters")
        print(f"Estimated Time: {directions_data['time_estimate']} minutes")
        print("\nNavigation completed successfully!")

    except ValueError:
        print("Invalid input. Please enter valid numbers.")
    except Exception as e:
        print(f"Error during navigation: {e}")


# main Function
def main():

    client = connect_to_weaviate()

    reset = input("Do you want to reset schemas? (yes/no): ").strip().lower() == "yes"
    initialize_schemas(client, reset=reset)

    print("\n--- Navigation System ---")

    while True:
        action = input(
            "\nEnter 'add' to add a place, 'list' to view places, 'navigate' to calculate route, or 'exit': ").strip().lower()

        if action == "add":
            name = input("Enter place name: ").strip()
            description = input("Enter description: ").strip()
            address = input("Enter address of the place: ").strip()
            place_type = input("Enter type of place (e.g., park, hospital): ").strip()
            add_place_with_geocoding(client, name, description, address, place_type)

        elif action == "list":
            places = fetch_all_places(client)
            if not places:
                print("No places found.")
            else:
                print("\nStored Places:")
                for place in places:
                    print(
                        f"{place['name']} (Lat: {place['latitude']}, Lon: {place['longitude']}) - {place['description']}")

        elif action == "navigate":
            navigate_with_directions(client)

        elif action == "exit":
            print("Exiting the system.")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
