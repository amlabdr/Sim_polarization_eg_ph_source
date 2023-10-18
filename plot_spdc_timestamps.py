import matplotlib.pyplot as plt
from collections import Counter

def plot_repetitions_from_file(file_name,total_attempts=None):
    # Read timestamps from the file
    with open(file_name, 'r') as file:
        timestamps = [line.strip() for line in file]

    # Count the occurrences of each timestamp
    timestamp_counts = Counter(timestamps)

    # Count the repetitions per occurrence
    repetitions_count = Counter(timestamp_counts.values())
    # Extract repetition values and corresponding counts
    unique_repetitions, counts = zip(*repetitions_count.items())

    # Calculate the total count of repetitions
    total_count = sum(counts)
    if total_count:
        repetitions_count[0]=total_attempts - total_count
    print(repetitions_count)

    # Extract repetition values and corresponding counts
    unique_repetitions, counts = zip(*repetitions_count.items())

    # Calculate the total count of repetitions
    total_count = sum(counts)

    # Calculate percentages
    percentages = [count / total_count for count in counts]

    # Create a bar plot
    plt.bar(unique_repetitions, percentages, align='center')
    plt.xlabel('Emitted Photon Number')
    plt.ylabel('Percentage of occurence')
    plt.title('Emitted Photon number distribution')

    # Set x-axis ticks to show only unique repetition values
    plt.xticks(unique_repetitions)

    # Set y-axis limits to represent percentages from 0 to 100%
    plt.ylim(0, 1)

    # Set y-axis ticks as percentages
    plt.yticks([0.0, 0.25, 0.5, 0.75, 1.0], ['0%', '25%', '50%', '75%', '100%'])


    for i in range(len(unique_repetitions)):
        plt.text(unique_repetitions[i], percentages[i], f'{percentages[i]*100:.2f}%', ha='center', va='bottom')

    plt.show()


# Example usage
file_name = "data/spdc_timestamps.txt"  
plot_repetitions_from_file(file_name,10000)
