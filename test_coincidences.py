from coincidences_beta import Coincidences
import numpy as np

# Example data (timestamps for Alice and Bob)
Alice = np.array([1.0, 2.0, 3.0, 4.0, 5.0])  # Replace with your actual data
Bob = np.array([1.2, 2.2, 2.9, 4.1, 4.9])  # Replace with your actual data

def read_timestamps_from_file(file_name):
    with open(file_name, 'r') as file:
        timestamps = [float(line.strip()) for line in file]
    return np.array(timestamps)

# Specify the file paths for Alice and Bob's data
alice_file = "coincidences_analyse/alice.txt"
bob_file = "coincidences_analyse/bob.txt"

# Read timestamp data from files
Alice = read_timestamps_from_file(alice_file)
Bob = read_timestamps_from_file(bob_file)

# Example: Create an instance of the Coincidences class
coincidence_analyzer = Coincidences("config.yaml", Alice, Bob)

# Find the rough peak value
coincidence_analyzer.findPeak()
print("Rough peak value:", coincidence_analyzer.mxp)

# Calculate coincidences and rates
coincidence_analyzer.CoincidenceAndRates()
print("Total Coincidences:", coincidence_analyzer.totalCoincidences)
print("Total Accidentals:", coincidence_analyzer.totalAccidentals)
print("Total Singles (Alice):", coincidence_analyzer.totalSinglesAlice)
print("Total Singles (Bob):", coincidence_analyzer.totalSinglesBob)
print("Coincidences Per Second:", coincidence_analyzer.coincidencesPerSecond)
print("Accidentals Per Second:", coincidence_analyzer.accidentalsPerSecond)


import matplotlib.pyplot as plt

# Plot the histogram
histo, edges, mx = coincidence_analyzer.getHistogram(coincidence_analyzer.range, coincidence_analyzer.resolution / 1000)

#plt.bar(edges[:-1], histo, width=np.diff(edges), align='center')
plt.xlabel('Time Differences (ps)')
plt.ylabel('Counts')
plt.title('Histogram of Time Differences')
plt.plot(edges[1:],histo)
x_min = -10000  # Set your minimum x-axis value here
x_max = 10000  # Set your maximum x-axis value here
plt.xlim(x_min, x_max)
plt.show()

