from math import sin, cos, acos, degrees
# import cmath


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


def armature_current(connection: str, load_current: float, nominal_voltage: float, pf_angle: float) -> complex:
    """Returns the armature current I_A based on the load connection to the motor."""

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
