import numpy as np


def total_resistance(power_short_circuit: float, current_short_circuit: float) -> float:
    """Returns the total equivalent resistance in ohms. The blocked (or short circuit) rotor test is used to determine the input
    parameters."""

    r_e = (2 * power_short_circuit) / (3 * current_short_circuit ** 2)

    return r_e


def rotation_losses(power_no_load: float, current_no_load: float, equivalent_resistance: float) -> float:
    """Returns the rotation losses (P_r) in watts using the results of the no load test."""

    p_r = power_no_load - (current_no_load ** 2 * equivalent_resistance)

    return p_r


def copper_losses_per_load(power_short_circuit: float, load: float) -> float:
    """Returns the copper losses in watts as a function of the load."""

    p_cu = power_short_circuit * (load ** 2)

    return p_cu


def input_power(voltage_line: float, current_no_load: float, pf: float) -> float:
    """Returns the motor input power in watts."""

    p_in = np.sqrt(3) * voltage_line * current_no_load * pf

    return p_in


def efficiency(input_power: float, load: float, rotation_losses: float, copper_losses: float) -> float:
    """Returns the motor efficiency in percentage."""

    eff = (1 - ((rotation_losses + copper_losses) / (input_power * load))) * 100

    return eff


def output_power(input_power: float, load: float, rotation_losses: float, copper_losses: float) -> float:
    """Returns the output power in watts and hp."""

    p_out_watts = (input_power * load) - (rotation_losses + copper_losses)
    p_out_hp = ((input_power * load) - (rotation_losses + copper_losses)) / 745.7

    return p_out_watts, p_out_hp


def torque(output_power: float, velocity: float) -> float:
    """Returns the motor torque using the output power in Nm."""

    torque = output_power / ((velocity * 2 * np.pi) / 60)

    return torque
