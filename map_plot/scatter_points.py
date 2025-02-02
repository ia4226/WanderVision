from gmplot import gmplot
import os
import webbrowser

# Location data with names
locations = [
    ("Akshaya Metropolis", 12.77403693580903, 80.01159027653155),
    ("Arch Gate", 12.822940787489248, 80.041652932524),
    ("Clock Tower", 12.823087245153845, 80.04486085434772),
    ("University Building", 12.823390621473665, 80.04178167855038),
    ("TP Ganesan", 12.825158565856153, 80.04615904344696)
]

# Extract latitudes, longitudes, and names
names = [loc[0] for loc in locations]
latitudes = [loc[1] for loc in locations]
longitudes = [loc[2] for loc in locations]

# Create a map centered around the average latitude and longitude
center_latitude = sum(latitudes) / len(latitudes)
center_longitude = sum(longitudes) / len(longitudes)
gmap = gmplot.GoogleMapPlotter(center_latitude, center_longitude, 15)  # Zoom level 15 for closer view

# Add scatter points for the locations
gmap.scatter(latitudes, longitudes, color="blue", size=100, marker=False)

# Add markers and labels with info windows
for name, lat, lon in locations:
    gmap.marker(lat, lon, color="red", info_window=name)

# Save the map to an HTML file
output_file = "scatter_map_with_labels.html"
gmap.draw(output_file)

# Open the map in the default web browser
absolute_path = os.path.abspath(output_file)
webbrowser.open(f"file://{absolute_path}", new=2)
