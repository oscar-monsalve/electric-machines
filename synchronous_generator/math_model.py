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
        v_phi_delta = complex(nominal_voltage, 0)
        i_a_delta = load_current / np.sqrt(3)
        i_a_delta_rec = cmath.rect(i_a_delta, np.deg2rad(pf_angle))
        i_a_delta_pol = cmath.polar(i_a_delta_rec)
        return i_a_delta_rec, i_a_delta_pol, v_phi_delta

    if connection == "star":
        v_phi_star = complex(nominal_voltage / np.sqrt(3), 0)
        i_a_star = load_current
        i_a_star_rec = cmath.rect(i_a_star, np.deg2rad(pf_angle))
        i_a_star_pol = cmath.polar(i_a_star_rec)
        return i_a_star_rec, i_a_star_pol, v_phi_star
