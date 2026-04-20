import pytest
from dc_machine.base import DCMachine


# DCMachine is abstract, so it cannot be instantiated directly.
#   - Create a concrete subclass (DummyDCMachine) that implements all abstract methods with simple placeholders.
#   - Then it is possible to test only constructor behavior of the base class without involving real machine physics.
class DummyDCMachine(DCMachine):
    """Concrete test double to exercise DCMachine constructor validations."""

    def validate_resistance(self) -> None:
        pass

    def field_current(self, applied_field_voltage: float) -> float:
        return applied_field_voltage

    def armature_current(self, terminal_voltage: float, induced_emf: float) -> float:
        return terminal_voltage - induced_emf

    def terminal_voltage(self, armature_current: float) -> float:
        return self.nominal_voltage - armature_current * self.armature_resistance

    def induced_torque(self, armature_current: float) -> float:
        return armature_current

    def shaft_speed_rpm(
        self, terminal_voltage: float, armature_current: float
    ) -> float:
        return self.speed_rpm


def valid_kwargs() -> dict:
    return {
        "armature_resistance": 2.0,
        "nominal_voltage": 220.0,
        "speed_rpm": 1500.0,
        "flux": 1.0,
        "k_constant": 1.0,
        "operation_mode": "motor",
        "shunt_resistance": None,
        "series_resistance": None,
        "brush_drop_voltage": None,
    }


def test_constructor_accepts_valid_inputs():
    """
    - Verifies that a valid configuration builds successfully.
    - Confirms fields are stored correctly.
    - Checks brush_drop_voltage=None is normalized by _brush_drop_value() to 0.0.
    """
    m = DummyDCMachine(**valid_kwargs())

    assert m.armature_resistance == 2.0
    assert m.nominal_voltage == 220.0
    assert m.speed_rpm == 1500.0
    assert m.flux == 1.0
    assert m.k_constant == 1.0
    assert m.operation_mode == "motor"
    assert m.brush_drop_voltage is None
    assert m._brush_drop_value() == 0.0


# Use pytest.mark.parametrize to avoid repetitive test functions and ensure consistent coverage.
@pytest.mark.parametrize(
    "field,value,error_msg",
    [
        ("armature_resistance", 0.0, "Armature resistance"),
        ("armature_resistance", -1.0, "Armature resistance"),
        ("nominal_voltage", 0.0, "supply voltage"),
        ("nominal_voltage", -10.0, "supply voltage"),
        ("speed_rpm", 0.0, "speed"),
        ("speed_rpm", -100.0, "speed"),
    ],
)
def test_constructor_rejects_non_positive_base_fields(field, value, error_msg):
    """
    Covers all core scalar validations in one compact test:
    - armature_resistance > 0
    - nominal_voltage > 0
    - speed_rpm > 0
    """
    kwargs = valid_kwargs()
    kwargs[field] = value

    with pytest.raises(ValueError, match=error_msg):
        DummyDCMachine(**kwargs)


@pytest.mark.parametrize(
    "flux,k_constant,error_msg",
    [
        (None, 1.0, "Flux must be provided"),
        (1.0, None, "K constant must be provided"),
        (0.0, 1.0, "magnetic flux"),
        (-0.1, 1.0, "magnetic flux"),
        (1.0, 0.0, "K constant"),
        (1.0, -5.0, "K constant"),
    ],
)
def test_induced_emf_rejects_invalid_analytic_model(flux, k_constant, error_msg):
    kwargs = valid_kwargs()
    kwargs["flux"] = flux
    kwargs["k_constant"] = k_constant

    machine = DummyDCMachine(**kwargs)

    with pytest.raises(ValueError, match=error_msg):
        machine.induced_emf()


def test_constructor_rejects_invalid_operation_mode():
    """
    - Ensures mode must be one of ("motor", "generator").
    - Protects against typo-driven invalid states early.
    """
    kwargs = valid_kwargs()
    kwargs["operation_mode"] = "invalid-mode"

    with pytest.raises(ValueError, match="operation modes"):
        DummyDCMachine(**kwargs)


def test_constructor_rejects_negative_brush_drop():
    """ "Validates that brush drop (design rule), when provided, must be non-negative."""
    kwargs = valid_kwargs()
    kwargs["brush_drop_voltage"] = -0.1

    with pytest.raises(ValueError, match="brush drop voltage"):
        DummyDCMachine(**kwargs)


def test_constructor_accepts_zero_brush_drop():
    kwargs = valid_kwargs()
    kwargs["brush_drop_voltage"] = 0.0

    m = DummyDCMachine(**kwargs)
    assert m.brush_drop_voltage == 0.0
    assert m._brush_drop_value() == 0.0


def test_constructor_accepts_positive_brush_drop():
    """
    - Confirm allowed boundary cases for optional brush drop behavior.
    - Confirms internal normalization/helper still returns expected values.
    """

    kwargs = valid_kwargs()
    kwargs["brush_drop_voltage"] = 2.0

    m = DummyDCMachine(**kwargs)
    assert m.brush_drop_voltage == 2.0
    assert m._brush_drop_value() == 2.0
