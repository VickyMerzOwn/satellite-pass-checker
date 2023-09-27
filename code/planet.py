import os
from datetime import datetime, timedelta
import ephem
from mpl_toolkits.basemap import Basemap

# read tle

filename = "sample-data/tles/planet_mc.tle"

with open(filename, "r") as tle_file:
	tle_lines = tle_file.readlines()

tles = []
for i in range(0, len(tle_lines), 3):
	line1 = tle_lines[i].strip()[2:]
	line2 = tle_lines[i+1].strip()
	line3 = tle_lines[i+2].strip()
	tles.append((line1, line2, line3))

filename = "sample-data/gsts/planet.csv"

gst_coordinates = []
with open(filename, "r") as file:
	for line in file:
		coordinates = line.strip().split(',')
		if len(coordinates) == 4:
			latitude, longitude, elevation, label = coordinates[0], coordinates[1], float(coordinates[2]), coordinates[3]
			gst_coordinates.append([latitude,longitude, elevation, label])

date_format = "%Y-%m-%d %H:%M:%S"
start_datetime = datetime.strptime("2023-8-14 12:00:00", date_format)
end_datetime = datetime.strptime("2023-8-15 11:59:59", date_format)

current_datetime = start_datetime

times = []

#la1 = 0
#la2 = -25
lo1 = 9
lo2 = 39

def gst_in_range(time, sat):
	global gst_coordinates
	for j in range(len(gst_coordinates)):
		observer = ephem.Observer()
		observer.lat = str(gst_coordinates[j][0])
		observer.lon = str(gst_coordinates[j][1])
		observer.elevation = gst_coordinates[j][2]
		observer.date = time
		sat.compute(observer)
		los_distance_km = sat.range / 1000.0
		if los_distance_km < 1000:
			return True
	return False

def dms_to_decimal(dms):
    degrees, minutes, seconds = map(float, dms.split(':'))
    decimal_degrees = degrees + minutes / 60 + seconds / 3600
    return decimal_degrees

#lat_long_data = []
latitudes = []
longitudes = []
coordinates = []
int_times = []
for i in range(len(tles)):
#for i in range(3):
	previous_hotspot = None
	current_hotspot = None
	time = 0
	satellite = ephem.readtle(
		tles[i][0], tles[i][1], tles[i][2]
	)
	c1 = 0
	c2 = 0
	c3 = 0
	c4 = 0
	c5, c6, c7 = 0, 0, 0

	while current_datetime < end_datetime:
		print(i, current_datetime, end="\r")
		satellite.compute(current_datetime)
		#print(sat)
		lat, long = satellite.sublat, satellite.sublong
		lat = dms_to_decimal(lat.__str__())
		long = dms_to_decimal(long.__str__())
		coordinates.append((lat, long))
		latitudes.append(lat)
		longitudes.append(long)
		#lat_long_data.append((lat, long))
		#print(lat, long)
		#break
		#print(lat, long, end="\r")
		#y = la1 <= lat <= la2
		#if y:
		#	c1 += 1
		z = lo1 <= long <= lo2
		#if z:
		#	c2 += 1
		x = z
		#if x:
		#	c3 += 1
		if x and not previous_hotspot:
			c4 += 1
			time = 0
			previous_hotspot = True
		else:
			c5 += 1
			in_range = gst_in_range(current_datetime, satellite)
			if in_range and previous_hotspot:
				c6 += 1
				time += 1
				int_times.append(time)
				previous_hotspot = False
			elif (not in_range) and previous_hotspot:
				c7 += 1
				time += 1
		current_datetime += timedelta(seconds=1)
	#print(f"\n{c1}, {c2}, {c3}, {c4}, {c5}, {c6}, {c7}") 
	current_datetime = start_datetime
	times.append(int_times)
	print("\n", len(int_times))
	int_times = []

file_name = "output.txt"

# Open the file in write mode
with open(file_name, "w") as outfile:
    # Iterate through the list of lists
    for inner_list in times:
        # Convert the integers in the inner list to strings and join them with spaces
        line = " ".join(map(str, inner_list))
        # Write the line to the file
        outfile.write(line + "\n")
#file_path = "output.txt"
#
## Open the file in write mode ('w')
#with open(file_path, 'w') as outfile:
#    # Iterate through the list and write each element to a separate line
#    for item in coordinates:
#        outfile.write(str(item) + '\n')

#import folium
#map_new=folium.Map()
#for i in range(len(latitudes)):
##	print(i, end="\r")
#	map_new.add_child(folium.Marker(location=[latitudes[i],longitudes[i]], icon=folium.Icon(color='green')))
###for i in
#map_new.save("something.html")
