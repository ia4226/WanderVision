#import dependencies
from gmplot import gmplot
import webbrowser
import os
#coordinates
latitude1, longitude1 = 12.773512973531492, 80.01193671059774 #akshaya metropolis
latitude2, longitude2 = 12.822940787489248, 80.041652932524 #arch gate
#map
center_latitude = (latitude1 + latitude2) / 2
center_longitude = (longitude1 + longitude2) / 2
gmap = gmplot.GoogleMapPlotter(center_latitude, center_longitude, 15)
#markers
gmap.marker(latitude1, longitude1, color='yellow')  # akshaya marker
gmap.marker(latitude2, longitude2, color='yellow')  # arch gate marker
#connecting line
gmap.plot([latitude1, latitude2], [longitude1, longitude2], color='red', edge_width=2.5)
#save map
output_file = "akshaya_archgate_map.html"
gmap.draw(output_file)
#open map in the browser
absolute_path = os.path.abspath(output_file)
webbrowser.open(f"file://{absolute_path}", new=2)
