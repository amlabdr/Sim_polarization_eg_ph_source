import numpy as np
import yaml
import matplotlib.pyplot as plt

class Coincidences:
    def __init__(self, yamlfn):
        self.yamlfn = yamlfn
        self.load_configuration()

    def load_configuration(self):
        with open(self.yamlfn, 'r') as yfn:
            self.dicty = yaml.load(yfn, Loader=yaml.SafeLoader)

        self.trange = float(self.dicty["trange"])  # in ns
        self.binwidth = float(self.dicty["binwidth"])  # in ns
        self.offset = float(self.dicty["offset"])  # in ps
        self.resolution = float(self.dicty["resolution"])  # in ps
        self.range = float(self.dicty["range"])  # in ps

    def load_timestamps(self, alice_file, bob_file):
        self.Alice = self.read_timestamps_from_file(alice_file)
        self.Bob = self.read_timestamps_from_file(bob_file)

    def read_timestamps_from_file(self, file_name):
        with open(file_name, 'r') as file:
            timestamps = [float(line.strip()) for line in file]
        return np.array(timestamps)

    def create_histogram(self, data, range_ns, width_ns):
        bins = np.arange(-range_ns/2, range_ns/2 + width_ns/2, width_ns) * 1000
        histo, edges = np.histogram(data, bins)
        mx = bins[np.argmax(histo)]
        return histo, edges, mx

    def find_peak(self):
        self.load_configuration()
        self.H_rough, self.edge_rough, self.mxp = self.create_histogram(
            self.Alice - self.offset, self.trange, self.binwidth)
        self.offset = self.mxp

    def calculate_coincidences_and_rates(self):
        self.load_configuration()
        #self.load_timestamps(self.dicty["alice_file"], self.dicty["bob_file"])

        self.Alice = self.Alice - self.offset
        histo, edges, self.mx = self.create_histogram(self.Alice - self.Bob, self.range, self.resolution / 1000)

        self.mxtim = edges[np.argmax(histo)] / 1000

        # Calculate coincidence and accidental windows
        self.coin_edge_lo = self.mxtim - self.dicty["coin_window"]["radius"]
        self.coin_edge_hi = self.mxtim + self.dicty["coin_window"]["radius"]
        self.acc_edge_lo = self.coin_edge_lo + self.dicty["coin_window"]["accidental_offset"]
        self.acc_edge_hi = self.coin_edge_hi + self.dicty["coin_window"]["accidental_offset"]

        self.coin_idx1 = np.searchsorted(edges, self.coin_edge_lo * 1000)
        self.coin_idx2 = np.searchsorted(edges, self.coin_edge_hi * 1000)
        self.acc_idx1 = np.searchsorted(edges, self.acc_edge_lo * 1000)
        self.acc_idx2 = np.searchsorted(edges, self.acc_edge_hi * 1000)

        # Calculate total coincidences and accidentals
        self.totalCoincidences = np.sum(histo[self.coin_idx1:self.coin_idx2])
        self.totalAccidentals = np.sum(histo[self.acc_idx1:self.acc_idx2])

        # Calculate total singles
        self.totalSinglesAlice = len(self.Alice)
        self.totalSinglesBob = len(self.Bob)

        # Calculate collection times
        self.tA = (self.Alice[-1] - self.Alice[0]) / 1e12
        self.tB = (self.Bob[-1] - self.Bob[0]) / 1e12

        # Calculate rates per second
        self.coincidencesPerSecond = self.totalCoincidences / np.mean([self.tA, self.tB])
        self.accidentalsPerSecond = self.totalAccidentals / np.mean([self.tA, self.tB])

    def plot_histogram(self):
        histo, edges, mx = self.create_histogram(self.Alice - self.Bob, self.range, self.resolution / 1000)
        #plt.bar(edges[1:], histo, width=np.diff(edges), align='center')
        plt.xlabel('Time Differences (ps)')
        plt.ylabel('Counts')
        plt.title('Histogram of Time Differences')
        x_min = -4000  # Set your minimum x-axis value here
        x_max = 4000  # Set your maximum x-axis value here
        plt.xlim(x_min, x_max)
        plt.plot(edges[1:],histo)
        print(histo)
        print(edges)
        # Get and print the peak delay value
        peak_delay = mx
        print("Delay at the Peak of the Histogram:", peak_delay, "ps")
        #plt.plot([self.coin_windw_1, self.coin_windw_1],[0, max(self.H)*1.1])
        #plt.plot([self.coin_windw_2, self.coin_windw_2],[0, max(self.H)*1.1])
        plt.show()

        
        
        
    def print_values(self):
        print("Peak Value:", self.mxp)
        print("Total Coincidences:", self.totalCoincidences)
        print("Total Accidentals:", self.totalAccidentals)
        print("Total Singles (Alice):", self.totalSinglesAlice)
        print("Total Singles (Bob):", self.totalSinglesBob)
        print("Coincidences Per Second:", self.coincidencesPerSecond)
        print("Accidentals Per Second:", self.accidentalsPerSecond)
# Example usage:
config_file = "config.yaml"
alice_file = "coincidences_analyse/alice.txt"
bob_file = "coincidences_analyse/bob.txt"

coincidence_analyzer = Coincidences(config_file)
coincidence_analyzer.load_timestamps(alice_file, bob_file)
coincidence_analyzer.find_peak()
coincidence_analyzer.calculate_coincidences_and_rates()
coincidence_analyzer.print_values()
coincidence_analyzer.plot_histogram()
