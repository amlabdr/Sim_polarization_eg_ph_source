from numpy import random
from sequence.components.light_source import SPDCSource
from sequence.components.photon import Photon
from sequence.kernel.timeline import Timeline
from sequence.utils.encoding import polarization

random.seed(0)

#class for simple Reciver 
class Receiver:
    def __init__(self, name, timeline):
        self.name = name
        self.timeline = timeline
        self.log = []
        self.photon_counter=0

    def get(self, photon):
        if self.name == "reciver2":
            delay = -3500
        else:delay = 0
        self.log.append((self.timeline.now() +delay, photon))
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
    tl = Timeline()
    FREQ, MEAN = 1e7, 0.1
    spdc = SPDCSource("spdc", tl, frequency=FREQ, mean_photon_num=MEAN, encoding_type=polarization)
    receiver1 = Receiver("reciver1",tl)
    receiver2 = Receiver("reciver2",tl)
    spdc.add_receiver(receiver1)
    spdc.add_receiver(receiver2)

    state_list = []
    STATE_LEN = 10000
    for _ in range(STATE_LEN):
        basis = random.randint(2)
        bit = random.randint(2)
        state_list.append(polarization["bases"][basis][bit])

    tl.init()
    spdc.emit(state_list)
    tl.run()

    assert (len(receiver1.log) / STATE_LEN) - MEAN < 0.1
    assert (len(receiver2.log) / STATE_LEN) - MEAN < 0.1
    """for qubit1 , qubit2 in zip(receiver1.log,receiver2.log):
        print(test_combine_state(qubit1[1],qubit2[1]))"""
    print(receiver1.get_rates())
    print(receiver2.get_rates())
    print(len(receiver2.log))

    """# Define the file name
    file_name = "data/spdc_timestamps.txt"
    save_logs(receiver1.log,file_name)"""
    file_name = "coincidences_analyse/alice.txt"
    save_logs(receiver1.log,file_name)
    file_name = "coincidences_analyse/bob.txt"
    save_logs(receiver2.log,file_name)
    

test_spdc_source()
