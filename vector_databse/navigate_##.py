# Import dependencies
import weaviate
from weaviate.auth import AuthClientPassword
import requests
import re
import gmplot  # Import gmplot for map plotting
import os
import webbrowser
#define schemas
def create_class_schema(class_name, description, properties):
    return {
        "class": class_name,
        "description": description,
        "properties": properties,
    }

# Google API
GOOGLE_API_KEY = "AIzaSyCpBxrwDuqFE2Amrcaa4Dng9gfAyrNoVtQ"  # Replace with your Google Maps API Key
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

# Weaviate instance
def connect_to_weaviate():
    url = "https://qbkes3xfqvs8lqxdvpdzgw.c0.asia-southeast1.gcp.weaviate.cloud"  # Actual Weaviate URL
    auth = AuthClientPassword(username="iarhatia@gmail.com", password="Shrikrishna#12")
    return weaviate.Client(url=url, auth_client_secret=auth)

# Geocoding
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

# Fetch directions from Google Maps API with mode
def fetch_directions_from_google_maps(start_coords, end_coords, mode='driving'):
    params = {
        "origin": f"{start_coords[0]},{start_coords[1]}",
        "destination": f"{end_coords[0]},{end_coords[1]}",
        "mode": mode,  # Travel mode (driving, walking, bicycling, transit)
        "key": GOOGLE_API_KEY
    }

    response = requests.get(GOOGLE_MAPS_BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            route_data = data["routes"][0]["legs"][0]

            # Extract the route coordinates as a list of latitudes and longitudes
            route_coordinates = []
            for step in route_data["steps"]:
                route_coordinates.append({"lat": step["start_location"]["lat"], "lon": step["start_location"]["lng"]})

            return {
                "coordinates": route_coordinates,
                "distance": route_data["distance"]["value"],
                "time_estimate": route_data["duration"]["value"] // 60,  # Time in minutes
                "directions": [step["html_instructions"] for step in route_data["steps"]],
            }
        else:
            raise Exception(f"Google Maps API Error: {data['status']}")
    else:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")


# Function to plot the map using gmplot
def plot_route_on_map(route_coordinates, start_coords, end_coords):
    gmap = gmplot.GoogleMapPlotter(start_coords[0], start_coords[1], 11, apikey=GOOGLE_API_KEY)
    latitudes = [coord["lat"] for coord in route_coordinates]
    longitudes = [coord["lon"] for coord in route_coordinates]

    # Plot the route and markers on the map
    gmap.plot(latitudes, longitudes, "blue", edge_width=3)
    gmap.marker(start_coords[0], start_coords[1], "green")
    gmap.marker(end_coords[0], end_coords[1], "red")

    # Save the map as an HTML file
    output_file = "route_map.html"
    gmap.draw(output_file)

    # Open map in the browser
    absolute_path = os.path.abspath(output_file)
    webbrowser.open(f"file://{absolute_path}", new=2)

# stored places
def fetch_all_places(client):
    results = client.query.get("Place", ["name", "latitude", "longitude", "description", "_additional { id }"]).do()
    return results.get("data", {}).get("Get", {}).get("Place", [])

# Remove unnecessary words
def clean_direction_text(direction):
    clean_text = re.sub(r"<.*?>", "", direction)
    clean_text = re.sub(r"Pass by.*?(?=\(|$)", "", clean_text).strip()
    return clean_text

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

        # Ask the user for their preferred travel mode
        print("\nSelect travel mode:")
        print("1. Driving")
        print("2. Walking")
        print("3. Cycling")
        print("4. Transit")

        mode_choice = input("Enter number for travel mode (1-4): ").strip()

        mode_mapping = {
            "1": "driving",
            "2": "walking",
            "3": "bicycling",
            "4": "transit",
        }

        mode = mode_mapping.get(mode_choice, "driving")  # Default to driving if invalid input

        # Fetch directions based on selected travel mode
        directions_data = fetch_directions_from_google_maps(start_coords, end_coords, mode)

        # Plot the route on the map
        plot_route_on_map(directions_data["coordinates"], start_coords, end_coords)

        # Print route directions and estimated time
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