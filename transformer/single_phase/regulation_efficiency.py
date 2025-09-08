from numpy import cos, sin, arccos, sqrt, rad2deg, deg2rad


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
    return rad2deg(arccos(power_factor))


def load_active_reactive_powers(load_apparent_power: float, phase_angle: float) -> float:
    load_active_power = load_apparent_power * cos(deg2rad(phase_angle))
    load_reactive_power = load_apparent_power * sin(deg2rad(phase_angle))
    return load_active_power, load_reactive_power


def secondary_open_circuit_voltage(phase_angle: float,
                                   secondary_voltage: float,
                                   load_current: float,
                                   secondary_equivalent_resistance: float,
                                   secondary_equivalent_reactance: float) -> float:
    v_re2 = load_current * secondary_equivalent_resistance
    v_xe2 = load_current * secondary_equivalent_reactance
    return sqrt((secondary_voltage*cos(deg2rad(phase_angle)) + v_re2)**2 + (secondary_voltage * sin(deg2rad(phase_angle)) + v_xe2)**2)


def voltage_regulation(secondary_open_circuit_voltage: float, secondary_voltage: float) -> float:
    return ((secondary_open_circuit_voltage - secondary_voltage) / (secondary_voltage)) * 100


def efficiency(phase_angle: float,
               secondary_voltage: float,
               load_current: float,
               secondary_equivalent_resistance: float,
               open_circuit_power: float) -> float:

    p_out = secondary_voltage * load_current * cos(deg2rad(phase_angle))
    p_in = p_out + secondary_equivalent_resistance * load_current**2 + open_circuit_power
    return (p_out / p_in) * 100
