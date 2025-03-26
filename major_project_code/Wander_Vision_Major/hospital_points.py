# hospital.py - Fetch and navigate to nearby hospitals in WanderVision

import requests
from map_plotter import plot_special_markers_on_map
from weaviate_client import fetch_all_places
from config import GOOGLE_API_KEY
from navigate import navigate_for_hospital

def fetch_nearby_hospitals(lat, lon, radius=5000):
    """Fetch nearby hospitals using Google Places API."""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": radius,
        "type": "hospital",
        "key": GOOGLE_API_KEY,
    }

    response = requests.get(url, params=params)
    results = response.json()

    if response.status_code != 200 or "results" not in results:
        print("Error fetching hospitals or no hospitals found.")
        return []

    return [
        {
            "name": place["name"],
            "latitude": place["geometry"]["location"]["lat"],
            "longitude": place["geometry"]["location"]["lng"],
            "address": place.get("vicinity", "Address not available"),
        }
        for place in results["results"]
    ]

def navigate_with_hospitals(client, hospitals_list):
    if not hospitals_list:
        print("No hospitals available to navigate.")
        return

    print("\nNearby Hospitals:")
    for idx, hospital in enumerate(hospitals_list, start=1):
        print(f"{idx}. {hospital['name']} - {hospital['address']}")

    try:
        hospital_idx = int(input("\nSelect a hospital to navigate to (enter number): ").strip())

        if 1 <= hospital_idx <= len(hospitals_list):
            navigate_for_hospital(client, hospitals_list[hospital_idx - 1])
        else:
            print("Invalid selection! Please try again.")

    except ValueError:
        print("Invalid input! Please enter a valid number.")

def display_nearby_hospitals(client):
    places = fetch_all_places(client)
    if not places:
        print("No places found.")
        return

    print("\nAvailable Places:")
    for idx, place in enumerate(places, start=1):
        print(f"{idx}. {place['name']} - (Lat: {place['latitude']}, Lon: {place['longitude']})")

    try:
        place_idx = int(input("\nEnter the number of the place to check nearby hospitals: ").strip())
        if 0 < place_idx <= len(places):
            selected_place = places[place_idx - 1]
            hospitals = fetch_nearby_hospitals(selected_place['latitude'], selected_place['longitude'])
            if hospitals:
                plot_special_markers_on_map(client, hospitals, marker_color="red")
                navigate_with_hospitals(client, hospitals)

    except ValueError:
        print("Invalid input! Please enter a number.")
