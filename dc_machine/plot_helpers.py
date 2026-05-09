"""Plotting helpers for educational DC-machine characteristic curves.

The public data helpers compute characteristic data from stable machine APIs.
The public plot helpers render already computed data with a small, consistent
matplotlib style. Axis values are automatically scaled to kilo-units when the
largest absolute plotted value on that axis is at least ``1000``.
"""

import matplotlib.pyplot as plt
from collections.abc import Sequence
from .separately_excited import SeparatelyExcitedMotorGenerator
from .utils import rpm_to_rad_s


ENGINEERING_SCALE_THRESHOLD = 1000.0
KILO_SCALE_FACTOR = 1000.0


# Generator characteristic curves: terminal voltage and terminal power vs. armature current.

def generator_terminal_voltage_characteristic_data(
    machine: SeparatelyExcitedMotorGenerator,
    armature_current_points: Sequence[float],
    applied_field_voltage: float,
    field_adjusting_resistance: float = 0.0,
    desired_speed_rpm: float | None = None,
    include_armature_reaction: bool = False,
) -> tuple[list[float], list[float]]:
    """Returns generator terminal-voltage characteristic data.

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
        ValueError: if the selected armature-reaction model requirements are not configured.
    """
    if machine.operation_mode != "generator":
        raise ValueError("generator_terminal_voltage_characteristic_data requires a machine in generator mode.")

    armature_current_values = _validate_non_negative_monotonic_points(
        points=armature_current_points,
        variable_name="armature_current_points"
    )

    terminal_voltage_values: list[float] = []

    for armature_current in armature_current_values:
        if include_armature_reaction:
            terminal_voltage = machine.terminal_voltage_from_field_voltage_with_armature_reaction(
                armature_current=armature_current,
                applied_field_voltage=applied_field_voltage,
                field_adjusting_resistance=field_adjusting_resistance,
                desired_speed_rpm=desired_speed_rpm
            )
        else:
            terminal_voltage = machine.terminal_voltage_from_field_voltage(
                armature_current=armature_current,
                applied_field_voltage=applied_field_voltage,
                field_adjusting_resistance=field_adjusting_resistance,
                desired_speed_rpm=desired_speed_rpm
            )
        terminal_voltage_values.append(terminal_voltage)

    return armature_current_values, terminal_voltage_values

def generator_terminal_power_characteristic_data(
    machine: SeparatelyExcitedMotorGenerator,
    armature_current_points: Sequence[float],
    applied_field_voltage: float,
    field_adjusting_resistance: float = 0.0,
    desired_speed_rpm: float | None = None,
    include_armature_reaction: bool = False,
) -> tuple[list[float], list[float]]:
    """Returns generator terminal-power characteristic data for fixed excitation and speed.

    The returned characteristic is:
        - x-axis: armature current ``I_A``
        - y-axis: terminal electrical power ``P_T = V_T * I_A``

    Terminal voltage values are first computed with
    ``generator_terminal_voltage_characteristic_data(...)``. Power is then
    calculated from the armature-side terminal output relation ``P_T = V_T * I_A``.

    Args:
        machine: separately excited DC machine configured in generator mode.
        armature_current_points: sweep points for armature current, in amps.
        applied_field_voltage: external DC field voltage, in volts.
        field_adjusting_resistance: external field-adjusting resistance, in ohms.
        desired_speed_rpm: shaft speed at which the characteristic is evaluated, in rpm.
        include_armature_reaction: whether to use the nonlinear fixed armature-reaction model.

    Returns:
        A tuple ``(armature_current_values, terminal_power_values)``. Power is in watts.

    Raises:
        ValueError: if the machine is not in generator mode.
        ValueError: if ``armature_current_points`` is empty.
        ValueError: if any armature-current point is negative.
        ValueError: if ``armature_current_points`` is not monotonic non-decreasing.
        ValueError: if the selected armature-reaction model requirements are not configured.
    """
    armature_current_values, terminal_voltage_values = generator_terminal_voltage_characteristic_data(
        machine=machine,
        armature_current_points=armature_current_points,
        applied_field_voltage=applied_field_voltage,
        field_adjusting_resistance=field_adjusting_resistance,
        desired_speed_rpm=desired_speed_rpm,
        include_armature_reaction=include_armature_reaction,
    )

    terminal_power_values = [
        machine.armature_terminal_power(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current
        )
        for armature_current, terminal_voltage in zip(
            armature_current_values, terminal_voltage_values
        )
    ]

    return armature_current_values, terminal_power_values

def plot_generator_terminal_voltage_characteristic(
    armature_current_points: Sequence[float],
    terminal_voltage_points: Sequence[float],
    *,
    ax=None,
    label: str | None = None,
    title: str | None = None
):
    """Plots terminal voltage versus armature current for a DC generator.

    If either axis reaches at least ``1000`` in absolute value, the plotted axis
    values are scaled by ``1000`` and the axis label receives the ``k`` prefix.

    Args:
        armature_current_points: armature-current values in amps.
        terminal_voltage_points: terminal-voltage values in volts.
        ax: optional matplotlib axes. If omitted, a new figure and axes are created.
        label: optional curve label.
        title: optional plot title.

    Returns:
        Tuple ``(fig, ax)`` for the created or reused figure and axes.

    Raises:
        ValueError: if the x and y data lengths do not match.
        ValueError: if either data sequence is empty.
        ValueError: if reused axes already use a different engineering scale.
    """
    return _plot_characteristic(
        x_values=armature_current_points,
        y_values=terminal_voltage_points,
        x_quantity="Armature current",
        x_symbol="$I_A$",
        x_unit="A",
        y_quantity="Terminal voltage",
        y_symbol="$V_T$",
        y_unit="V",
        ax=ax,
        label=label,
        title=title,
    )

def plot_generator_terminal_power_characteristic(
    armature_current_points: Sequence[float],
    terminal_power_points: Sequence[float],
    *,
    ax=None,
    label: str | None = None,
    title: str | None = None,
):
    """Plots terminal output power versus armature current for a DC generator.

    If either axis reaches at least ``1000`` in absolute value, the plotted axis
    values are scaled by ``1000`` and the axis label receives the ``k`` prefix.

    Args:
        armature_current_points: armature-current values in amps.
        terminal_power_points: terminal-power values in watts.
        ax: optional matplotlib axes. If omitted, a new figure and axes are created.
        label: optional curve label.
        title: optional plot title.

    Returns:
        Tuple ``(fig, ax)`` for the created or reused figure and axes.

    Raises:
        ValueError: if the x and y data lengths do not match.
        ValueError: if either data sequence is empty.
        ValueError: if reused axes already use a different engineering scale.
    """
    return _plot_characteristic(
        x_values=armature_current_points,
        y_values=terminal_power_points,
        x_quantity="Armature current",
        x_symbol="$I_A$",
        x_unit="A",
        y_quantity="Terminal power",
        y_symbol="$P_T$",
        y_unit="W",
        ax=ax,
        label=label,
        title=title,
    )

# Motor characteristic plot helpers can be added here after their public APIs stabilize.

def motor_torque_speed_characteristic_data(
    machine: SeparatelyExcitedMotorGenerator,
    armature_current_points: Sequence[float],
    terminal_voltage: float,
    applied_field_voltage: float,
    field_adjusting_resistance: float = 0.0,
    include_armature_reaction: bool = False,
) -> tuple[list[float], list[float]]:
    """Returns OCC-based motor torque-speed characteristic data.

    The returned characteristic is:
         - x-axis: induced torque ``T_ind``
         - y-axis: shaft speed ``n_m``

    This helper is intentionally OCC-based. It requires a magnetization curve and
    solves each operating-point speed from the field-voltage excitation and
    terminal conditions. It does not fall back to the analytic EMF model.

    For each armature-current point without armature reaction:
        1. solve speed from ``shaft_speed_rpm_from_field_voltage(...)``
        2. solve induced EMF from ``induced_emf_from_terminal_conditions(...)``
        3. compute torque from ``T_ind = E_A * I_A / omega``

    When ``include_armature_reaction`` is true, the same terminal-condition EMF
    is used, but the speed is solved from the OCC at the equivalent field current
    after fixed demagnetizing armature reaction.

    Args:
        machine: separately excited DC machine configured in motor mode with a magnetization curve.
        armature_current_points: sweep points for armature current, in amps.
        terminal_voltage: motor terminal voltage, in volts.
        applied_field_voltage: external DC field voltage, in volts.
        field_adjusting_resistance: external field-adjusting resistance, in ohms.
        include_armature_reaction: whether to use the nonlinear fixed armature-reaction model.

    Returns:
        A tuple ``(torque_values, speed_rpm_values)``.

    Raises:
        ValueError: if the machine is not in motor mode.
        ValueError: if the machine does not have a magnetization curve.
        ValueError: if ``armature_current_points`` is empty.
        ValueError: if any armature-current point is negative.
        ValueError: if ``armature_current_points`` is not monotonic non-decreasing.
        ValueError: if the selected armature-reaction model requirements are not configured.
        ValueError: if a solved speed is not positive.
    """
    if machine.operation_mode != "motor":
        raise ValueError("motor_torque_speed_characteristic_data requires a machine in motor mode.")

    if not machine.has_magnetization_curve():
        raise ValueError("motor_torque_speed_characteristic_data requires a magnetization curve.")

    armature_current_values = _validate_non_negative_monotonic_points(
        points=armature_current_points,
        variable_name="armature_current_points",
    )

    torque_values: list[float] = []
    speed_rpm_values: list[float] = []

    for armature_current in armature_current_values:
        induced_emf = machine.induced_emf_from_terminal_conditions(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current
        )

        if include_armature_reaction:
            reference_speed_rpm = machine.magnetization_curve.reference_speed_rpm
            equivalent_field_current = machine.equivalent_field_current_with_armature_reaction(
                applied_field_voltage=applied_field_voltage,
                field_adjusting_resistance=field_adjusting_resistance,
            )
            reference_emf = machine.induced_emf_from_equivalent_field_current(
                equivalent_field_current=equivalent_field_current,
                desired_speed_rpm=reference_speed_rpm,
            )

            if reference_emf == 0:
                raise ValueError("Cannot solve motor speed: OCC gives zero emf at the equivalent field current.")

            speed_rpm = induced_emf * (reference_speed_rpm / reference_emf)
        else:
            speed_rpm = machine.shaft_speed_rpm_from_field_voltage(
                terminal_voltage=terminal_voltage,
                armature_current=armature_current,
                applied_field_voltage=applied_field_voltage,
                field_adjusting_resistance=field_adjusting_resistance
            )

        if speed_rpm <= 0:
            raise ValueError("Solved motor speed must be positive when computing torque.")

        torque = (induced_emf * armature_current) / rpm_to_rad_s(speed_rpm)

        torque_values.append(torque)
        speed_rpm_values.append(speed_rpm)

    return torque_values, speed_rpm_values


def motor_torque_current_characteristic_data(
    machine: SeparatelyExcitedMotorGenerator,
    armature_current_points: Sequence[float],
    terminal_voltage: float,
    applied_field_voltage: float,
    field_adjusting_resistance: float = 0.0,
    include_armature_reaction: bool = False,
) -> tuple[list[float], list[float]]:
    """Returns OCC-based motor torque-current characteristic data.

    The returned characteristic is:
        - x-axis: induced torque ``T_ind``
        - y-axis: armature current ``I_A``

    This helper reuses ``motor_torque_speed_characteristic_data(...)`` so torque
    is computed consistently from the same OCC-based operating-point solution.

    Args:
        machine: separately excited DC machine configured in motor mode with a magnetization curve.
        armature_current_points: sweep points for armature current, in amps.
        terminal_voltage: motor terminal voltage, in volts.
        applied_field_voltage: external DC field voltage, in volts.
        field_adjusting_resistance: external field-adjusting resistance, in ohms.
        include_armature_reaction: whether to use the nonlinear fixed armature-reaction model.

    Returns:
        A tuple ``(torque_values, armature_current_values)``.

    Raises:
        ValueError: if the machine is not in motor mode.
        ValueError: if the machine does not have a magnetization curve.
        ValueError: if ``armature_current_points`` is empty.
        ValueError: if any armature-current point is negative.
        ValueError: if ``armature_current_points`` is not monotonic non-decreasing.
        ValueError: if the selected armature-reaction model requirements are not configured.
        ValueError: if a solved speed is not positive.
    """
    torque_values, _ = motor_torque_speed_characteristic_data(
        machine=machine,
        armature_current_points=armature_current_points,
        terminal_voltage=terminal_voltage,
        applied_field_voltage=applied_field_voltage,
        field_adjusting_resistance=field_adjusting_resistance,
        include_armature_reaction=include_armature_reaction,
    )

    armature_current_values = list(armature_current_points)

    return torque_values, armature_current_values

def plot_motor_torque_speed_characteristic(
    torque_points: Sequence[float],
    speed_points: Sequence[float],
    *,
    ax=None,
    label: str | None = None,
    title: str | None = None,
):
    """Plots shaft speed versus induced torque for a DC motor.

    If either axis reaches at least ``1000`` in absolute value, the plotted axis
    values are scaled by ``1000`` and the axis label receives the ``k`` prefix.

    Args:
        torque_points: induced-torque values in N·m.
        speed_points: shaft-speed values in rpm.
        ax: optional matplotlib axes. If omitted, a new figure and axes are created.
        label: optional curve label.
        title: optional plot title.

    Returns:
        Tuple ``(fig, ax)`` for the created or reused figure and axes.

    Raises:
        ValueError: if the x and y data lengths do not match.
        ValueError: if either data sequence is empty.
        ValueError: if reused axes already use a different engineering scale.
    """
    return _plot_characteristic(
        x_values=torque_points,
        y_values=speed_points,
        x_quantity="Torque",
        x_symbol="$T_{ind}$",
        x_unit="N·m",
        y_quantity="Speed",
        y_symbol="$n_m$",
        y_unit="rpm",
        ax=ax,
        label=label,
        title=title,
    )

def plot_motor_torque_current_characteristic(
    torque_points: Sequence[float],
    armature_current_points: Sequence[float],
    *,
    ax=None,
    label: str | None = None,
    title: str | None = None,
):
    """Plots armature current versus induced torque for a DC motor.

    If either axis reaches at least ``1000`` in absolute value, the plotted axis
    values are scaled by ``1000`` and the axis label receives the ``k`` prefix.

    Args:
        torque_points: induced-torque values in N·m.
        armature_current_points: armature-current values in amps.
        ax: optional matplotlib axes. If omitted, a new figure and axes are created.
        label: optional curve label.
        title: optional plot title.

    Returns:
        Tuple ``(fig, ax)`` for the created or reused figure and axes.

    Raises:
        ValueError: if the x and y data lengths do not match.
        ValueError: if either data sequence is empty.
        ValueError: if reused axes already use a different engineering scale.
    """
    return _plot_characteristic(
        x_values=torque_points,
        y_values=armature_current_points,
        x_quantity="Torque",
        x_symbol="$T_{ind}$",
        x_unit="N·m",
        y_quantity="Armature current",
        y_symbol="$I_A$",
        y_unit="A",
        ax=ax,
        label=label,
        title=title,
    )

# Private helpers

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

def _engineering_scale(values: Sequence[float]) -> tuple[float, str]:
    """Returns the engineering scale factor and prefix for a plotted axis."""
    if not values:
        raise ValueError("Plot data must contain at least one point.")

    max_abs_value = max(abs(value) for value in values)

    if max_abs_value >= ENGINEERING_SCALE_THRESHOLD:
        return KILO_SCALE_FACTOR, "k"

    return 1.0, ""

def _format_axis_label(quantity: str, symbol: str, unit: str, prefix: str) -> str:
    """Formats an axis label with an optional engineering prefix."""
    return f"{quantity}, {symbol} ({prefix}{unit})"


def _axis_scale_from_values(ax, axis_name: str, values: Sequence[float]) -> tuple[float, str]:
    """Returns or stores the engineering scale used by a reused matplotlib axis."""
    scale_attr = f"_dc_machine_{axis_name}_scale_factor"
    prefix_attr = f"_dc_machine_{axis_name}_prefix"
    scale_factor, prefix = _engineering_scale(values)

    if hasattr(ax, scale_attr):
        existing_scale_factor = getattr(ax, scale_attr)
        existing_prefix = getattr(ax, prefix_attr)

        if existing_scale_factor != scale_factor:
            raise ValueError(
                f"Existing axes use {existing_prefix or 'base'} units on the {axis_name}-axis; "
                f"new data would require {prefix or 'base'} units. Create a new axes for this curve."
            )

        return existing_scale_factor, existing_prefix

    setattr(ax, scale_attr, scale_factor)
    setattr(ax, prefix_attr, prefix)

    return scale_factor, prefix

def _plot_characteristic(
    x_values: Sequence[float],
    y_values: Sequence[float],
    *,
    x_quantity: str,
    x_symbol: str,
    x_unit: str,
    y_quantity: str,
    y_symbol: str,
    y_unit: str,
    ax=None,
    label: str | None = None,
    title: str | None = None,
):
    """Plots one characteristic curve with the module's default educational style.

    The first curve plotted on an axes determines the engineering scale for that
    axes. Later curves plotted on the same axes must use the same scale so that
    overlaid data remain visually consistent.
    """
    x_values = list(x_values)
    y_values = list(y_values)

    if len(x_values) != len(y_values):
        raise ValueError("x_values and y_values must have the same length.")

    if ax is None:
        fig, ax = plt.subplots(figsize=(7.0, 4.8))
    else:
        fig = ax.figure

    x_scale_factor, x_prefix = _axis_scale_from_values(ax, axis_name="x", values=x_values)
    y_scale_factor, y_prefix = _axis_scale_from_values(ax, axis_name="y", values=y_values)

    x_plot_values = [value / x_scale_factor for value in x_values]
    y_plot_values = [value / y_scale_factor for value in y_values]

    title_fontsize = 16.0
    label_fontsize = 14.0
    tick_labelsize = 12.0
    legend_fontsize = 12.0

    ax.plot(x_plot_values, y_plot_values, linewidth=2.0, label=label)

    ax.set_xlabel(
        _format_axis_label(x_quantity, x_symbol, x_unit, x_prefix),
        fontsize=label_fontsize,
    )
    ax.set_ylabel(
        _format_axis_label(y_quantity, y_symbol, y_unit, y_prefix),
        fontsize=label_fontsize,
    )

    if title is not None:
        ax.set_title(title, fontsize=title_fontsize)

    ax.tick_params(axis="both", labelsize=tick_labelsize)

    ax.grid(True, which="major", linewidth=0.8, alpha=0.8)
    ax.minorticks_on()
    ax.grid(True, which="minor", linewidth=0.4, alpha=0.35)

    if label is not None:
        ax.legend(frameon=True, fontsize=legend_fontsize)

    fig.tight_layout()

    return fig, ax
