#vector_database #dependencies

import os
from dotenv import load_dotenv
import weaviate
from weaviate.auth import AuthClientPassword

# Load environment variables
load_dotenv()

def connect_to_weaviate():  # Connect
    url = os.getenv("WEAVIATE_URL")
    username = os.getenv("WEAVIATE_USERNAME")
    password = os.getenv("WEAVIATE_PASSWORD")

    if not url or not username or not password:
        raise ValueError("Weaviate credentials are missing. Check your .env file.")

    auth = AuthClientPassword(username=username, password=password)
    return weaviate.Client(url=url, auth_client_secret=auth)


def initialize_schemas(client, reset=False):
    from config import schemas
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

def fetch_all_places(client):
    results = client.query.get("Place", ["name", "latitude", "longitude", "description", "_additional { id }"]).do()
    return results.get("data", {}).get("Get", {}).get("Place", [])

def list_places_in_table(client):
    places = fetch_all_places(client)

    if not places:
        print("No places found.")
        return

    unique_places = []
    seen = set()
    for place in places:
        place_key = (place['name'], place['latitude'], place['longitude'])
        if place_key not in seen:
            unique_places.append(place)
            seen.add(place_key)

    print("\nAvailable Places:")
    print(f"{'ID':<5} {'Name':<20} {'Lat':<15} {'Lon':<15} {'Description'}")
    print("-" * 60)

    for idx, place in enumerate(unique_places, start=1):
        print(f"{idx:<5} {place['name']:<20} {place['latitude']:<15} {place['longitude']:<15} {place['description']}")

    print("\nTotal Places:", len(unique_places))

def save_to_weaviate(client, place):
    safe_point_data = {
        "name": place["name"],
        "description": place["description"],
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "is_safe": True  #mark it as a safe point
    }
    client.data_object.create(safe_point_data, "Place")
    print(f"Safe point {place['name']} saved to the database.")

def fetch_safe_points_from_database(client):
    query = """
    {
      Get {
        Places(where: {
          path: ["is_safe"]
          operator: Equal
          valueBoolean: true
        }) {
          name
          description
          latitude
          longitude
        }
      }
    }
    """

    result = client.query.raw(query)
    safe_points = result["data"]["Get"]["Places"]
    return safe_points

