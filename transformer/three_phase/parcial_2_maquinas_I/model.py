from math import cos, sin, acos, sqrt, degrees, radians


def line_voltage_secondary(line_voltage_at_primary: float, simple_transf_ratio: float) -> float:
    return line_voltage_at_primary / (sqrt(3) * simple_transf_ratio)

def line_current_primary(apparent_power_nominal: float, line_voltage_at_primary: float) -> float:
    return apparent_power_nominal / (sqrt(3) * line_voltage_at_primary)

def load_current_phase(load_apparent_power: float, vl2: float) -> float:
    return load_apparent_power / (3 * vl2)

def power_factor_angle(power_factor: float) -> float:
    return degrees(acos(power_factor))

def efficiency(
    phase_voltage_secondary: float,
    phase_load_current_secondary: float,
    power_factor_angle: float,
    equivalent_resistance_secondary: float,
    open_circuit_losses: float
) -> [float]:
    p_out = 3 * phase_voltage_secondary * phase_load_current_secondary * cos(radians(power_factor_angle))
    p_cu = 3 * phase_load_current_secondary ** 2 * equivalent_resistance_secondary
    effic = (p_out / (p_out + p_cu + open_circuit_losses)) * 100

    return effic, p_out, p_cu

def open_circuit_voltage_secondary(
    phase_voltage_secondary: float,
    phase_load_current_secondary: float,
    power_factor_angle: float,
    equivalent_resistance_secondary: float,
    equivalent_reactance_secondary: float
) -> float:
    vf2_cos_phi = phase_voltage_secondary * cos(radians(power_factor_angle))
    icf2_ref2 = phase_load_current_secondary * equivalent_resistance_secondary
    vf2_sin_phi = phase_voltage_secondary * sin(radians(power_factor_angle))
    icf2_xef2 = phase_load_current_secondary * equivalent_reactance_secondary

    return sqrt((vf2_cos_phi + icf2_ref2) ** 2 + (vf2_sin_phi + icf2_xef2) ** 2)

def voltage_regulation(v20: float, phase_voltage_secondary: float) -> float:
    return ((v20 - phase_voltage_secondary) / phase_voltage_secondary) * 100
