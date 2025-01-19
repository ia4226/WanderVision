# import dependencies
import weaviate  # vector database
from weaviate.auth import AuthClientPassword
import os


# function to create a schema class
def create_class_schema(class_name, description, properties):
    return {
        "class": class_name,
        "description": description,
        "properties": properties,
    }


# schemas for WanderVision
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
            {"name": "category", "dataType": ["text"],
             "description": "Category of the landmark (e.g., historic, natural)"},
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
    # connect to weaviate instance
    url = "https://belhthdprsuurfecdtjqa.c0.asia-southeast1.gcp.weaviate.cloud"
    auth = AuthClientPassword(
        username="<ADD_USERNAME>",
        password="<ADD_PASSWORD>",
    )
    return weaviate.Client(url=url, auth_client_secret=auth)


def initialize_schemas(client):
    # initialize schemas in the Weaviate instance
    for schema in schemas:
        try:
            client.schema.create_class(schema)
            print(f"Class {schema['class']} created successfully.")
        except Exception as e:
            print(f"Error creating class {schema['class']}: {e}")


def add_place(client, name, description, latitude, longitude, place_type):
    # add a new place to the Weaviate instance
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
    # fetch all places stored in Weaviate
    results = client.query.get("Place", ["name", "latitude", "longitude", "description"]).do()
    return results.get("data", {}).get("Get", {}).get("Place", [])


def add_landmark(client, name, coordinates, category):
    # add a new landmark to the Weaviate instance
    client.data_object.create(
        {
            "name": name,
            "coordinates": coordinates,
            "category": category,
        },
        "Landmark",
    )
    print(f"Landmark '{name}' added successfully.")


def fetch_all_landmarks(client):
    # fetch all landmarks stored in Weaviate
    results = client.query.get("Landmark", ["name", "coordinates", "category"]).do()
    return results.get("data", {}).get("Get", {}).get("Landmark", [])


def add_obstacle(client, location, description, obstacle_type, severity):
    # add a new obstacle to the Weaviate instance
    client.data_object.create(
        {
            "location": location,
            "description": description,
            "type": obstacle_type,
            "severity": severity,
        },
        "Obstacle",
    )
    print(f"Obstacle at '{location}' added successfully.")


def fetch_all_obstacles(client):
    # fetch all obstacles stored in Weaviate
    results = client.query.get("Obstacle", ["location", "description", "type", "severity"]).do()
    return results.get("data", {}).get("Get", {}).get("Obstacle", [])

def calculate_path(start_coords, end_coords):
    # basic calculation method for navigation
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
    # main interactive function to run WanderVision
    client = connect_to_weaviate()
    initialize_schemas(client)
    print("\n--- Welcome to WanderVision ---")

    while True:
        action = input(
            "Enter 'add' to add a place, 'list' to view places, "
            "'add_landmark' to add a landmark, 'list_landmarks' to view landmarks, "
            "'add_obstacle' to add an obstacle, 'list_obstacles' to view obstacles, "
            "'navigate' for directions, or 'exit' to quit: "
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
            if not places:
                print("No places found.")
            else:
                for place in places:
                    print(place)

        elif action == "add_landmark":
            name = input("Enter landmark name: ").strip()
            coordinates = input("Enter coordinates (e.g., '20.5937,78.9629'): ").strip()
            category = input("Enter category of the landmark (e.g., historic, natural): ").strip()
            add_landmark(client, name, coordinates, category)

        elif action == "list_landmarks":
            landmarks = fetch_all_landmarks(client)
            if not landmarks:
                print("No landmarks found.")
            else:
                for landmark in landmarks:
                    print(landmark)

        elif action == "add_obstacle":
            location = input("Enter location of the obstacle: ").strip()
            description = input("Enter description: ").strip()
            obstacle_type = input("Enter type of obstacle (e.g., roadblock, construction): ").strip()
            severity = input("Enter severity of the obstacle (e.g., low, high): ").strip()
            add_obstacle(client, location, description, obstacle_type, severity)

        elif action == "list_obstacles":
            obstacles = fetch_all_obstacles(client)
            if not obstacles:
                print("No obstacles found.")
            else:
                for obstacle in obstacles:
                    print(obstacle)

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

                start_coords = (places[start_idx]["latitude"], places[start_idx]["longitude"])
                end_coords = (places[end_idx]["latitude"], places[end_idx]["longitude"])
                directions = calculate_path(start_coords, end_coords)
                print(f"Directions: {directions}")
            except ValueError:
                print("Invalid selection. Please enter valid numbers.")

        elif action == "exit":
            print("Exiting WanderVision. Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
