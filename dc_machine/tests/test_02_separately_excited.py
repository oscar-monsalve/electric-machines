import pytest
from separately_excited import SeparatelyExcitedMotorGenerator
from utils import rpm_to_rad_s


def make_machine(mode: str = "motor", brush_drop_voltage: float | None = None) -> SeparatelyExcitedMotorGenerator:
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

def test_field_current():
    m = make_machine()
    external_dc_field_voltage = 100.0
    m.field_current(external_dc_field_voltage) == pytest.approx(1.0)

def test_armature_current_motor_without_brush_drop():
    m = make_machine(mode="motor", brush_drop_voltage=None)
    # Ia = (Vt - E - Vb)/Ra = (220 - 1500 - 0)/2 = -640
    ia = m.armature_current(terminal_voltage=220, induced_emf=1500)
    ia == pytest.approx(-640.0)

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
