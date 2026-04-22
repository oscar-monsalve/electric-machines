import pytest
from dc_machine.magnetization import MagnetizationCurve
from dc_machine.separately_excited import SeparatelyExcitedMotorGenerator
from dc_machine.utils import rpm_to_rad_s


# ----------------------------
# Factories
# ----------------------------

def make_machine(
    mode: str = "motor",
    brush_drop_voltage: float | None = None
) -> SeparatelyExcitedMotorGenerator:
    return SeparatelyExcitedMotorGenerator(
        armature_resistance=2.0,
        nominal_voltage=220.0,
        speed_rpm=1500.0,
        flux=1.0,
        k_constant=1.0,
        operation_mode=mode,
        shunt_resistance=100.0,
        brush_drop_voltage=brush_drop_voltage,
    )

def make_curve() -> MagnetizationCurve:
    return MagnetizationCurve(
        field_current_points=[0.0, 1.0, 2.0],
        emf_points=[10.0, 50.0, 90.0],
        reference_speed_rpm=1000.0,
    )

def make_machine_with_curve(mode: str = "generator") -> SeparatelyExcitedMotorGenerator:
    return SeparatelyExcitedMotorGenerator(
        armature_resistance=2.0,
        nominal_voltage=220.0,
        speed_rpm=1000.0,
        operation_mode=mode,
        shunt_resistance=100.0,
        magnetization_curve=make_curve(),
    )

def make_machine_with_analytic_model(mode: str = "generator") -> SeparatelyExcitedMotorGenerator:
    return SeparatelyExcitedMotorGenerator(
        armature_resistance=2.0,
        nominal_voltage=220.0,
        speed_rpm=1000.0,
        operation_mode=mode,
        shunt_resistance=100.0,
        flux=1.0,
        k_constant=1.0,
    )

def make_machine_without_emf_model(mode: str = "generator") -> SeparatelyExcitedMotorGenerator:
    return SeparatelyExcitedMotorGenerator(
        armature_resistance=2.0,
        nominal_voltage=220.0,
        speed_rpm=1000.0,
        operation_mode=mode,
        shunt_resistance=100.0,
    )

# ----------------------------
# Analytic model tests
# ----------------------------

def test_field_current():
    m = make_machine()
    external_dc_field_voltage = 100.0
    assert m.field_current(external_dc_field_voltage) == pytest.approx(1.0)

def test_armature_current_motor_without_brush_drop():
    m = make_machine(mode="motor", brush_drop_voltage=None)
    # Ia = (Vt - E - Vb)/Ra = (220 - 1500 - 0)/2 = -640
    ia = m.armature_current(terminal_voltage=220, induced_emf=1500)
    assert ia == pytest.approx(-640.0)

def test_armature_current_motor_with_brush_drop():
    m = make_machine(mode="motor", brush_drop_voltage=2.0)
    # Ia = (220 - 1500 - 2)/2 = -641
    ia = m.armature_current(terminal_voltage=220.0, induced_emf=1500.0)
    assert ia == pytest.approx(-641.0)

def test_armature_current_generator_with_brush_drop():
    m = make_machine(mode="generator", brush_drop_voltage=2.0)
    # Ia = (E - Vt - Vb)/Ra = (1500 - 220 - 2)/2 = 639
    ia = m.armature_current(terminal_voltage=220.0, induced_emf=1500.0)
    assert ia == pytest.approx(639.0)

def test_terminal_voltage_motor_with_brush_drop():
    m = make_machine(mode="motor", brush_drop_voltage=2.0)
    # Vt = Vnom - Ia*Ra - Vb = 220 - 10*2 - 2 = 198
    vt = m.terminal_voltage(armature_current=10.0)
    assert vt == pytest.approx(198.0)

def test_terminal_voltage_generator_with_brush_drop():
    m = make_machine(mode="generator", brush_drop_voltage=2.0)
    # E = K*flux*n = 1500
    # Vt = E - Ia*Ra - Vb = 1500 - 10*2 - 2 = 1478
    vt = m.terminal_voltage(armature_current=10.0)
    assert vt == pytest.approx(1478.0)

def test_induced_torque():
    m = make_machine(mode="motor")
    ia = 10.0
    expected = (m.induced_emf() * ia) / rpm_to_rad_s(m.speed_rpm)
    assert m.induced_torque(ia) == pytest.approx(expected)

def test_shaft_speed_rpm_motor_with_brush_drop():
    m = make_machine(mode="motor", brush_drop_voltage=2.0)
    # n = (Vt - Ia*Ra - Vb)/(K*flux)
    n = m.shaft_speed_rpm(terminal_voltage=220.0, armature_current=10.0)
    assert n == pytest.approx(198.0)

def test_shaft_speed_rpm_generator_with_brush_drop():
    m = make_machine(mode="generator", brush_drop_voltage=2.0)
    # n = (Vt + Ia*Ra + Vb)/(K*flux)
    n = m.shaft_speed_rpm(terminal_voltage=220.0, armature_current=10.0)
    assert n == pytest.approx(242.0)

def test_negative_brush_drop_raises():
    with pytest.raises(ValueError):
        make_machine(brush_drop_voltage=-0.1)

# ----------------------------
# Magnetization curve tests
# ----------------------------

def test_induced_emf_from_field_voltage_uses_magnetization_curve():
    machine = make_machine_with_curve()
    emf = machine.induced_emf_from_field_voltage(applied_field_voltage=100.0)
    assert emf == pytest.approx(50.0)

def test_induced_emf_from_field_voltage_scales_curve_with_speed():
    machine = SeparatelyExcitedMotorGenerator(
        armature_resistance=2.0,
        nominal_voltage=220.0,
        speed_rpm=2000.0,
        operation_mode="generator",
        shunt_resistance=100.0,
        magnetization_curve=make_curve(),
    )
    emf = machine.induced_emf_from_field_voltage(applied_field_voltage=100.0)
    assert emf == pytest.approx(100.0)

def test_induced_emf_from_field_voltage_falls_back_to_analytic_model():
    machine = make_machine_with_analytic_model()
    emf = machine.induced_emf_from_field_voltage(applied_field_voltage=100.0)
    assert emf == pytest.approx(machine.induced_emf())

def test_induced_emf_from_field_voltage_prefers_curve_over_analytic_model():
    machine = SeparatelyExcitedMotorGenerator(
        armature_resistance=2.0,
        nominal_voltage=220.0,
        speed_rpm=1000.0,
        operation_mode="generator",
        shunt_resistance=100.0,
        flux=1.0,
        k_constant=1.0,
        magnetization_curve=make_curve(),
    )
    emf = machine.induced_emf_from_field_voltage(applied_field_voltage=100.0)
    assert emf == pytest.approx(50.0)

def test_induced_emf_from_field_voltage_raises_without_any_emf_model():
    machine = make_machine_without_emf_model()
    with pytest.raises(ValueError, match="provide either magnetization_curve or both flux and k_constant"):
        machine.induced_emf_from_field_voltage(applied_field_voltage=100.0)

def test_field_voltage_from_emf_uses_magnetization_curve_inverse():
    machine = make_machine_with_curve()
    field_voltage = machine.field_voltage_from_emf(emf=50.0)
    assert field_voltage == pytest.approx(100.0)

def test_field_voltage_from_emf_raises_without_magnetization_curve():
    machine = make_machine_with_analytic_model()
    with pytest.raises(ValueError, match="requires a magnetization curve"):
        machine.field_voltage_from_emf(emf=50.0)

def test_terminal_voltage_from_emf_generator_uses_operating_point_emf():
    machine = make_machine_with_curve(mode="generator")
    vt = machine.terminal_voltage_from_emf(
        armature_current=10.0,
        induced_emf=50.0,
    )
    assert vt == pytest.approx(30.0)

def test_terminal_voltage_from_field_voltage_uses_magnetization_curve():
    machine = make_machine_with_curve(mode="generator")
    vt = machine.terminal_voltage_from_field_voltage(
        armature_current=10.0,
        applied_field_voltage=100.0,
    )
    assert vt == pytest.approx(30.0)

def test_terminal_voltage_from_field_voltage_falls_back_to_analytic_model():
    machine = make_machine_with_analytic_model(mode="generator")
    vt = machine.terminal_voltage_from_field_voltage(
        armature_current=10.0,
        applied_field_voltage=100.0,
    )
    expected = machine.induced_emf() - (10.0 * machine.armature_resistance)
    assert vt == pytest.approx(expected)

def test_induced_torque_from_emf_uses_operating_point_emf():
    machine = make_machine_with_curve()
    ia = 10.0
    induced_emf = 50.0
    expected = (induced_emf * ia) / rpm_to_rad_s(machine.speed_rpm)

    assert machine.induced_torque_from_emf(
        armature_current=ia,
        induced_emf=induced_emf,
    ) == pytest.approx(expected)


def test_induced_torque_from_field_voltage_falls_back_to_analytic_model():
    machine = make_machine_with_analytic_model()
    ia = 10.0
    expected = (machine.induced_emf() * ia) / rpm_to_rad_s(machine.speed_rpm)

    assert machine.induced_torque_from_field_voltage(
        armature_current=ia,
        applied_field_voltage=100.0,
    ) == pytest.approx(expected)

def test_induced_torque_from_field_voltage_uses_magnetization_curve():
    machine = make_machine_with_curve()
    ia = 10.0
    expected_emf = 50.0
    expected = (expected_emf * ia) / rpm_to_rad_s(machine.speed_rpm)

    assert machine.induced_torque_from_field_voltage(
        armature_current=ia,
        applied_field_voltage=100.0,
    ) == pytest.approx(expected)

def test_shaft_speed_rpm_from_field_current_uses_magnetization_curve_generator():
    machine = make_machine_with_curve(mode="generator")
    # E = Vt + Ia*Ra + Vb = 60 + 10*2 + 0 = 80 V
    speed = machine.shaft_speed_rpm_from_field_current(
        terminal_voltage=60.0,
        armature_current=10.0,
        field_current=1.0,
    )
    # At If=1.0 A, reference EMF is 50 V at 1000 rpm, so speed = 80 * 1000 / 50 = 1600 rpm
    assert speed == pytest.approx(1600.0)

def test_shaft_speed_rpm_from_field_current_raises_without_magnetization_curve():
    machine = make_machine_with_analytic_model()
    with pytest.raises(ValueError, match="requires a magnetization curve"):
        machine.shaft_speed_rpm_from_field_current(
            terminal_voltage=60.0,
            armature_current=10.0,
            field_current=1.0,
        )

def test_shaft_speed_rpm_from_field_voltage_uses_magnetization_curve_generator():
    machine = make_machine_with_curve(mode="generator")

    speed = machine.shaft_speed_rpm_from_field_voltage(
        terminal_voltage=60.0,
        armature_current=10.0,
        applied_field_voltage=100.0,
    )

    assert speed == pytest.approx(1600.0)

def test_shaft_speed_rpm_from_field_voltage_raises_without_magnetization_curve():
    machine = make_machine_with_analytic_model()

    with pytest.raises(ValueError, match="requires a magnetization curve"):
        machine.shaft_speed_rpm_from_field_voltage(
            terminal_voltage=60.0,
            armature_current=10.0,
            applied_field_voltage=100.0,
        )
