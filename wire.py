import numpy as np
import scipy.constants as spc


class WireSegment:
    """
    Simulates a segment of straight wire
    """

    def __init__(self, start, end, current):
        self.set_start(start)
        self.set_end(end)
        self.set_current(current)

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def current(self):
        return self._current

    @property
    def wire_vector(self):
        """
        Wire as a vector
        """
        return self.end - self.start

    def _clean_vector(self, vector, length=3):
        """
        Ensure a vector is of the right length and format before setting it
        """
        vector = np.array(vector)
        if len(vector) != 3:
            raise ValueError(f'Vector should have length {length}')
        return vector

    def set_start(self, start):
        self._start = self._clean_vector(start)

    def set_end(self, end):
        self._end = self._clean_vector(end)

    def set_current(self, current):
        self._current = current

    def field(self, r):
        """
        Return the field generated by the wire at position r
        """
        r = self._clean_vector(r)
        # Find the smallest vector from r to wire, if the wire were inifinite
        param = np.dot(r - self.start, self.wire_vector)
        param /= np.dot(self.wire_vector, self.wire_vector) 
        a = self.start - r + param * self.wire_vector
        a_norm = np.linalg.norm(a)
        # Field direction is normal to the wire-point plane
        # TODO check sign!
        direction = np.cross(self.wire_vector, r - self.start)
        direction = direction / np.sqrt(np.dot(direction, direction))
        # Magnitude from the standard formula
        start_rel = r - self.start
        cos_start = np.dot(start_rel, a)
        cos_start /= (np.linalg.norm(start_rel) * a_norm)
        sin_start = np.sqrt(1 - cos_start**2)
        end_rel = r - self.end
        cos_end = np.dot(end_rel, a)
        cos_end /= (np.linalg.norm(end_rel) * a_norm)
        sin_end = np.sqrt(1 - cos_end**2)
        mag = spc.mu_0 * self.current * (sin_end + sin_start) / (4*np.pi*a_norm)
        return mag * direction


class WireCluster:
    """
    Holds a list of WireSegments. Can be used to find the fields of all of them
    by taking the sum of each segment's contribution.
    """
    def __init__(self, wires):
        self.set_wires(wires)

    def set_wires(self, wires):
        """
        Check that each element of the list is a WireSegment
        """
        for wire in wires:
            if type(wire) != WireSegment:
                raise ValueError(
                    'All wires in cluster must have type WireSegment'
                    )
        self._wires = wires.copy()

    def field(self, r):
        """
        Get cluster field by summing each segment's contribution
        """
        field = [ wire.field(r) for wire in self._wires ]
        return sum(field)
