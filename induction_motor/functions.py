import numpy as np
import cmath


def rotor_velocity(s, field_velocity):
    """
    Returns the rotor velocity in (rpm)
    """
    return (1 - s) * field_velocity

