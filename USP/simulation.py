from USP import trap as USP_trap
from USP import particle
from USP import utils
import numpy as np
from itertools import repeat
import multiprocessing as mp
import pickle

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def _integ(particle, potential, t_0, t_end, dt, out_times):
    """
    Call init_integ of a passed mol. For parallelisation
    """
    particle.integ(potential, t_0, t_end, dt)
    return particle


class Simulation:
    """
    """

    def __init__(self,
            process_no,
            trap,
            t_0,
            t_end,
            dt,
            ):
        """
        """
        self._process_no = process_no
        self.set_trap(trap)
        self._t_0 = t_0
        self._t_end = t_end
        self._dt = dt
        self._eval_times = np.arange(t_0, t_end, dt)
        self._particles = None

    @property
    def particles(self):
        return self._particles

    @property
    def result(self):
        """
        TODO: May be helpful to provide some sort of reduced form of output for
        exporting
        """
        raise NotImplemented

    def set_trap(self, trap):
        """
        Set trap, checking type in the process. Can also set trap to None.
        """
        if trap is None:
            self._trap = None
        elif isinstance(trap, USP_trap.AbstractTrap):
            self._trap = trap
        else:
            raise ValueError(
            'trap is not of valid type, expected None or AbstractTrap'
            )

    def get_rs(self, t):
        """
        Return a list of all particles positions at the given time
        """
        rs = [ p.r(t) for p in self._particles ]
        return rs

    def get_vs(self, t):
        """
        Return a list of all particles velocities at the given time
        """
        vs = [ p.v(t) for p in self._particles ]
        return vs

    def save_to_pickle(self, filename):
        """
        Save particles as a pickle
        """
        with open(filename, 'wb') as f:
            pickle.dump(self._particles, f)

    def load_from_pickle(self, filename):
        """
        Load particles from pickle
        """
        with open(filename, 'rb') as f:
            self._particles = pickle.load(f)


    def run(self):
        """
        Run the simulation using multiprocessing. Creates particles
        """
        # Check that a trap has been specified
        if self._trap is None:
            raise RuntimeError('No trap has been specified for this simulation')

        # Create args for _integ running in parallel
        args = zip(
                self._particles,
                repeat(self._trap.potential),
                repeat(self._t_0),
                repeat(self._t_end),
                repeat(self._dt),
                repeat([0, self._t_end]) # FIXME Should be arbitrary
                )

        # Multiprocessing
        with mp.Pool(self._process_no) as p:
            self._particles = p.starmap(_integ, args)

    def init_particles(
            self,
            particle_no,
            mass,
            r_sigma,
            v_sigma,
            r_centre = [0, 0, 0],
            v_centre = [0, 0, 0],
            seed = None
            ):
        """
        Create particles for simulation.

        Args:
        particle_no: int
        mass: float
        r_sigma: std for particle position distribution
        v_sigma: std for particle velocity distribution
        r_centre: where to centre positions (default origin)
        v_centre: where to centre velocities (default origin)
        seed: if not None, sets the numpy seed

        Output:
        None, populates self._particles
        """

        if seed is not None:
            np.seed(seed)

        # Clean sigma input into np arrays of length 3
        if type(r_sigma) in [float, int]:
            r_sigma = [r_sigma, r_sigma, r_sigma]
        if type(v_sigma) in [float, int]:
            v_sigma = [v_sigma, v_sigma, v_sigma]
        r_sigma = utils.clean_vector(r_sigma)
        v_sigma = utils.clean_vector(v_sigma)

        # Clean centre inputs into np arrays of length 3
        r_centre = utils.clean_vector(r_centre)
        v_centre = utils.clean_vector(v_centre)

        # Generate particles
        self._particles = [
            particle.Particle(
              [
                  np.random.normal(r_centre[0], r_sigma[0]),
                  np.random.normal(r_centre[1], r_sigma[1]),
                  np.random.normal(r_centre[2], r_sigma[2])
              ],
              [
                  np.random.normal(v_centre[0], v_sigma[0]),
                  np.random.normal(v_centre[1], v_sigma[1]),
                  np.random.normal(v_centre[2], v_sigma[2])
              ],
              mass
              )
            for i in range(particle_no)
            ]

    def plot_start_end_positions(self):
        """
        """
        start_rs = np.array(self.get_rs(self._t_0)).transpose()
        end_rs = np.array(self.get_rs(self._t_end)).transpose()
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(start_rs[0], start_rs[1], start_rs[2], 'b')
        ax.scatter(end_rs[0], end_rs[1], end_rs[2], 'r')
        plt.show()

    def get_total_energy(self, t):
        """
        Get the total energy (KE + potential) at a specified time 
        """
        energies = [p.energy(t, self._trap.potential) for p in self._particles]
        return np.sum(np.array(energies))
