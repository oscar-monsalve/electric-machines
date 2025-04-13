import cmath
from math import sqrt, radians, degrees, cos


def syncrhonous_impedance_magnitude(armature_resistance: float, syncrhonous_reactance: complex, ) -> complex:
    return sqrt(armature_resistance**2 + syncrhonous_reactance.imag**2)


def equivalent_circuit_resistance(armature_resistance: float, load_resistance: float, ) -> float:
    return armature_resistance + load_resistance


def equivalent_circuit_reactance(syncrhonous_reactance: float, load_reactance: complex) -> complex:
    return complex(0, syncrhonous_reactance.imag + load_reactance.imag)


def equivalent_circuit_impedance_magnitude(circuit_equivalent_resistance: float, circuit_equivalent_reactance: complex, ) -> float:
    return sqrt(circuit_equivalent_resistance**2 + circuit_equivalent_reactance.imag**2)


def power_factor_angle(load_impedance: complex) -> float:
    if load_impedance.imag == 0:
        return degrees(cmath.polar(load_impedance)[1])
    elif load_impedance.imag > 0:
        return degrees(cmath.polar(load_impedance)[1]) * -1
    elif load_impedance.imag < 0:
        return degrees(cmath.polar(load_impedance)[1]) * -1


def armature_current(internal_generated_voltage: float, equivalent_impedance: complex,
                     pf_angle: float) -> tuple[complex, tuple[float, float]]:
    ia = internal_generated_voltage / sqrt(equivalent_impedance.real**2 + equivalent_impedance.imag**2)
    i_a_rec = cmath.rect(ia, radians(pf_angle))
    i_a_pol = cmath.polar(i_a_rec)
    return i_a_rec, i_a_pol


def phase_voltage(armature_current_magnitude: float, load_impedance: float) -> float:
    return armature_current_magnitude * sqrt(load_impedance.real**2 + load_impedance.imag**2)


def line_voltage(phase_voltage: float) -> float:
    return phase_voltage * sqrt(3)


def input_power(line_voltage: float, armature_current: float, pf_angle: float, armature_resistance: float) -> float:
    p_out = sqrt(3) * line_voltage * armature_current * cos(radians(pf_angle))
    p_cu = 3 * armature_current**2 * armature_resistance
    return p_out + p_cu


def internal_generated_voltage_phasor(phase_voltage: float, armature_current: complex,
                                      syncrhonous_reactance: complex) -> tuple[float, float]:
    ea_rec = phase_voltage + armature_current * (syncrhonous_reactance)
    ea_magnitud = cmath.polar(ea_rec)[0]
    ea_phase_angle = degrees(cmath.polar(ea_rec)[1])
    return ea_magnitud, ea_phase_angle


def armature_resistance_voltage(armature_current: complex, armature_resistance: float) -> tuple[float, float]:
    v_ra = armature_current * armature_resistance
    v_ra_magnitud = cmath.polar(v_ra)[0]
    v_ra_angle = degrees(cmath.polar(v_ra)[1])
    return v_ra_magnitud, v_ra_angle


def syncrhonous_reactance_voltage(armature_current: complex, syncrhonous_reactance: complex) -> tuple[float, float]:
    v_xs = armature_current * syncrhonous_reactance
    v_xs_magnitud = cmath.polar(v_xs)[0]
    v_xs_angle = degrees(cmath.polar(v_xs)[1])
    return v_xs_magnitud, v_xs_angle
