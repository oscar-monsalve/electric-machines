from math import pi


def power_to_watts(active_power: float, unit: str) -> float:
    """Calculates the active power in watts (W) from hp or cv.
    Args:
        active_power: power in horse power (hp).
        unit: either "watts", or "hp", or "cv".

    Returns:
        The active power in watts (W) from horse power (hp) or CV.
    """
    ONE_HP_IN_WATTS = 745.7
    ONE_CV_IN_WATTS = 735.5
    valid_units: list(str) = ("watts", "hp", "cv")

    match unit:
        case "watts":
            return active_power
        case "hp":
            return active_power * ONE_HP_IN_WATTS
        case "cv":
            return active_power * ONE_CV_IN_WATTS
        case _:
            raise ValueError(f"Provide one of the following active power units: {valid_units}")

def rpm_to_rad_s(speed: float) -> float:
    """Converts shaft speed units to rad/s from rpm.

    Args:
        speed: shaft speed in rpm.

    Returns:
        The shaft speed in rad/s.
    """
    return speed * (2 * pi / 60)

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
