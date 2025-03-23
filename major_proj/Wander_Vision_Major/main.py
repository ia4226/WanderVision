#dependencies
from weaviate_client import connect_to_weaviate, initialize_schemas, list_places_in_table
from geocoding import add_place_with_geocoding
from navigate import navigate_with_directions, navigate_for_hospital
from hospital_points import display_nearby_hospitals, navigate_with_hospitals
from safe_point import add_safe_point, list_safe_points
from speech_to_speech import speech_command  # New STS module, yet to work perf

def query_weaviate(client, query):
    response = client.query.get("Place", ["name", "description"]).with_near_text({"concepts": [query]}).do()
    print("Weaviate Response:", response)  # Debugging line

    if response and response.get("data"):
        places = response["data"]["Get"]["Place"]
        if places:
            return f"The closest match I found is {places[0]['name']}. {places[0]['description']}"

    return "I couldn't find relevant information."

def main():
    client = connect_to_weaviate()
    reset = input("Do you want to reset schemas? (yes/no): ").strip().lower() == "yes"
    initialize_schemas(client, reset=reset)

    print("\n--- WanderVision Navigation System ---")
    while True:
        action = input(
            "\nEnter an option ('add', 'list', 'navigate', 'hospitals', 'safe_points','voice', or 'exit'): ").strip().lower()

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
            elif sub_action == "list":
                list_safe_points()
            else:
                print("Invalid option for safe points. Please try again.")

        elif action == "voice":
            print("Starting voice command mode...")
            speech_command(client, query_weaviate)

        elif action == "exit":
            print("Exiting WanderVision Navigation System. Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
