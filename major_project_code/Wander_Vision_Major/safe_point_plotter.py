# safe_point_plotter.py

def plot_safe_points_on_map(gmap, safe_points, marker_color="pink", is_safe=True):
    if safe_points:
        for point in safe_points:
            gmap.marker(point['latitude'], point['longitude'], marker_color)
            gmap.text(point['latitude'], point['longitude'], f"{point['name']} - Safe Point")
