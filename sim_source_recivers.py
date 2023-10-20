from numpy import random
from sequence.components.light_source import SPDCSource
from sequence.components.photon import Photon
from sequence.kernel.timeline import Timeline
from sequence.utils.encoding import polarization
from sequence.topology.node import Node
from sequence.kernel.entity import Entity
from sequence.components.optical_channel import QuantumChannel
from coincidences import Coincidences

random.seed(0)
class source_port(Entity):
    def __init__(self, name, timeline:Timeline,owner:Node):
        super().__init__(name, timeline)
        self.name = name
        self.timeline = timeline
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
        self.timeline = timeline
        FREQ, MEAN = 1e7, 0.1
        self.spdc = SPDCSource("spdc", self.timeline, frequency=FREQ, mean_photon_num=MEAN, encoding_type=polarization)
        self.ports = {}
        for i in range (eg_photons_number):
            self.ports[i] = source_port(str(i), self.timeline, self)
            self.spdc.add_receiver(self.ports[i])
        self.first_component_name = self.spdc.name
    def get(self, photon, **kwargs):
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
        self.name = name
        self.timeline = timeline
        self.log = []
        self.photon_counter=0

    def receive_qubit(self, src: str, qubit) -> None:
        self.log.append((self.timeline.now(), qubit))
        self.photon_counter +=1
    def get_rates(self):
        if self.photon_counter > 0:
            rate = 1e12*self.photon_counter/(self.log[-1][0] - self.log[0][0])
        else:
            rate = 0
        return rate

def test_combine_state(photon1,photon2):
    state1 = photon1.quantum_state
    state2 = photon2.quantum_state
    try:
        for i, coeff in enumerate(state1.state):
            assert coeff == state2.state[i]
        assert state1.entangled_states == state2.entangled_states
        assert state1.entangled_states == [state1, state2]

        # If all assertions pass, return True
        return True

    except AssertionError:
        # If any assertion fails, return False
        return False

def save_logs(log_list,file_name):
    # Extract timestamps from the log list
    timestamps = [str(timestamp) for timestamp, _ in log_list]

    # Write the timestamps to the file
    with open(file_name, 'w') as file:
        file.write('\n'.join(timestamps))

    print(f"Timestamps have been saved to '{file_name}'.")

def test_spdc_source():
    timeline = Timeline()
    source = source_node("source",timeline,2)
    alice = Receiver("alice",timeline)
    bob = Receiver("bob",timeline)

    qc1 = QuantumChannel("qc1",timeline,attenuation=0.0002,distance=1000)
    qc2 = QuantumChannel("qc2",timeline,attenuation=0.0002,distance=1011)

    qc1.set_ends(source,alice)
    qc2.set_ends(source,bob)

    """source.spdc.add_receiver(alice)
    source.spdc.add_receiver(bob)"""

    state_list = []
    STATE_LEN = 1000
    for _ in range(STATE_LEN):
        state_list.append(polarization["bases"][0][0])
    timeline.init()
    source.spdc.emit(state_list)
    timeline.run()
    print("alice photon counter", alice.photon_counter)
    print("bob photon counter", bob.photon_counter)
    """file_name = "data/alice.txt"
    save_logs(alice.log,file_name)
    file_name = "data/bob.txt"
    save_logs(bob.log,file_name)"""

def test_coincidences():
    config_file = "config.yaml"
    alice_file = "data/alice.txt"
    bob_file = "data/bob.txt"

    coincidence_analyzer = Coincidences(config_file)
    coincidence_analyzer.load_timestamps(alice_file, bob_file)
    coincidence_analyzer.find_peak()
    coincidence_analyzer.calculate_coincidences_and_rates()
    coincidence_analyzer.print_values()
    coincidence_analyzer.plot_histogram()

test_spdc_source()
test_coincidences()
