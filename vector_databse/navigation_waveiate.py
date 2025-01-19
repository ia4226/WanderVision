#import dependencies
import weaviate #vector database
from weaviate.auth import AuthClientPassword
import os
#function to create a schema class
def create_class_schema(class_name, description, properties):
    return {
        "class": class_name,
        "description": description,
        "properties": properties,
    }
#schemas for WanderVision
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
            {"name": "image_vector", "dataType": ["blob"], "description": "Vectorized image representation"},
        ],
    ),
    create_class_schema(
        class_name="Route",
        description="Details about a route between two places",
        properties=[
            {"name": "start_place", "dataType": ["Place"], "description": "Starting place of the route"},
            {"name": "end_place", "dataType": ["Place"], "description": "Ending place of the route"},
            {"name": "path_coordinates", "dataType": ["text[]"], "description": "List of coordinates in the route"},
            {"name": "distance", "dataType": ["number"], "description": "Distance of the route in meters"},
            {"name": "time_estimate", "dataType": ["number"], "description": "Estimated time in minutes"},
        ],
    ),
    create_class_schema(
        class_name="Landmark",
        description="Details about a significant landmark",
        properties=[
            {"name": "name", "dataType": ["text"], "description": "Name of the landmark"},
            {"name": "coordinates", "dataType": ["text"], "description": "Coordinates of the landmark"},
            {"name": "image_vector", "dataType": ["blob"], "description": "Vectorized image representation"},
            {"name": "category", "dataType": ["text"], "description": "Category of the landmark (e.g., historic, natural)"},
        ],
    ),
    create_class_schema(
        class_name="Obstacle",
        description="Details about obstacles on a route",
        properties=[
            {"name": "location", "dataType": ["text"], "description": "Location of the obstacle"},
            {"name": "description", "dataType": ["text"], "description": "Description of the obstacle"},
            {"name": "type", "dataType": ["text"], "description": "Type of obstacle (e.g., roadblock, construction)"},
            {"name": "severity", "dataType": ["text"], "description": "Severity of the obstacle (e.g., low, high)"},
        ],
    ),
]
def connect_to_weaviate():
    #connect to weaviate instance
    url = "https://belhthdprsuurfecdtjqa.c0.asia-southeast1.gcp.weaviate.cloud"
    auth = AuthClientPassword(
        username="<ADD_USERNAME>",
        password="<ADD_PASSWORD>",
    )
    return weaviate.Client(url=url, auth_client_secret=auth)

def initialize_schemas(client):
   #initialize schemas in the Weaviate instance.
    for schema in schemas:
        try:
            client.schema.create_class(schema)
            print(f"Class {schema['class']} created successfully.")
        except Exception as e:
            print(f"Error creating class {schema['class']}: {e}")

def add_place(client, name, description, latitude, longitude, place_type):
    #add a new place to the Weaviate instance.
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
    print(f"Place '{name}' added successfully.")

def fetch_all_places(client):
    #stored places
    results = client.query.get("Place", ["name", "latitude", "longitude", "description"]).do()
    return results.get("data", {}).get("Get", {}).get("Place", [])

def calculate_path(start_coords, end_coords):
    #basic calculation method (should try A* or Djikstra)
    dx = end_coords[0] - start_coords[0]
    dy = end_coords[1] - start_coords[1]
    directions = []
    if dx > 0:
        directions.append(f"Move right {dx} units")
    elif dx < 0:
        directions.append(f"Move left {abs(dx)} units")
    if dy > 0:
        directions.append(f"Move up {dy} units")
    elif dy < 0:
        directions.append(f"Move down {abs(dy)} units")
    return " and ".join(directions) if directions else "You are already at your destination."

def main():
    client = connect_to_weaviate()
    initialize_schemas(client)
    print("\n--- Welcome to WanderVision ---")

    #add places
    while True:
        action = input(
            "Enter 'add' to add a place, 'list' to view places, 'navigate' for directions, or 'exit' to quit: "
        ).strip().lower()

        if action == "add":
            name = input("Enter place name: ").strip()
            description = input("Enter description: ").strip()
            latitude = float(input("Enter latitude: "))
            longitude = float(input("Enter longitude: "))
            place_type = input("Enter type of place (e.g., park, hospital): ").strip()
            add_place(client, name, description, latitude, longitude, place_type)

        elif action == "list":
            places = fetch_all_places(client)
            for place in places:
                print(place)

        elif action == "navigate":
            places = fetch_all_places(client)
            if len(places) < 2:
                print("Not enough places stored to calculate a route. Add more places first.")
                continue

            print("Available places:")
            for idx, place in enumerate(places):
                print(f"{idx + 1}. {place['name']} (lat: {place['latitude']}, lon: {place['longitude']})")

            try:
                start_idx = int(input("Select the starting place (enter number): ")) - 1
                end_idx = int(input("Select the ending place (enter number): ")) - 1

                if start_idx < 0 or start_idx >= len(places) or end_idx < 0 or end_idx >= len(places):
                    print("Invalid selection. Try again.")
                    continue

                start_coords = (places[start_idx]['latitude'], places[start_idx]['longitude'])
                end_coords = (places[end_idx]['latitude'], places[end_idx]['longitude'])
                #calculate directions
                directions = calculate_path(start_coords, end_coords)
                print(f"Directions: {directions}")

            except ValueError:
                print("Invalid input. Please enter valid numbers.")

        elif action == "exit":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
