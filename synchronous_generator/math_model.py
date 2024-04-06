import numpy as np
import cmath


def power_factor_sign(type_of_load: str, fp: float) -> float:
    """Returns the sign (+ or -) based on the type of load."""

    if type_of_load == "lagging":
        return fp * -1
    if type_of_load == "leading":
        return fp


def power_factor_angle(fp: float) -> float:
    """Returns the power factor angle based on the power factor and its sign."""

    if fp < 0:
        return np.rad2deg(np.arccos(fp)) - 180
    if fp >= 0:
        return np.rad2deg(np.arccos(fp))


def velocity(freq: int, poles: int) -> int:
    """Returns the generator's angular velocity based on the frequency and number of poles."""

    return (120 * freq) / poles


def armature_current(connection: str, load_current: float, nominal_voltage: float, pf_angle: float) -> float:
    """Returns the armature current I_A based on the load connection to the generator."""

    if connection == "delta":
        i_a_delta = complex(load_current / np.sqrt(3), pf_angle)
        v_phi_delta = complex(nominal_voltage, 0)
        i_a_polar = cmath.polar(i_a_delta)
        v_phi_polar = cmath.polar(v_phi_delta)
    if connection == "star":
        i_a_star = complex(load_current, pf_angle)
        v_phi_star = complex(nominal_voltage / np.sqrt(3), 0)
        i_a_polar = cmath.polar(i_a_star)
        v_phi_polar = cmath.polar(v_phi_star)

    return i_a_delta, i_a_polar, v_phi_polar
