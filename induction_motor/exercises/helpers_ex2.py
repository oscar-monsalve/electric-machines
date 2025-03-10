from math import sqrt, pi


def phase_voltage(line_voltage: float, connection) -> float:
    """
    Returns the phase voltage depending on the motor connection.

    Args:
    - line_voltage: line-to-line nominal motor voltage.
    - connection: 1 if connected in "wye" or 2 if connected in "delta".
    """
    if connection == 1:
        return line_voltage / sqrt(3)
    if connection == 2:
        return line_voltage


def synchronous_velocity(frequency: float, poles: int) -> float:
    """Returns the motor synchronous velocity in rpm."""
    return (120 * frequency) / poles


def shaft_velocity(synchronous_velocity: float, slip: float) -> float:
    """
    Returns the motor shaft velocity in rpm at a given slip "s".

    Args:
    - synchronous_velocity: motor synchronous velocity in rpm.
    - slip: motor slip in range (0 < s <= 1).
    """
    return (1 - slip) * synchronous_velocity


def rpm2radsec(rpm: float) -> float:
    return rpm * (2*pi/60)


def thevenin_voltage(phase_voltage: float, r1: float, x1: complex, xm: complex) -> float:
    """
    Returns the Thevenin voltage in volts.

    Args:
    - phase_voltage: Motor phase voltage in volts.
    - r1: Stator resistance in ohms.
    - x1: Stator reactance in ohms. It must be a complex number.
    - xm: Magnetizing reactance in ohms. It must be a complex number.
    """
    return (xm.imag/(sqrt(r1**2 + (x1.imag + xm.imag)**2))) * phase_voltage


def thevenin_impedance(r1: float, x1: complex, xm: complex) -> complex:
    """
    Returns the Thevenin impedance as a complex number (R+jX) in ohms.

    Args:
    - r1: Stator resistance in ohms.
    - x1: Stator reactance in ohms. It must be a complex number.
    - xm: Magnetizing reactance in ohms. It must be a complex number.
    """
    return (xm * (r1 + x1)) / (r1 + x1 + xm)


def torque_induced(v_th: float, r_th: float, x_th: float, r2: float, x2: complex, sync_velocity: float, slip: float) -> float:
    """
    Returns the induced torque in Nm as a function of the slip.

    Args:
    - v_th: Thevenin voltage in volts.
    - r_th: Thevenin resistance in ohms.
    - x_th: Thevenin reactance in ohms.
    - r2: Rotor resistance in ohms.
    - x2: Rotor reactance in ohms. It must be a complex number.
    - sync_velocity : motor synchronous velocity. It must be in rad/s.
    - slip: Motor slip. slip=1 if the motor is at startup.
    """
    return (3 * v_th**2 * (r2/slip)) / (sync_velocity * ((r_th + (r2/slip))**2 + (x_th + x2.imag)**2))


def max_slip_at_max_torque(r_th: float, x_th: float, r2: float, x2: complex) -> float:
    """
    Returns the slip (s_max) at the maximum induced torque.

    Args:
    - r_th: Thevenin resistance in ohms.
    - x_th: Thevenin reactance in ohms.
    - r2: Rotor resistance in ohms.
    - x2: Rotor reactance in ohms. It must be a complex number.
    """
    return r2 / (sqrt(r_th**2 + (x_th + x2.imag)**2))


def max_torque_induced(v_th: float, r_th: float, x_th: float, x2: complex, sync_velocity: float) -> float:
    """
    Returns the maximum induced torque in Nm.

    Args:
    - v_th: Thevenin voltage in volts.
    - r_th: Thevenin resistance in ohms.
    - x_th: Thevenin reactance in ohms.
    - x2: Rotor reactance in ohms. It must be a complex number.
    - sync_velocity : motor synchronous velocity. It must be in rad/s.
    """
    return (3 * v_th**2) / (2*sync_velocity * (r_th + sqrt(r_th**2 + (x_th+x2.imag)**2)))
