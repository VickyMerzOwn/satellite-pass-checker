import os
import csv
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt


def get_time_differences_in_seconds(csv_file_path):
    time_differences_in_seconds = []
    time_between_contacts_in_seconds = []

    with open(csv_file_path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        satellite = None
        previous_finish = None
        for row in csvreader:
            start_time = datetime.strptime(row['Start'], '%Y-%m-%d %H:%M:%S')
            finish_time = datetime.strptime(row['Finish'], '%Y-%m-%d %H:%M:%S')
            
            time_difference = (finish_time - start_time).total_seconds()
            time_differences_in_seconds.append(time_difference)

            if row['Resource'] == satellite:
                current_start = datetime.strptime(row['Start'], '%Y-%m-%d %H:%M:%S')
                time_between_contacts_in_seconds.append((current_start - previous_finish).total_seconds())
                previous_finish = datetime.strptime(row['Finish'], '%Y-%m-%d %H:%M:%S')
            else:
                satellite = row['Resource']
                previous_finish = datetime.strptime(row['Finish'], '%Y-%m-%d %H:%M:%S')


    return time_differences_in_seconds, time_between_contacts_in_seconds

def calculate_cdf(measurements):
    sorted_measurements = np.sort(measurements)
    n = len(sorted_measurements)
    cdf = np.arange(1, n + 1) / n
    return sorted_measurements, cdf

def plot_cdf(sorted_measurements, cdf):
    

    # Plot CDF
    
    

    # Extrapolated lines for percentiles
    for percentile in percentiles:
        plt.axvline(x=percentile, color='r', linestyle='--')

    plt.savefig('cdf_plot.png', dpi=300, bbox_inches='tight')


# time_differences_in_seconds, time_between_contacts_in_seconds = get_time_differences_in_seconds(csv_file_path)
# print(len(time_differences_in_seconds), time_differences_in_seconds[:10])
# print(len(time_between_contacts_in_seconds), time_between_contacts_in_seconds[:10])


if __name__ == '__main__':
    for filename in os.listdir('results/data'):
    # for filename in ["planet_mc_planet.csv", "planet_mc_all_gst.csv"]:
        if filename.endswith('.csv'):
            string = filename
            csv_file_path = 'results/data/' + filename
            time_differences_in_seconds, time_between_contacts_in_seconds = get_time_differences_in_seconds(csv_file_path)
            contact_sorted, contact_cdf = calculate_cdf(time_differences_in_seconds)
            gaps_sorted, gap_cdf = calculate_cdf(time_between_contacts_in_seconds)

            percentiles = np.percentile(contact_sorted, [25, 50, 75])
            plt.plot(contact_sorted, contact_cdf, marker='o')
            plt.xlabel('Contacts Duration (s)')
            plt.ylabel('CDF')
            for percentile in percentiles:
                plt.axvline(x=percentile, color='r', linestyle='--')
            mean = np.mean(contact_sorted)
            median = percentiles[1]

            string += f" [{mean}|{median}](cdfs/{filename.split('/')[-1][:-4]})"

            plt.savefig('results/cdfs/' + filename.split('/')[-1][:-4] + '.png', dpi=300, bbox_inches='tight')
            plt.clf()

            percentiles = np.percentile(gaps_sorted, [25, 50, 75])
            plt.plot(gaps_sorted, gap_cdf, marker='o')
            plt.xlabel('Gaps Duration (s)')
            plt.ylabel('CDF')
            for percentile in percentiles:
                plt.axvline(x=percentile, color='r', linestyle='--')
            mean = np.mean(gaps_sorted)
            median = percentiles[1]

            string += f", [{mean}|{median}](cdfs/gaps_{filename.split('/')[-1][:-4]})"

            print(string)

            plt.savefig('results/cdfs/gaps_' + filename.split('/')[-1][:-4] + '.png', dpi=300, bbox_inches='tight')
            plt.clf()

