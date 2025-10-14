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


def armature_current(connection: str, load_current: float, nominal_voltage: float, pf_angle: float) -> complex:
    """Returns the armature current I_A based on the load connection to the generator."""

    if connection not in ("delta", "star"):
        raise TypeError("'Connection' is not a valid input. Try with 'delta' or 'star'.")
    elif connection == "delta":
        v_phi_delta = complex(nominal_voltage, 0)
        i_a_delta = load_current / np.sqrt(3)
        i_a_delta_rec = cmath.rect(i_a_delta, np.deg2rad(pf_angle))
        i_a_delta_pol = cmath.polar(i_a_delta_rec)
        return i_a_delta_rec, i_a_delta_pol, v_phi_delta
    elif connection == "star":
        v_phi_star = complex(nominal_voltage / np.sqrt(3), 0)
        i_a_star = load_current
        i_a_star_rec = cmath.rect(i_a_star, np.deg2rad(pf_angle))
        i_a_star_pol = cmath.polar(i_a_star_rec)
        return i_a_star_rec, i_a_star_pol, v_phi_star


def complex_reactance(xs: float) -> complex:
    return complex(0, xs)


def complex_resistance(ra: float) -> complex:
    return complex(ra, 0)


def internal_voltage(v_phi: complex, xs: complex, ra: complex, ia: complex) -> complex:
    v_jxs_rec = xs * ia
    v_ra_rec = ra * ia
    e_a_rec = v_phi + v_jxs_rec + v_ra_rec
    return cmath.polar(v_jxs_rec), cmath.polar(v_ra_rec), cmath.polar(e_a_rec)


def copper_losses(i_a: complex, r_a: complex) -> float:
    return 3 * (i_a[0]) ** 2 * r_a.real


def output_power(v_nominal: float, i_load: float, fp: float) -> float:
    return np.sqrt(3) * v_nominal * i_load * fp


def input_power(p_mech_misc: float, p_core: float, p_cu: float, p_out: float) -> float:
    return p_mech_misc + p_core + p_cu + p_out


def efficiency(p_in: float, p_out: float) -> float:
    return (p_out / p_in) * 100


def apparent_power(p_out: float, fp: float) -> float:
    return p_out / fp


def reactive_power(s: float, p_out: float) -> float:
    return np.sqrt(s ** 2 - p_out ** 2)


def converted_power(p_cu: float, p_out: float) -> float:
    return p_cu + p_out


def induced_torque(p_conv: float, velocity: float) -> float:
    velocity_rad = velocity * ((2 * np.pi) / 60)
    return p_conv / velocity_rad


def applied_torque(p_in: float, velocity: float):
    velocity_rad = velocity * ((2 * np.pi) / 60)
    return p_in / velocity_rad
