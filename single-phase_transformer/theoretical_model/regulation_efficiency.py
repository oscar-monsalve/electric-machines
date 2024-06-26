import numpy as np


def load_apparent_power(is_load_percentage: bool, nominal_aparent_power: float) -> float:
    if is_load_percentage is True:
        load_percentage = float(input("What is load percentage connected to the secondary (%)?:\n"))
        return (nominal_aparent_power * load_percentage) / 100
    if is_load_percentage is False:
        load_aparent_power = float(input("What is the aparent power of the load in VA?:\n"))
        return load_aparent_power


def load_current(load_aparent_power: float, secondary_voltage: float) -> float:
    return load_aparent_power / secondary_voltage


def phase_angle() -> float:
    power_factor = float(input("What is the power factor of the load?\n"))
    return np.rad2deg(np.arccos(power_factor))


def load_active_reactive_powers(load_apparent_power: float, phase_angle: float) -> float:
    load_active_power = load_apparent_power * np.cos(np.deg2rad(phase_angle))
    load_reactive_power = load_apparent_power * np.sin(np.deg2rad(phase_angle))
    return load_active_power, load_reactive_power


def secondary_open_circuit_voltage(phase_angle: float, secondary_voltage: float, load_current: float,
                                   secondary_equivalent_resistance: float, secondary_equivalent_reactance:
                                   float) -> float:
    return np.sqrt((secondary_voltage*np.cos(np.deg2rad(phase_angle))+load_current*secondary_equivalent_resistance)**2 + (secondary_voltage*np.sin(np.deg2rad(phase_angle))+load_current*secondary_equivalent_reactance)**2)


def voltage_regulation(secondary_open_circuit_voltage: float, secondary_voltage: float) -> float:
    return ((secondary_open_circuit_voltage - secondary_voltage) / (secondary_voltage)) * 100


def efficiency(phase_angle: float, secondary_voltage: float, load_current: float, secondary_equivalent_resistance:
               float, open_circuit_power: float) -> float:
    return ((secondary_voltage*load_current*np.cos(np.rad2deg(phase_angle))) / (secondary_voltage*load_current*np.cos(np.rad2deg(phase_angle))+secondary_equivalent_resistance*load_current**2+open_circuit_power)) * 100
