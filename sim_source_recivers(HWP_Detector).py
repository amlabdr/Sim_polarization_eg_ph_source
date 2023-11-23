from numpy import random
from components.light_source import SPDCSource
from sequence.components.photon import Photon
from sequence.kernel.timeline import Timeline
from sequence.utils.encoding import polarization
from sequence.topology.node import Node
from sequence.kernel.entity import Entity
from sequence.components.optical_channel import QuantumChannel
from coincidencesSim import Coincidences
from sequence.components.detector import QSDetectorPolarization
from components.half_wave_plate import HalfWavePlate
from math import sqrt
import matplotlib.pyplot as plt
import numpy as np
"""# Configure the logging
import logging
log_filename = 'sim_log.log'
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger
logger = logging.getLogger(__name__)"""
random.seed(0)
class Counter:
    def __init__(self):
        self.count = 0
        self.log = []

    def trigger(self, detector, info):
        self.count += 1
        self.log.append(detector.timeline.now())
    
    def get_rates(self):
        if len(self.log) > 0:
            rate = 1e12*self.count/(self.log[-1] - self.log[0])
        else:
            rate = 0
        return rate

class source_port(Entity):
    def __init__(self, name, timeline:Timeline,owner:Node):
        super().__init__(name, timeline)
        self.owner = owner
        self.add_receiver(owner)
    def init(self):
        # Implement the init method as required by the Entity class
        pass
    def get(self, photon, **kwargs):
        photon.name = self.name
        self._receivers[0].get(photon)

class source_node(Node):
    def __init__(self, name: str, timeline: Timeline,eg_photons_number:int):
        super().__init__(name, timeline)
        FREQ, MEAN = 1e7, 0.1
        self.spdc = SPDCSource("spdc", self.timeline, frequency=FREQ, mean_photon_num=MEAN, encoding_type=polarization)
        self.ports = {}
        for i in range (eg_photons_number):
            self.ports[i] = source_port(str(i), self.timeline, self)
            self.spdc.add_receiver(self.ports[i])
        self.first_component_name = self.spdc.name
    def get(self, photon, **kwargs):
        #print(photon.quantum_state.state)
        index = 0
        for dst in self.qchannels:
            if int(photon.name) == index:
                self.send_qubit(dst, photon)
                break
            index +=1
#class for simple Reciver 
class Receiver(Node):
    def __init__(self, name: str, timeline: Timeline):
        super().__init__(name, timeline)
        self.log = []
        hwp_name = name +".hwp"
        self.hwp = HalfWavePlate(name= hwp_name,timeline= self.timeline,angle=0)
        self.add_component(self.hwp)
        self.hwp.owner = self
        self.set_first_component(hwp_name)
        QSDetectorPolarization_name = name + ".QSDetectorPolarization"
        self.QSDetectorPolarization = QSDetectorPolarization(name = QSDetectorPolarization_name,timeline=self.timeline)
        self.QSDetectorPolarization.update_detector_params(0, "efficiency", 1)
        self.QSDetectorPolarization.update_detector_params(1, "efficiency", 1)
        self.hwp.add_receiver(self.QSDetectorPolarization)
        self.counter0 = Counter()
        self.counter1 = Counter()
        self.QSDetectorPolarization.detectors[0].attach(self.counter0)
        self.QSDetectorPolarization.detectors[1].attach(self.counter1)
    def get_rates(self):
        if self.photon_counter > 0:
            rate = 1e12*self.photon_counter/(self.log[-1][0] - self.log[0][0])
        else:
            rate = 0
        return rate


def save_logs(log_list,file_name):
    # Extract timestamps from the log list
    timestamps = [str(timestamp) for timestamp in log_list]

    # Write the timestamps to the file
    with open(file_name, 'w') as file:
        file.write('\n'.join(timestamps))

    print(f"Timestamps have been saved to '{file_name}'.")

def test_spdc_source(alice_angle,bob_angle):
    timeline = Timeline()
    source = source_node("source",timeline,2)
    alice = Receiver("alice",timeline)
    bob = Receiver("bob",timeline)

    qc1 = QuantumChannel("qc1",timeline,attenuation=0,distance=1)
    qc2 = QuantumChannel("qc2",timeline,attenuation=0,distance=1)

    qc1.set_ends(source,alice)
    qc2.set_ends(source,bob)

    """source.spdc.add_receiver(alice)
    source.spdc.add_receiver(bob)"""
    alice.hwp.set_angle(alice_angle)
    bob.hwp.set_angle(bob_angle)
    alice.hwp.set_matrix(alice.hwp,bob.hwp)   
    bob.hwp.set_matrix(alice.hwp,bob.hwp) 
    alice.hwp.other = bob.hwp
    bob.hwp.other = alice.hwp
    state_list = []
    STATE_LEN = 10000
    basis_list = [0 for _ in range(STATE_LEN)]
    alice.QSDetectorPolarization.set_basis_list(basis_list, 0, -1)
    bob.QSDetectorPolarization.set_basis_list(basis_list, 0, -1)
    for _ in range(STATE_LEN):
        state_list.append((complex(sqrt(1/2)),complex(sqrt(1/2))))
    timeline.init()
    source.spdc.emit(state_list)
    timeline.run()
    """print("alice photon counter0", alice.counter0.count)
    #print("alice photon rate", alice.counter0.get_rates())
    print("alice photon counter1", alice.counter1.count)
    print("bob photon counter0", bob.counter0.count)
    print("bob photon counter1", bob.counter1.count)
    file_name = "data/alice0.txt"
    save_logs(alice.counter0.log,file_name)
    file_name = "data/bob0.txt"
    save_logs(bob.counter0.log,file_name)
    file_name = "data/alice1.txt"
    save_logs(alice.counter1.log,file_name)
    file_name = "data/bob1.txt"
    save_logs(bob.counter1.log,file_name)"""
    coin_rate = test_coincidences(alice.counter0.log,bob.counter0.log)
    return coin_rate

def test_coincidences(alice_timestamps, bob_timestamps):
    calibration_range, calibration_binwidth = 1e3,1
    coinc_range_ns = 100
    counter_coincidences=Coincidences(np.array(alice_timestamps),np.array(bob_timestamps), calibration_range, calibration_binwidth)
    counter_coincidences.get_offset(calibration_range,calibration_binwidth)

    counter_coincidences.CoincidenceAndRates(coinc_range_ns)
    TotalCoinc = counter_coincidences.totalCoincidences
    rate = counter_coincidences.coincidencesPerSecond
    """coincidence_analyzer = Coincidences(config_file)
    coincidence_analyzer.load_timestamps(alice=alice_timestamps, bob=bob_timestamps,Load_from_file=False)
    coincidence_analyzer.find_peak()
    coincidence_analyzer.calculate_coincidences_and_rates()"""
    #coincidence_analyzer.print_values()
    #coincidence_analyzer.plot_histogram()
    #return coincidence_analyzer.coincidencesPerSecond
    return TotalCoinc


hwp_start_angle = 0
hwp_end_angle =180


angle_range = list(range(hwp_start_angle, hwp_end_angle+1, 1))

alice_angle_range=[-45,0,45,90]
#alice_angle_range=[0]
#angle_range = [0]
coinc_rate_plt = plt
for alice_angle in alice_angle_range:  
    coincidences_dict = []
    #counter1 = []
    #counter2 = []  
    for theta in angle_range:
        print("done for angle", theta)
        coin_rate= test_spdc_source(alice_angle=alice_angle,bob_angle=theta)
        coincidences_dict.append(coin_rate)
        print(coin_rate)
    coinc_rate_plt.plot(angle_range,coincidences_dict,'-', label = 'alice: '+str(alice_angle))
    #coinc_rate_plt.plot(H_rough,'-', label = 'Histograme'+str(state))
    #coinc_rate_plt.plot(edge[1:],H)


coinc_rate_plt.xlabel('Bob angle')
coinc_rate_plt.ylabel('coincidences')
coinc_rate_plt.legend()
coinc_rate_plt.show()

#print(test_spdc_source())
#test_coincidences()
