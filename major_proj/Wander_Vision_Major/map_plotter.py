# map_plotter.py <- #dependecies:
import gmplot
import os
import webbrowser
from config import GOOGLE_API_KEY
from safe_point_plotter import plot_safe_points_on_map
from safe_point import load_safe_points

def plot_route_on_map(route_coordinates, start_coords, end_coords, selected_coords=None, marker_color="yellow"):

    safe_points = load_safe_points()

    gmap = gmplot.GoogleMapPlotter(start_coords[0], start_coords[1], 11, apikey=GOOGLE_API_KEY)

    if safe_points:
        plot_safe_points_on_map(gmap, safe_points, marker_color="lightblue", is_safe=True)

    latitudes = [coord["lat"] for coord in route_coordinates]
    longitudes = [coord["lon"] for coord in route_coordinates]
    #plot the route
    gmap.plot(latitudes, longitudes, "blue", edge_width=3)
    gmap.marker(start_coords[0], start_coords[1], "green")  #start
    gmap.marker(end_coords[0], end_coords[1], "red")  # end

    if selected_coords:
        for coord in selected_coords:
            if coord != start_coords and coord != end_coords:
                gmap.marker(coord[0], coord[1], marker_color)  # intermediate

    # save and open map
    output_file = "route_map_with_safe_points.html"
    gmap.draw(output_file)
    absolute_path = os.path.abspath(output_file)
    webbrowser.open(f"file://{absolute_path}", new=2)

def plot_special_markers_on_map(client, places, marker_color="gray", is_safe=False):

    safe_points = load_safe_points()

    if places:
        first_place = places[0]
        gmap = gmplot.GoogleMapPlotter(first_place['latitude'], first_place['longitude'], 15, apikey=GOOGLE_API_KEY)

        #plot safe points
        if safe_points:
            plot_safe_points_on_map(gmap, safe_points, marker_color="lightblue", is_safe=True)

        #plot hospitals
        for place in places:
            gmap.marker(place['latitude'], place['longitude'], marker_color)
            gmap.text(place['latitude'], place['longitude'],
                      f"{place['name']} - {'Safe Point' if is_safe else 'Hospital'}")

        #save and run map
        output_file = "special_markers_with_safe_points.html"
        gmap.draw(output_file)
        absolute_path = os.path.abspath(output_file)
        webbrowser.open(f"file://{absolute_path}", new=2)
    else:
        print("No places to plot.")
