# Dependencies
from weaviate_client import connect_to_weaviate, initialize_schemas, list_places_in_table
from geocoding import add_place_with_geocoding
from navigate import navigate_with_directions
from hospital_points import display_nearby_hospitals
from safe_point import add_safe_point, list_safe_points
from speech_to_speech import speech_command  # Speech-to-speech module handles voice interaction


def query_weaviate(client, intent, params):
    """Handles queries based on recognized intent."""
    try:
        if intent == "locate":
            place_name = params.get("place")
            response = client.query.get("Place", ["name", "_additional {latitude longitude}"]).with_where({
                "path": ["name"],
                "operator": "Equal",
                "valueString": place_name
            }).do()

            if response and response.get("data"):
                places = response["data"]["Get"]["Place"]
                if places:
                    latitude = places[0]["_additional"]["latitude"]
                    longitude = places[0]["_additional"]["longitude"]
                    return f"The coordinates of {place_name} are Latitude: {latitude}, Longitude: {longitude}."

            return f"I couldn't find coordinates for {place_name}."

        elif intent == "navigate":
            place_name = params.get("place")
            # Call navigation function (e.g., navigate_with_directions)
            navigate_with_directions(client)
            return f"Navigating to {place_name}. Directions provided."

        elif intent == "hospital_search":
            # Call hospital search function (e.g., display_nearby_hospitals)
            display_nearby_hospitals(client)
            return f"Nearby hospitals have been displayed."

        elif intent == "add_safe_point":
            name = input("Enter safe point name: ").strip()
            address = input("Enter safe point address: ").strip()
            add_safe_point(name, address)
            return f"Safe point '{name}' added successfully."

        elif intent == "list_safe_points":
            list_safe_points()
            return f"Safe points have been listed."

        else:  # Default fallback for unrecognized queries
            response = client.query.get("Place", ["name", "description"]).with_near_text(
                {"concepts": [params["query"]]}).do()
            if response and response.get("data"):
                places = response["data"]["Get"]["Place"]
                if places:
                    return f"The closest match I found is {places[0]['name']}. {places[0]['description']}"

            return f"I couldn't find relevant information for '{params['query']}'."
    except Exception as e:
        print(f"Error querying Weaviate: {e}")
        return f"An error occurred while accessing the database."


def main():
    client = connect_to_weaviate()
    if not client.is_ready():
        print("Failed to connect to Weaviate. Please check your configuration.")
        return

    reset = input("Do you want to reset schemas? (yes/no): ").strip().lower() == "yes"
    if reset:
        initialize_schemas(client, reset=reset)

    print("\n--- WanderVision Navigation System ---")

    while True:
        action = input(
            "\nEnter an option ('add', 'list', 'navigate', 'hospitals', 'safe_points', 'voice', or 'exit'): ").strip().lower()

        if action == "add":
            name = input("Enter place name: ").strip()
            description = input("Enter description: ").strip()
            address = input("Enter address of the place: ").strip()
            place_type = input("Enter type of place (e.g., park, hospital): ").strip()
            add_place_with_geocoding(client, name, description, address, place_type)

        elif action == "list":
            list_places_in_table(client)

        elif action == "navigate":
            navigate_with_directions(client)

        elif action == "hospitals":
            display_nearby_hospitals(client)

        elif action == "safe_points":
            sub_action = input("\nEnter 'add' to add a safe point or 'list' to view safe points: ").strip().lower()
            if sub_action == "add":
                name = input("Enter safe point name: ").strip()
                address = input("Enter safe point address: ").strip()
                add_safe_point(name, address)
                print(f"Safe point '{name}' added successfully.")
            elif sub_action == "list":
                list_safe_points()
                print(f"Safe points have been listed.")
            else:
                print("Invalid option for safe points. Please try again.")

        elif action == "voice":
            print("Starting voice command mode...")
            speech_command(client)

        elif action == "exit":
            print("Exiting WanderVision Navigation System. Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
