import numpy as np


def transformation_ratio(primary_voltage: float, secondary_voltage: float) -> float:
    return primary_voltage / secondary_voltage


def nominal_current(nominal_aparent_power: float, nominal_voltage: float) -> float:
    """
    nominal_current() -> float.
    Calculates the nominal current of the primary or the secondary.
    nominal_aparent_power: primary or secondary, nominal_voltage: primary or secondary.
    """

    return nominal_aparent_power / nominal_voltage


def open_circuit_test_side(open_circuit_current: float, primary_current: float, secondary_current: float) -> str:
    """
    open_circuit_test_side() -> str.
    Determines if the open-circuit test was performed at the primary or secondary.
    """

    ratio_open_circuit_current_to_primary_current = open_circuit_current / primary_current
    ratio_open_circuit_current_to_secondary_current = open_circuit_current / secondary_current

    if ratio_open_circuit_current_to_primary_current <= 0.8:
        return "primary"
    if ratio_open_circuit_current_to_secondary_current <= 0.8:
        return "secondary"


def open_circuit_aparent_power(short_circuit_side: str, primary_voltage: float, secondary_voltage: float, open_circuit_current: float) -> float:
    if short_circuit_side == "primary":
        return primary_voltage * open_circuit_current
    if short_circuit_side == "secondary":
        return secondary_voltage * open_circuit_current


def open_circuit_reactive_power(open_circuit_aparent_power: float, open_circuit_active_power: float) -> float:
    return np.sqrt(open_circuit_aparent_power**2 - open_circuit_active_power**2)


def core_resistance_and_reactance(short_circuit_side: str, transformation_ratio: float, primary_voltage: float,
                                  secondary_voltage: float, open_circuit_active_power: float,
                                  open_circuit_reactive_power: float) -> float:

    if short_circuit_side == "primary":
        rm1 = primary_voltage ** 2 / open_circuit_active_power
        xm1 = primary_voltage ** 2 / open_circuit_reactive_power
        rm2 = rm1 / transformation_ratio ** 2
        xm2 = xm1 / transformation_ratio ** 2
        return rm1, xm1, rm2, xm2
    if short_circuit_side == "secondary":
        rm2 = secondary_voltage ** 2 / open_circuit_active_power
        xm2 = secondary_voltage ** 2 / open_circuit_reactive_power
        rm1 = rm2 * transformation_ratio ** 2
        xm1 = xm2 * transformation_ratio ** 2
        return rm1, xm1, rm2, xm2


def core_currents(short_circuit_side: str, primary_voltage: float, secondary_voltage: float,
                  primary_core_resistance: float, primary_core_reactance: float, secondary_core_resistance: float,
                  secondary_core_reactance: float) -> float:

    if1 = primary_voltage / primary_core_resistance
    im1 = primary_voltage / primary_core_reactance
    if2 = secondary_voltage / secondary_core_resistance
    im2 = secondary_voltage / secondary_core_reactance
    return if1, im1, if2, im2


def open_circuit_current(if1: float, im1: float, if2: float, im2: float) -> float:
    primary_open_circuit_current = np.sqrt(if1**2 + im1**2)
    secondary_open_circuit_current = np.sqrt(if2**2 + im2**2)
    return primary_open_circuit_current, secondary_open_circuit_current


def short_circuit_test_side(short_circuit_voltage: float, primary_voltage: float, secondary_voltage: float) -> str:
    """
    short_circuit_test_side() -> str.
    Determines if the short-circuit test was performed at the primary or secondary.
    """

    ratio_short_circuit_voltage_to_primary_voltage = short_circuit_voltage / primary_voltage
    ratio_short_circuit_voltage_to_secondary_voltage = short_circuit_voltage / secondary_voltage

    if ratio_short_circuit_voltage_to_primary_voltage <= 0.8:
        return "primary"
    if ratio_short_circuit_voltage_to_secondary_voltage <= 0.8:
        return "secondary"


def short_circuit_aparent_power(short_circuit_side: str, short_circuit_voltage: float, primary_current: float,
                                secondary_current: float) -> float:
    if short_circuit_side == "primary":
        return short_circuit_voltage * primary_current
    if short_circuit_side == "secondary":
        return short_circuit_voltage * secondary_current


def short_circuit_reactive_power(short_circuit_aparent_power: float, short_circuit_active_power: float) -> float:
    return np.sqrt(short_circuit_aparent_power**2 - short_circuit_active_power**2)


def equivalent_resistance_and_reactance(short_circuit_active_power: float, short_circuit_reactive_power: float,
                                        primary_current: float, secondary_current: float) -> float:
    re1 = short_circuit_active_power / primary_current ** 2
    xe1 = short_circuit_reactive_power / primary_current ** 2
    re2 = short_circuit_active_power / secondary_current ** 2
    xe2 = short_circuit_reactive_power / secondary_current ** 2

    return re1, xe1, re2, xe2


def primary_secondary_impedances(transformation_ratio: float, primary_equivalent_resistance: float,
                                 primary_equivalent_reactance: float, secondary_equivalent_resistance: float,
                                 secondary_equivalent_reactance: float) -> float:
    r1 = primary_equivalent_resistance / 2
    x1 = primary_equivalent_reactance / 2
    r2 = primary_equivalent_resistance / (2 * transformation_ratio ** 2)
    x2 = primary_equivalent_reactance / (2 * transformation_ratio ** 2)

    return r1, x1, r2, x2
