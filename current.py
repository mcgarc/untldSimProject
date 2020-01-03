import warnings
import numpy as np


class AbstractCurrentProfile:
    """
    Abstract class describing the change of a current through time
    """

    def __init__(self):
        pass

    def __eq__(self, other):
        """
        Should override built in equality method
        """
        warnings.warn(
                'Current profile uses built-in equality method',
                UserWarning
                )
        return super().__eq__(other)

        

    def current(self, t):
        """
        Return the current at the specified time.
        """
        raise NotImplementedError


class ConstantCurrent(AbstractCurrentProfile):
    """
    Profile of a current that is constant through time
    """

    def __init__(self, current):
        self._current = current

    def __eq__(self, other):
        if isinstance(other, ConstantCurrent):
            if self.current(0) == other.current(0):
                return True
        return False


    def current(self, t):
        return self._current

class StepCurrent(AbstractCurrentProfile):
    """
    Current that steps through time. Takes a list of currents and a
    corresponding list of times of the same length. Each current element is the
    current *up to and excluding* the corresponding time element
    """

    def __init__(self, currents, times):
        self._currents = currents
        self._times = sorted(times)
        self._size = len(currents)
        self._check_times_currents()

    def __eq__(self, other):
        instance = isinstance(other, StepCurrent)
        size = self._size == len(other)
        curs = self.currents == other.currents
        times = self.times == other.times
        if instance and size and curs and times:
            return True
        return False

    def __len__(self):
        return self._size

    def _check_times_currents(self):
        """
        Check the relative length of currents and times
        """
        if len(self.currents) + 1 != len(self.times):
            raise ValueError('Mismatched current and time lengths')

    @property
    def times(self):
        return self._times

    @property
    def currents(self):
        return self._currents
        
    def current(self, t):
        cond_list = [t < self.times[0]]
        cond_list += [self.times[i] <= t and t < self.times[i+1] for i in range(self._size)] 
        cond_list += [t >= self.times[-1]]
        cur_list = [0] + self.currents + [0]
        return float(np.piecewise(t, cond_list, cur_list))

class RampCurrent(StepCurrent):
    """
    Current that ramps through time. Takes a list of currents and a
    corresponding list of times. At each time, ramp up to the next current and
    hold at that value until the next time. Ramps are linear.

    For inputs of currents = [1] and times = [0, 1, 2, 3] ramp will look like 
   1|     _____
    |    /     \
    |   /       \
    |  /         \
    | /           \
    |/             \
   0------------------
    0    1    2     3
    """

    def __init__(self, currents, times):
        super().__init__(currents, times)

    def _check_times_currents(self):
        """
        Overrides superclass check for relative length of times and currents
        """
        if len(self.times) != 2*len(self.currents) + 2:
            raise ValueError('Mismatched current and time lengths')
