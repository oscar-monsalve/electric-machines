from dc_machine.magnetization import MagnetizationCurve
from dc_machine.plot_helpers import (
    generator_terminal_power_characteristic_data,
    generator_terminal_voltage_characteristic_data,
    motor_torque_current_characteristic_data,
    motor_torque_speed_characteristic_data,
    plot_motor_torque_current_characteristic,
    plot_motor_torque_speed_characteristic,
    plot_generator_terminal_power_characteristic,
    plot_generator_terminal_voltage_characteristic,
)
from dc_machine.separately_excited import SeparatelyExcitedMotorGenerator
from dc_machine.utils import rpm_to_rad_s

import matplotlib.pyplot as plt
import pytest
import matplotlib
matplotlib.use("Agg")


def make_curve() -> MagnetizationCurve:
    return MagnetizationCurve(
        field_current_points=[0.0, 1.0, 2.0],
        emf_points=[10.0, 50.0, 90.0],
        reference_speed_rpm=1000.0,
    )


def make_machine(
    mode: str = "generator",
    field_turns: float | None = None,
    armature_reaction_mmf: float | None = None,
) -> SeparatelyExcitedMotorGenerator:
    return SeparatelyExcitedMotorGenerator(
        armature_resistance=2.0,
        nominal_voltage=220.0,
        speed_rpm=1000.0,
        operation_mode=mode,
        shunt_resistance=100.0,
        magnetization_curve=make_curve(),
        field_turns=field_turns,
        armature_reaction_mmf=armature_reaction_mmf,
    )


def make_machine_without_curve(mode: str = "motor") -> SeparatelyExcitedMotorGenerator:
    return SeparatelyExcitedMotorGenerator(
        armature_resistance=2.0,
        nominal_voltage=220.0,
        speed_rpm=1000.0,
        operation_mode=mode,
        shunt_resistance=100.0,
        flux=1.0,
        k_constant=1.0,
    )


def test_generator_terminal_voltage_characteristic_data_rejects_motor_mode():
    machine = make_machine(mode="motor")

    with pytest.raises(ValueError, match="generator mode"):
        generator_terminal_voltage_characteristic_data(
            machine=machine,
            armature_current_points=[0.0, 10.0],
            applied_field_voltage=100.0,
        )


def test_generator_terminal_voltage_characteristic_data_rejects_empty_current_points():
    machine = make_machine()

    with pytest.raises(ValueError, match="at least one point"):
        generator_terminal_voltage_characteristic_data(
            machine=machine,
            armature_current_points=[],
            applied_field_voltage=100.0,
        )


def test_generator_terminal_voltage_characteristic_data_rejects_negative_current_points():
    machine = make_machine()

    with pytest.raises(ValueError, match="negative values"):
        generator_terminal_voltage_characteristic_data(
            machine=machine,
            armature_current_points=[0.0, -1.0],
            applied_field_voltage=100.0,
        )


def test_generator_terminal_voltage_characteristic_data_rejects_non_monotonic_current_points():
    machine = make_machine()

    with pytest.raises(ValueError, match="monotonic non-decreasing"):
        generator_terminal_voltage_characteristic_data(
            machine=machine,
            armature_current_points=[0.0, 20.0, 10.0],
            applied_field_voltage=100.0,
        )


def test_generator_terminal_voltage_characteristic_data_uses_compensated_occ_path():
    machine = make_machine()

    armature_current_points, terminal_voltage_points = generator_terminal_voltage_characteristic_data(
        machine=machine,
        armature_current_points=[0.0, 10.0],
        applied_field_voltage=100.0,
    )

    # If = 1 A, E = 50 V at 1000 rpm, Vt = E - Ia*Ra
    assert armature_current_points == [0.0, 10.0]
    assert terminal_voltage_points == pytest.approx([50.0, 30.0])


def test_generator_terminal_voltage_characteristic_data_uses_armature_reaction_path():
    machine = make_machine(field_turns=1000.0, armature_reaction_mmf=200.0)

    armature_current_points, terminal_voltage_points = generator_terminal_voltage_characteristic_data(
        machine=machine,
        armature_current_points=[0.0, 10.0],
        applied_field_voltage=100.0,
        include_armature_reaction=True,
    )

    # If = 1 A, If* = 0.8 A, E = 42 V at 1000 rpm, Vt = E - Ia*Ra
    assert armature_current_points == [0.0, 10.0]
    assert terminal_voltage_points == pytest.approx([42.0, 22.0])


def test_generator_terminal_power_characteristic_data_uses_compensated_voltage_data():
    machine = make_machine()

    armature_current_points, terminal_power_points = generator_terminal_power_characteristic_data(
        machine=machine,
        armature_current_points=[0.0, 10.0],
        applied_field_voltage=100.0,
    )

    # Vt = [50, 30], so Pt = Vt * Ia = [0, 300]
    assert armature_current_points == [0.0, 10.0]
    assert terminal_power_points == pytest.approx([0.0, 300.0])


def test_generator_terminal_power_characteristic_data_uses_armature_reaction_voltage_data():
    machine = make_machine(field_turns=1000.0, armature_reaction_mmf=200.0)

    armature_current_points, terminal_power_points = generator_terminal_power_characteristic_data(
        machine=machine,
        armature_current_points=[0.0, 10.0],
        applied_field_voltage=100.0,
        include_armature_reaction=True,
    )

    # Vt = [42, 22], so Pt = Vt * Ia = [0, 220]
    assert armature_current_points == [0.0, 10.0]
    assert terminal_power_points == pytest.approx([0.0, 220.0])


def test_plot_generator_terminal_voltage_characteristic_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="same length"):
        plot_generator_terminal_voltage_characteristic(
            armature_current_points=[0.0, 10.0],
            terminal_voltage_points=[50.0],
        )


def test_plot_generator_terminal_voltage_characteristic_returns_created_figure_and_axes():
    fig, ax = plot_generator_terminal_voltage_characteristic(
        armature_current_points=[0.0, 10.0],
        terminal_voltage_points=[50.0, 30.0],
        label="Compensated",
        title="Generator terminal characteristic",
    )

    assert fig is ax.figure
    assert ax.get_xlabel() == "Armature current, $I_A$ (A)"
    assert ax.get_ylabel() == "Terminal voltage, $V_T$ (V)"
    assert ax.get_title() == "Generator terminal characteristic"
    assert len(ax.lines) == 1

    plt.close(fig)


def test_plot_generator_terminal_voltage_characteristic_reuses_existing_axes():
    fig, ax = plt.subplots()

    returned_fig, returned_ax = plot_generator_terminal_voltage_characteristic(
        armature_current_points=[0.0, 10.0],
        terminal_voltage_points=[50.0, 30.0],
        ax=ax,
        label="Compensated",
    )

    assert returned_fig is fig
    assert returned_ax is ax
    assert len(ax.lines) == 1

    plt.close(fig)


def test_plot_generator_terminal_power_characteristic_returns_created_figure_and_axes():
    fig, ax = plot_generator_terminal_power_characteristic(
        armature_current_points=[0.0, 10.0],
        terminal_power_points=[0.0, 300.0],
        label="Compensated",
        title="Generator terminal power characteristic",
    )

    assert fig is ax.figure
    assert ax.get_xlabel() == "Armature current, $I_A$ (A)"
    assert ax.get_ylabel() == "Terminal power, $P_T$ (W)"
    assert ax.get_title() == "Generator terminal power characteristic"
    assert len(ax.lines) == 1

    plt.close(fig)


def test_plot_generator_terminal_power_characteristic_uses_kw_for_large_power_values():
    fig, ax = plot_generator_terminal_power_characteristic(
        armature_current_points=[0.0, 10.0],
        terminal_power_points=[0.0, 3000.0],
    )

    assert ax.get_ylabel() == "Terminal power, $P_T$ (kW)"
    assert list(ax.lines[0].get_ydata()) == pytest.approx([0.0, 3.0])

    plt.close(fig)


def test_plot_generator_terminal_voltage_characteristic_uses_kv_for_large_voltage_values():
    fig, ax = plot_generator_terminal_voltage_characteristic(
        armature_current_points=[0.0, 10.0],
        terminal_voltage_points=[1000.0, 2000.0],
    )

    assert ax.get_ylabel() == "Terminal voltage, $V_T$ (kV)"
    assert list(ax.lines[0].get_ydata()) == pytest.approx([1.0, 2.0])

    plt.close(fig)


def test_plot_generator_terminal_voltage_characteristic_rejects_mixed_axis_scales_on_reused_axes():
    fig, ax = plot_generator_terminal_voltage_characteristic(
        armature_current_points=[0.0, 10.0],
        terminal_voltage_points=[50.0, 30.0],
    )

    with pytest.raises(ValueError, match="Existing axes use base units"):
        plot_generator_terminal_voltage_characteristic(
            armature_current_points=[0.0, 10.0],
            terminal_voltage_points=[1000.0, 2000.0],
            ax=ax,
        )

    plt.close(fig)


def test_motor_torque_speed_characteristic_data_rejects_generator_mode():
    machine = make_machine(mode="generator")

    with pytest.raises(ValueError, match="motor mode"):
        motor_torque_speed_characteristic_data(
            machine=machine,
            armature_current_points=[0.0, 10.0],
            terminal_voltage=100.0,
            applied_field_voltage=100.0,
        )


def test_motor_torque_speed_characteristic_data_requires_magnetization_curve():
    machine = make_machine_without_curve(mode="motor")

    with pytest.raises(ValueError, match="magnetization curve"):
        motor_torque_speed_characteristic_data(
            machine=machine,
            armature_current_points=[0.0, 10.0],
            terminal_voltage=100.0,
            applied_field_voltage=100.0,
        )


def test_motor_torque_speed_characteristic_data_uses_occ_speed_solution():
    machine = make_machine(mode="motor")

    torque_points, speed_points = motor_torque_speed_characteristic_data(
        machine=machine,
        armature_current_points=[0.0, 10.0],
        terminal_voltage=100.0,
        applied_field_voltage=100.0,
    )

    # If = 1 A, E_ref = 50 V at 1000 rpm.
    # Ia = 0 A: E = 100 V, n = 2000 rpm, T = 0.
    # Ia = 10 A: E = 80 V, n = 1600 rpm, T = E*Ia/omega.
    assert speed_points == pytest.approx([2000.0, 1600.0])
    assert torque_points == pytest.approx([0.0, 800.0 / rpm_to_rad_s(1600.0)])


def test_motor_torque_speed_characteristic_data_uses_armature_reaction_path():
    machine = make_machine(mode="motor", field_turns=1000.0, armature_reaction_mmf=200.0)

    torque_points, speed_points = motor_torque_speed_characteristic_data(
        machine=machine,
        armature_current_points=[0.0, 10.0],
        terminal_voltage=100.0,
        applied_field_voltage=100.0,
        include_armature_reaction=True,
    )

    # If = 1 A, If* = 0.8 A, E_ref = 42 V at 1000 rpm.
    expected_speed_at_load = 80.0 * (1000.0 / 42.0)
    assert speed_points == pytest.approx([100.0 * (1000.0 / 42.0), expected_speed_at_load])
    assert torque_points == pytest.approx([0.0, 800.0 / rpm_to_rad_s(expected_speed_at_load)])


def test_motor_torque_current_characteristic_data_reuses_torque_solution():
    machine = make_machine(mode="motor")

    torque_points, current_points = motor_torque_current_characteristic_data(
        machine=machine,
        armature_current_points=[0.0, 10.0],
        terminal_voltage=100.0,
        applied_field_voltage=100.0,
    )

    assert current_points == [0.0, 10.0]
    assert torque_points == pytest.approx([0.0, 800.0 / rpm_to_rad_s(1600.0)])


def test_plot_motor_torque_speed_characteristic_returns_created_figure_and_axes():
    fig, ax = plot_motor_torque_speed_characteristic(
        torque_points=[0.0, 5.0],
        speed_points=[2000.0, 1600.0],
        title="Motor torque-speed characteristic",
    )

    assert fig is ax.figure
    assert ax.get_xlabel() == "Torque, $T_{ind}$ (N·m)"
    assert ax.get_ylabel() == "Speed, $n_m$ (krpm)"
    assert ax.get_title() == "Motor torque-speed characteristic"

    plt.close(fig)


def test_plot_motor_torque_current_characteristic_returns_created_figure_and_axes():
    fig, ax = plot_motor_torque_current_characteristic(
        torque_points=[0.0, 5.0],
        armature_current_points=[0.0, 10.0],
        title="Motor torque-current characteristic",
    )

    assert fig is ax.figure
    assert ax.get_xlabel() == "Torque, $T_{ind}$ (N·m)"
    assert ax.get_ylabel() == "Armature current, $I_A$ (A)"
    assert ax.get_title() == "Motor torque-current characteristic"

    plt.close(fig)
