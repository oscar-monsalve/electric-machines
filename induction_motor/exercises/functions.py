import numpy as np
import cmath


def preliminars(line_voltage, load_resistance, slip, rotor_resistance, eq_impedance):
    """
    Returns the phase voltage from the line voltage in (V).
    Returns the load resistance as a function of the slip in (Ohms).
    Returns the equivalent impedance using the rotor impedance and the load resistance in (Ohms).
    """

    phase_voltage = complex(line_voltage / np.sqrt(3), 0)  # Phase voltage
    r_l = load_resistance / slip  # Load resistance
    z_eq = rotor_resistance + eq_impedance + r_l  # Equivalent impedance

    return phase_voltage, r_l, z_eq


def rotor_velocity(s, field_velocity):
    """
    Returns the rotor velocity in (rpm)
    """

    return (1 - s) * field_velocity


def rotor_current(phase_voltage, z_eq):
    """
    Returns the rotor current in (A) in cartesian and polar coordinates.
    """
    i_r = phase_voltage / z_eq
    i_r_polar = cmath.polar(i_r)

    return i_r, i_r_polar


def rotor_power(i_r_polar, r_l):
    """
    Returns the rotor power (output power) in (W).
    """
    p_r = 3 * i_r_polar[0]**2 * r_l

    return p_r


def torque(rotor_rpm, p_r):
    """
    Returns the rotor torque in (Nm).
    """
    omega = rotor_rpm * 2 * np.pi / 60
    t = p_r / omega

    return t


def motor_efficiency(phase_voltage, r_m, jx_m, i_r, p_r, fp):
    """
    Returns the motor efficiency in (%).
    The function takes as input parameters the core impedance (r_m, jx_m), the rotor current (i_r), the rotor power (p_r), and the
    power factor (fp).
    """
    i_f = phase_voltage / r_m  # Current through the core reactance
    i_m = phase_voltage / jx_m  # Current through the core resistance
    i_0 = i_f + i_m
    i_en = i_0 + i_r  # Input current
    i_en_polar = cmath.polar(i_en)
    p_en = 3 * np.real(phase_voltage) * i_en_polar[0] * fp  # Input power
    eta = (p_r / p_en) * 100  # Efficiency

    return eta, i_en_polar
