import weaviate
from weaviate.auth import AuthClientPassword
import os

def calculate_path(start_x, start_y, end_x, end_y):
    if any(coord is None for coord in (start_x, start_y, end_x, end_y)):
        print("Error: Missing coordinates. Cannot calculate path.")
        return None

    dx = end_x - start_x
    dy = end_y - start_y
    directions = []
    # horizontal movement
    if dx > 0:
        directions.append(f"Move right {dx} units")
    elif dx < 0:
        directions.append(f"Move left {abs(dx)} units")
    # vertical movement
    if dy > 0:
        directions.append(f"Move up {dy} units")
    elif dy < 0:
        directions.append(f"Move down {abs(dy)} units")

    return " and ".join(directions) if directions else "You are already at your destination."

def fetch_place_coordinates(client, place_name):
    """Fetch coordinates for a specific place (case-insensitive)."""
    query = client.query.get("Location", ["x_coordinate", "y_coordinate"]).with_where({
        "path": ["location_name"],
        "operator": "Equal",
        "valueText": place_name.lower()  # case-insensitive lookup
    }).do()

    place = query.get("data", {}).get("Get", {}).get("Location", [])
    return (place[0].get("x_coordinate"), place[0].get("y_coordinate")) if place else (None, None)


def fetch_all_places(client):
    """Retrieve all stored places."""
    results = client.query.get("Location", ["location_name", "x_coordinate", "y_coordinate"]).do()
    return results.get("data", {}).get("Get", {}).get("Location", [])


def add_new_place(client):
    """Allow the user to add or update a place dynamically."""
    print("\n--- Add a New Place ---")

    # Input place details
    place_name = input("Enter the name of the new place: ").strip().lower()  # Store as lowercase
    description = input("Enter a short description: ").strip()

    # validate coordinates
    while True:
        try:
            x_coordinate = float(input("Enter the X coordinate: ").strip())
            y_coordinate = float(input("Enter the Y coordinate: ").strip())
            break
        except ValueError:
            print("Error: Coordinates must be numbers. Please try again.")

    # check if the place already exists
    query = client.query.get("Location", ["_additional {id}"]).with_where({
        "path": ["location_name"],
        "operator": "Equal",
        "valueText": place_name
    }).do()

    place = query.get("data", {}).get("Get", {}).get("Location", [])

    if place:
        object_id = place[0]["_additional"]["id"]
        update = input(f"'{place_name}' already exists. Do you want to update it? (yes/no): ").strip().lower()
        if update == "yes":
            client.data_object.update({
                "location_name": place_name,
                "description": description,
                "x_coordinate": x_coordinate,
                "y_coordinate": y_coordinate
            }, "Location", object_id)
            print(f"Updated existing place: {place_name}.")
        else:
            print(f"Skipped updating {place_name}.")
    else:
        # add new
        client.data_object.create({
            "location_name": place_name,
            "description": description,
            "x_coordinate": x_coordinate,
            "y_coordinate": y_coordinate
        }, "Location")
        print(f"Added new place: {place_name}.")


def validate_data(client):
    """Ensure initial data is in the schema."""
    data_objects = [
        {"location_name": "park", "description": "A green public space", "x_coordinate": 5, "y_coordinate": 10},
        {"location_name": "library", "description": "A place full of books", "x_coordinate": -10, "y_coordinate": 15},
        {"location_name": "cafe", "description": "A cozy coffee shop", "x_coordinate": 10, "y_coordinate": -5},
    ]
    for obj in data_objects:
        query = client.query.get("Location", ["_additional {id}"]).with_where({
            "path": ["location_name"],
            "operator": "Equal",
            "valueText": obj["location_name"]
        }).do()
        if not query.get("data", {}).get("Get", {}).get("Location", []):  # Place not found
            client.data_object.create(obj, "Location")
            print(f"Added default place: {obj['location_name']}")


def main():
    # auth details
    url = "https://h0jpd58tdaxyxmkbkd6vg.c0.asia-southeast1.gcp.weaviate.cloud"
    auth = AuthClientPassword(
        username="<YOUR_USERNAME>",
        password="<YOUR_PASSWORD>"
    )

    try:
        print("Connecting to Weaviate instance...")
        client = weaviate.Client(url=url, auth_client_secret=auth)
        print("Connected!")

        schema_definition = {
            "class": "Location",
            "properties": [
                {"name": "location_name", "dataType": ["text"]},
                {"name": "description", "dataType": ["text"]},
                {"name": "x_coordinate", "dataType": ["number"]},
                {"name": "y_coordinate", "dataType": ["number"]}
            ]
        }

        current_schema = client.schema.get()
        if "Location" not in [cls["class"] for cls in current_schema.get("classes", [])]:
            print("Creating schema for 'Location'.")
            client.schema.create_class(schema_definition)
            print("'Location' schema created successfully.")
            validate_data(client)  #default
        else:
            print("'Location' schema already exists.")
            validate_data(client)

        while True:
            add_place_choice = input("Do you want to add a new place? (yes/no): ").strip().lower()
            if add_place_choice == "yes":
                add_new_place(client)
            elif add_place_choice == "no":
                print("Proceeding to the navigation system...")
                break
            else:
                print("Please enter 'yes' or 'no'.")

        all_places = fetch_all_places(client)
        available_places = [place for place in all_places if
                            None not in [place.get("x_coordinate"), place.get("y_coordinate")]]

        print("\n--- Navigation System ---")
        if not available_places:
            print("No available places found in the system!")
            add_place_choice = input("Do you want to add a new place? (yes/no): ").strip().lower()
            if add_place_choice == "yes":
                add_new_place(client)
                available_places = fetch_all_places(client)  # Refresh places
                if not available_places:
                    print("Still no places found. Exiting!")
                    return
            else:
                print("Exiting as there are no places.")
                return

        print("Available places:\n- " + "\n- ".join([place["location_name"] for place in available_places]))

        while True:
            start = input("Enter your current location (or type 'exit' to quit): ").strip().lower()
            if start.lower() == "exit":
                print("Exiting the program. Goodbye.")
                break

            destination = input("Enter your desired destination: ").strip().lower()

            # Retrieve coordinates
            start_coords = fetch_place_coordinates(client, start)
            dest_coords = fetch_place_coordinates(client, destination)

            # Validate locations
            if start_coords == (None, None):
                print(f"Error: '{start}' not found in the database.")
            elif dest_coords == (None, None):
                print(f"Error: '{destination}' not found in the database.")
            else:
                # Calculate the path
                directions = calculate_path(*start_coords, *dest_coords)
                print(f"\nDirections from '{start}' to '{destination}': {directions}")

    except Exception as e:
        print("An error occurred:", str(e))


if __name__ == "__main__":
    main()
