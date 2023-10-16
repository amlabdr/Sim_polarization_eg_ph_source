"""Models for simulation of wave plate.

This module introduces the HalfWavePlates class.
The wave plate modifies the phase of incoming photons, but does not add additional delay or losses.
"""
from numpy import pi, cos, sin
from math import e
import numpy as np
from cmath import exp

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sequence.components.photon import Photon

from sequence.kernel.entity import Entity


class HalfWavePlate(Entity):
    """Class implementing a simple half wave plate.

    Attributes:
        name (str): name of the wave plate instance.
        timeline (Timeline): simulation timeline.
        angle with fast axis at angle
        fidelity (float): fraction of qubits not lost on the reflective surface
    """

    def __init__(self, name, timeline, angle = 0, fidelity=1):
        """Constructor for wave plate class.

        Args:
            name (str): name of the wave plate.
            timeline (Timeline): simulation timeline.
            angle with fast axis at angle: (default 0)
            phase (float): phase to apply to incoming photons (default 0.0).
        """

        super().__init__(name, timeline)
        self.fidelity = fidelity
        self.angle = angle
               
    

    def init(self):
        """Implementation of Entity interface (see base class)."""
        assert len(self._receivers) == 1, "BeamSplitter should only be attached to 1 output."
        
    

    
    def set_angle(self, angle: float):
        """Method to change the angle with fast axis 
        Args:
            angle (float): new phase to use.
        """
        self.angle=angle/2
        theta = np.radians(self.angle)
        self.mat = np.array([[cos(2*theta) , sin(2*theta)],
                        [sin(2*theta),   -cos(2*theta)]])

    def set_matrix(self, HWP1,HWP2):
        #self.HWP_4dM = np.tensordot(HWP1.mat,HWP2.mat)
        self.HWP_4dM = np.kron(HWP1.mat,HWP2.mat)        

    def get_angle(self):
        """Method to get the angle with fast axis """
        return self.angle

    def get(self, photon: "Photon", setstate =True):
        #print("before HWP: ",photon.quantum_state.state)
        """Method to receive a photon for measurement.

        Args:
            photon (Photon): photon to measure (must have polarization encoding)

        """
        
        state = photon.quantum_state.state
        assert photon.encoding_type["name"] == "polarization", "hwp should only be used with polarization."
        rng = self.get_generator()

        if rng.random() < self.fidelity and setstate:
            #state = tuple(np.dot(self.HWP_4d, state))  
            state = tuple(self.HWP_4dM.dot(state))
            photon.set_state(state)
        #print("after HWP: ",photon.quantum_state.state)
        self._receivers[0].get(photon)
        

class HalfWavePlate2dim(Entity):
    """Class implementing a simple half wave plate.

    Attributes:
        name (str): name of the wave plate instance.
        timeline (Timeline): simulation timeline.
        angle with fast axis at angle
        fidelity (float): fraction of qubits not lost on the reflective surface
    """

    def __init__(self, name, timeline, angle = 0, fidelity=1):
        """Constructor for wave plate class.

        Args:
            name (str): name of the wave plate.
            timeline (Timeline): simulation timeline.
            angle with fast axis at angle: (default 0)
            phase (float): phase to apply to incoming photons (default 0.0).
        """

        super().__init__(name, timeline)
        self.fidelity = fidelity
        self.angle = angle
        
    

    def init(self):
        """Implementation of Entity interface (see base class)."""
        assert len(self._receivers) == 1, "BeamSplitter should only be attached to 1 output."
        
    def HWP_2d (self, angle):
        mat = np.array([[cos(2*angle) , sin(2*angle)],
                        [sin(2*angle),   -cos(2*angle)]])
        # Extend the Jones matrix to 4x4 using the Kronecker product
        self.HWP_2d = mat

    def set_angle(self, angle: float):
        """Method to change the angle with fast axis 
        Args:
            angle (float): new phase to use.
        """
        self.angle=angle/2
        theta = np.radians(self.angle)
        self.HWP_2d(theta)
        

    def get_angle(self):
        """Method to get the angle with fast axis """
        return self.angle

    def get(self, photon: "Photon", **kwargs):
        #print("before HWP: ",photon.quantum_state.state)
        """Method to receive a photon for measurement.

        Args:
            photon (Photon): photon to measure (must have polarization encoding)

        """
        
        state = photon.quantum_state.state
        assert photon.encoding_type["name"] == "polarization", "hwp should only be used with polarization."
        rng = self.get_generator()
        if rng.random() < self.fidelity:
            state = tuple(self.HWP_2d.dot(state))
            photon.set_state(state)
        #print("after HWP: ",photon.quantum_state.state)
        self._receivers[0].get(photon)