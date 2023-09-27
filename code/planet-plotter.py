import numpy as np
import matplotlib.pyplot as plt

# Specify the file name
file_name = "results/fires/output.txt"

# Initialize an empty list to store the integers
integers_list = []

# Open the file in read mode
with open(file_name, "r") as file:
    # Iterate through each line in the file
    for line in file:
        # Split the line into a list of strings using spaces as the separator
        tokens = line.strip().split()
        
        # Convert each token to an integer and append it to the list
        for token in tokens:
            num = int(token)
            if num != 1:
                integers_list.append(num)

# Now, integers_list contains all the integers from the file
print(len(integers_list))


def calculate_cdf(measurements):
    sorted_measurements = np.sort(measurements)
    n = len(sorted_measurements)
    cdf = np.arange(1, n + 1) / n
    return sorted_measurements, cdf

sorted_list, cdf = calculate_cdf(integers_list)
percentiles = np.percentile(sorted_list, [25, 50, 75])
plt.plot(sorted_list, cdf, marker='o')
plt.xlabel('Time sensitive contacts (s)')
plt.ylabel('CDF')
for percentile in percentiles:
    plt.axvline(x=percentile, color='r', linestyle='--')

mean = np.mean(sorted_list)
median = percentiles[1]
plt.savefig('results/fires/fire.png', dpi=300, bbox_inches='tight')
plt.clf()
