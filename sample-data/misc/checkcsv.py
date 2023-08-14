import csv

# Read the CSV file
with open('output.csv', 'r') as file:
    reader = csv.reader(file)
    rows = list(reader)

# Remove duplicate rows
unique_rows = list(set(tuple(row) for row in rows))

# Count the number of unique rows
num_unique_rows = len(unique_rows)

print("Number of unique rows:", num_unique_rows)
print(unique_rows)