import json
import csv

# Read the JSON file
with open('azure_gs.json') as file:
    data = json.load(file)

# Extract latitudes and longitudes
locations = []
for item in data:
    latitude = item['metadata']['latitude']
    longitude = item['metadata']['longitude']
    locations.append((latitude, longitude))

# Write the latitudes and longitudes to a CSV file
with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Latitude', 'Longitude'])  # Write header
    writer.writerows(locations)  # Write data rows
