#import dependencies
from gmplot import gmplot
import webbrowser
import os
#coordinates for map
latitude, longitude = 12.773512973531492, 80.01193671059774
gmap1 = gmplot.GoogleMapPlotter(latitude, longitude, 18)
#marking
gmap1.marker(latitude, longitude, "yellow")
#save file
output_file = "akshaya_map_marked.html"
gmap1.draw(output_file)
# open map
absolute_path = os.path.abspath(output_file)
webbrowser.open(f"file://{absolute_path}", new=2)
