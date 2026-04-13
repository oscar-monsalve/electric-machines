from math import pi

def speed_regulation(speed_no_load: float, speed_full_load: float) -> float:
    """
    Calculates the machine's speed regulation as a percentage. Both velocities must have the same units.

    Args:
        speed_no_load: machine's shaft speed at no load in rad/s or rpm.
        speed_full_load: machine's shaft speed at full load in rad/s or rpm.

    Returns:
        The calculated speed regulation percentage.
    """

    if speed_full_load == 0:
        raise ValueError("Full-load speed cannot be zero.")
    elif speed_no_load == 0:
        raise ValueError("No-load speed cannot be zero.")

    return ((speed_no_load - speed_full_load) / speed_full_load) * 100

def rpm_to_rad_s(speed: float) -> float:
    """Converts shaft speed units to rad/s from rpm.

    Args:
        speed: shaft speed in rpm.

    Returns:
        The shaft speed in rad/s.
    """

    return speed * (2 * pi / 60)
