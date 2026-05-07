import matplotlib.pyplot as plt
from collections.abc import Sequence
from .separately_excited import SeparatelyExcitedMotorGenerator


def _validate_non_negative_monotonic_points(points: Sequence[float], variable_name: str) -> list[float]:
    values = list(points)

    if not values:
        raise ValueError(f"{variable_name} must contain at least one point.")

    for value in values:
        if value < 0:
            raise ValueError(f"{variable_name} cannot contain negative values.")

    for idx, value in enumerate(values[:-1]):
        if value > values[idx + 1]:
            raise ValueError(f"{variable_name} must be monotonic non-decreasing.")

    return values

def generator_terminal_characteristic_data(
    machine: SeparatelyExcitedMotorGenerator,
    armature_current_points: Sequence[float],
    applied_field_voltage: float,
    field_adjusting_resistance: float = 0.0,
    desired_speed_rpm: float | None = None,
    include_armature_reaction: bool = False,
) -> tuple[list[float], list[float]]:
    """Returns generator terminal-characteristic data for a fixed excitation and speed.

    The returned characteristic is:
        - x-axis: armature current ``I_A``
        - y-axis: terminal voltage ``V_T``

    The machine must operate in generator mode. For the compensated / linear case,
    the helper uses ``terminal_voltage_from_field_voltage(...)``. For the fixed
    armature-reaction case, it uses
    ``terminal_voltage_from_field_voltage_with_armature_reaction(...)``.

    Args:
        machine: separately excited DC machine configured in generator mode.
        armature_current_points: sweep points for armature current, in amps.
        applied_field_voltage: external DC field voltage, in volts.
        field_adjusting_resistance: external field-adjusting resistance, in ohms.
        desired_speed_rpm: shaft speed at which the characteristic is evaluated, in rpm.
        include_armature_reaction: whether to use the nonlinear fixed armature-reaction model.

    Returns:
        A tuple ``(armature_current_values, terminal_voltage_values)``.

    Raises:
        ValueError: if the machine is not in generator mode.
        ValueError: if ``armature_current_points`` is empty.
        ValueError: if any armature-current point is negative.
        ValueError: if ``armature_current_points`` is not monotonic non-decreasing.
    """
