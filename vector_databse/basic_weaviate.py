import weaviate
from weaviate.auth import AuthClientPassword

#define URL and authentication details
url = "https://h0jpd58tdaxyxmkbkd6vg.c0.asia-southeast1.gcp.weaviate.cloud"
auth = AuthClientPassword(
    username="<YOUR_USERNAME>",
    password="<YOUR_PASSWORD>"
)

try:
    #connect to Weaviate
    print("Connecting to Weaviate instance with username/password authentication...")
    client = weaviate.Client(url=url, auth_client_secret=auth)
    print("Connection established!")

    #Remove Duplicates
    print("Checking and removing duplicates...")
    existing_objects = client.query.get("Place", ["places", "_additional {id}"]).do()

    #track unique "places" and IDs
    unique_places = {}
    for obj in existing_objects["data"]["Get"]["Place"]:
        place_name = obj["places"]
        object_id = obj["_additional"]["id"]

        if place_name in unique_places:
            #delete duplicates
            client.data_object.delete(object_id, "Place")  # Correct delete method
            print(f"Deleted duplicate object for place '{place_name}' with ID '{object_id}'.")
        else:

            unique_places[place_name] = object_id

    print("Duplicate cleanup complete.")

    #upload data
    print("Uploading data objects...")
    data_objects = [
        {"places": "Park", "description": "A green area with trees", "direction": "Turn left"},
        {"places": "Library", "description": "A place to borrow books", "direction": "Turn right"},
        {"places": "Cafe", "description": "A place to have coffee", "direction": "Go straight"},
        {"places": "Grocery Store", "description": "A place to buy groceries", "direction": "Turn back"}
    ]

    for obj in data_objects:
        existing_objects = client.query.get("Place", ["places"]).with_where({
            "path": ["places"],
            "operator": "Equal",
            "valueText": obj["places"]
        }).do()

        if (
                existing_objects.get("data")
                and existing_objects["data"].get("Get")
                and existing_objects["data"]["Get"].get("Place")
        ):
            print(f"Object with 'places' = '{obj['places']}' already exists. Skipping upload...")
        else:
            client.data_object.create(data_object=obj, class_name="Place")
            print(f"Object with 'places' = '{obj['places']}' has been uploaded.")

    print("Data objects upload process complete.")

    #display results
    while True:
        print("\nEnter the value to query from 'places'. Examples: Park, Library, Cafe, Grocery Store")
        user_query = input("Query for 'places' (or type 'exit' to quit): ").strip()

        if user_query.lower() == "exit":
            print("Exiting the program. Goodbye!")
            break

        print(f"Querying for places matching '{user_query}'...")
        result = client.query.get("Place", ["places", "description", "direction"]).with_where({
            "path": ["places"],
            "operator": "Equal",
            "valueText": user_query
        }).do()

        if (
                result.get("data")
                and result["data"].get("Get")
                and result["data"]["Get"].get("Place")
        ):
            print("\nQuery Result: ")
            for place in result["data"]["Get"]["Place"]:
                print(f"Place: {place['places']}, Description: {place['description']}, Direction: {place['direction']}")
        else:
            print(f"No matching results found for the place '{user_query}'.")

except Exception as e:
    print("An error occurred:", str(e))
finally:
    # cleaning resources
    if 'client' in locals():
        del client
