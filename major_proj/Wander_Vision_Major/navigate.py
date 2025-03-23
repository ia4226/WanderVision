# navigate.py - Handles general and hospital navigation in WanderVision

# Dependencies
from weaviate_client import fetch_all_places
from directions import fetch_directions_from_google_maps
from map_plotter import plot_route_on_map
from utils import clean_direction_text

def convert_distance(distance_in_meters, unit="km"):
    """Convert distance from meters to km or miles."""
    if unit == "km":
        return distance_in_meters / 1000
    elif unit == "miles":
        return distance_in_meters * 0.000621371
    return distance_in_meters

def navigate_with_directions(client):
    """Navigate between stored places using Google Maps directions."""
    places = fetch_all_places(client)
    if len(places) < 2:
        print("Not enough places stored to calculate routes. Add more places first.")
        return

    print("\nAvailable places:")
    for idx, place in enumerate(places):
        print(f"{idx + 1}. {place['name']} (Lat: {place['latitude']}, Lon: {place['longitude']})")

    try:
        selected_places = []
        while True:
            place_idx = input("Select a place (enter number or 'done' to finish): ").strip()
            if place_idx.lower() == 'done':
                break
            selected_places.append(int(place_idx) - 1)

        if len(selected_places) < 2:
            print("You must select at least two places.")
            return

        coords = [(places[idx]["latitude"], places[idx]["longitude"]) for idx in selected_places]

        print("\nSelect travel mode:")
        print("1. Driving\n2. Walking\n3. Cycling\n4. Transit")
        mode_choice = input("Enter number for travel mode (1-4): ").strip()

        mode_mapping = {"1": "driving", "2": "walking", "3": "bicycling", "4": "transit"}
        mode = mode_mapping.get(mode_choice, "driving")

        all_route_coords = []
        all_directions = []
        total_distance = 0
        total_time = 0

        for i in range(len(coords) - 1):
            start_coords, end_coords = coords[i], coords[i + 1]
            directions_data = fetch_directions_from_google_maps(start_coords, end_coords, mode)

            total_distance += directions_data["distance"]
            total_time += directions_data["time_estimate"]

            all_route_coords.extend(directions_data["coordinates"])
            all_directions.extend(directions_data["directions"])

        plot_route_on_map(all_route_coords, coords[0], coords[-1], selected_coords=coords)

        print("\nRoute Directions:")
        for idx, step in enumerate(all_directions, start=1):
            print(f"{idx}. {clean_direction_text(step)}")

        print(f"\nTotal Distance: {convert_distance(total_distance, 'km')} km")
        print(f"Estimated Time: {total_time} minutes\nNavigation completed successfully!")

    except ValueError:
        print("Invalid input. Please enter valid numbers.")
    except Exception as e:
        print(f"Error during navigation: {e}")

def navigate_for_hospital(client, selected_hospital):
    print(f"Fetching directions to: {selected_hospital['name']}")

    user_locations = fetch_all_places(client)
    if not user_locations:
        print("No stored locations available. Please add a location first.")
        return

    # user selects a starting location
    print("\nSelect your starting location:")
    for idx, loc in enumerate(user_locations, start=1):
        print(f"{idx}. {loc['name']} ({loc['latitude']}, {loc['longitude']})")

    try:
        choice = int(input("Enter the number of your starting location: ")) - 1
        if choice < 0 or choice >= len(user_locations):
            print("Invalid choice. Defaulting to first location.")
            choice = 0
    except ValueError:
        print("Invalid input. Defaulting to first location.")
        choice = 0

    start_coords = (user_locations[choice]["latitude"], user_locations[choice]["longitude"])
    end_coords = (selected_hospital["latitude"], selected_hospital["longitude"])

    directions_data = fetch_directions_from_google_maps(start_coords, end_coords, "driving")

    if not directions_data:
        print("Error fetching directions.")
        return

    plot_route_on_map(directions_data["coordinates"], start_coords, end_coords)
    print(f"\nNavigating from {user_locations[choice]['name']} to {selected_hospital['name']} - {selected_hospital['address']}")
    for idx, step in enumerate(directions_data["directions"], start=1):
        print(f"{idx}. {clean_direction_text(step)}")
    print("\nNavigation completed successfully!")

