import cmath
from math import sqrt
from math import radians


def syncrhonous_impedance() -> complex:
    pass


def equivalent_circuit_resistance() -> float:
    pass


def equivalent_circuit_reactance() -> complex:
    pass


def equivalent_circuit_impedance_magnitude() -> float:
    pass


def power_factor_angle(load_impedance: complex, load_type: str) -> float:
    if load_type not in ("r", "l", "c"):
        raise TypeError("Incorrect load type. Insert 'r', 'l', or 'c' for resistive, inducive or capacitive load.")
    elif load_type == "r":
        return cmath.polar(load_impedance)[1]
    elif load_type == "l":
        pass
    elif load_type == "c":
        pass


def armature_current(connection: str, load_current: float, nominal_voltage: float, pf_angle: float) -> complex:
    """Returns the armature current I_A based on the load connection to the generator."""

    if connection == "delta":
        v_phi_delta = complex(nominal_voltage, 0)
        i_a_delta = load_current / sqrt(3)
        i_a_delta_rec = cmath.rect(i_a_delta, radians(pf_angle))
        i_a_delta_pol = cmath.polar(i_a_delta_rec)
        return i_a_delta_rec, i_a_delta_pol, v_phi_delta

    if connection == "star":
        v_phi_star = complex(nominal_voltage / sqrt(3), 0)
        i_a_star = load_current
        i_a_star_rec = cmath.rect(i_a_star, radians(pf_angle))
        i_a_star_pol = cmath.polar(i_a_star_rec)
        return i_a_star_rec, i_a_star_pol, v_phi_star
