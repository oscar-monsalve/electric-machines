from math import sin, cos, asin, acos, sqrt, degrees, radians
import cmath


def hp2watts(hp: float) -> float:
    """Converts horse-power to watts"""

    return hp * 745.7


def input_power(p_out: float, p_mec: float, p_core: float) -> float:
    """Returns the input power in watts assuming that the copper losses are negligible"""

    return p_out + p_mec + p_core


def power_factor(pf_angle: float) -> float:
    return cos(radians(pf_angle))


def power_factor_angle(fp: float, type_of_load: str) -> float:
    """Returns the power factor angle based on the power factor and its sign."""

    pf_sign = 0
    if type_of_load not in ("lagging", "leading"):
        raise TypeError("Type of load is not a valid input. Try with 'lagging' or 'leading'.")
    elif type_of_load == "lagging":
        pf_sign = fp * -1
    elif type_of_load == "leading":
        pf_sign = fp

    if pf_sign < 0:
        return degrees(acos(pf_sign)) - 180
    elif pf_sign >= 0:
        return degrees(acos(pf_sign))


def initial_armature_current(connection: str, nominal_voltage: float,
                             pf_angle: float, p_in: float) -> tuple[complex, float, float, complex]:
    """Returns the armature current IA based on the motor connection."""

    if connection not in ("delta", "star"):
        raise TypeError("'Connection' is not a valid input. Try with 'delta' or 'star'.")
    elif connection == "delta":
        v_phi_delta = complex(nominal_voltage, 0)
        i_a_delta = p_in / (3 * nominal_voltage * cos(radians(abs(pf_angle))))
        i_a_delta_rec = cmath.rect(i_a_delta, radians(pf_angle))
        i_a_delta_mag = cmath.polar(i_a_delta_rec)[0]
        i_a_delta_angle = degrees(cmath.polar(i_a_delta_rec)[1])
        return i_a_delta_rec, i_a_delta_mag, i_a_delta_angle, v_phi_delta
    elif connection == "star":
        v_phi_star = complex(nominal_voltage / sqrt(3), 0)
        i_a_star = p_in / (3 * nominal_voltage * cos(radians(abs(pf_angle))))
        i_a_star_rec = cmath.rect(i_a_star, radians(pf_angle))
        i_a_star_mag = cmath.polar(i_a_star_rec)[0]
        i_a_star_angle = degrees(cmath.polar(i_a_star_rec)[1])
        return i_a_star_rec, i_a_star_mag, i_a_star_angle, v_phi_star


def line_current(armature_current: float, connection: str) -> float:
    if connection not in ("delta", "star"):
        raise TypeError("'Connection' is not a valid input. Try with 'delta' or 'star'.")
    elif connection == "delta":
        return armature_current * sqrt(3)
    elif connection == "star":
        return armature_current


def initial_ea_voltage(phase_voltage: complex, armature_current: complex,
                       syncrhonous_reactance: complex) -> tuple[complex, float, float]:
    ea_rec = phase_voltage - (armature_current * syncrhonous_reactance)
    ea_mag = cmath.polar(ea_rec)[0]
    ea_angle = degrees(cmath.polar(ea_rec)[1])
    return ea_rec, ea_mag, ea_angle


def new_ea_voltage(original_ea: float, field_current_increase: float) -> float:
    return (1 + (field_current_increase/100)) * original_ea


def new_delta_angle(initial_ea: float, new_ea: float, initial_delta_angle: float) -> float:
    return degrees(asin((initial_ea / new_ea) * sin(radians(initial_delta_angle))))


def new_armature_current(phase_voltage: complex, new_ea_voltage: complex,
                         syncrhonous_reactance: complex) -> tuple[complex, float, float]:
    ia2_rec = (phase_voltage - new_ea_voltage) / syncrhonous_reactance
    ia2_mag = cmath.polar(ia2_rec)[0]
    ia2_angle = degrees(cmath.polar(ia2_rec)[1])
    return ia2_rec, ia2_mag, ia2_angle
