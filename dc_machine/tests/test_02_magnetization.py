import pytest
from magnetization import MagnetizationCurve


def make_curve() -> MagnetizationCurve:
    return MagnetizationCurve(
        field_current_points=[0.0, 1.0, 2.0, 3.0],
        emf_points=[10.0, 50.0, 80.0, 100.0],
        reference_speed_rpm=1000.0
    )

def test_constructor_accepts_valid_inputs():
    curve = make_curve()

    assert curve.field_current_points == [0.0, 1.0, 2.0, 3.0]
    assert curve.emf_points == [10.0, 50.0, 80.0, 100.0]
    assert curve.reference_speed_rpm == 1000.0

@pytest.mark.parametrize(
    "field_current_points,emf_points,error_msg",
    [
        ([0.0], [10.0], "at least two"),
        ([0.0, 1.0], [10.0], "same size"),
        ([0.0, -1.0], [10.0, 20.0], "negative values for field_current_points"),
        ([0.0, 1.0], [10.0, -20.0], "negative values for emf_points"),
        ([0.0, 1.0, 1.0], [10.0, 20.0, 30.0], "strictly increasing"),
        ([0.0, 2.0, 1.0], [10.0, 20.0, 30.0], "strictly increasing"),
        ([0.0, 1.0, 2.0], [10.0, 30.0, 20.0], "non-decreasing"),
    ],
)
def test_constructor_rejects_invalid_curve_data(field_current_points, emf_points, error_msg):
    with pytest.raises(ValueError, match=error_msg):
        MagnetizationCurve(
            field_current_points=field_current_points,
            emf_points=emf_points,
            reference_speed_rpm=1000.0
        )

@pytest.mark.parametrize("reference_speed_rpm", [0.0, -1000.0])
def test_constructor_rejects_non_positive_reference_speed(reference_speed_rpm):
    with pytest.raises(ValueError, match="Reference speed"):
        MagnetizationCurve(
            field_current_points=[0.0, 1.0],
            emf_points=[10.0, 20.0],
            reference_speed_rpm=reference_speed_rpm
        )

def test_emf_from_field_current_interpolates_at_reference_speed():
    curve = make_curve()

    emf = curve.emf_from_field_current(field_current=1.5, desired_speed_rpm=1000.0)
    assert emf == 65.0

def test_emf_from_field_current_scales_with_speed():
    curve = make_curve()

    emf = curve.emf_from_field_current(field_current=1.5, desired_speed_rpm=2000.0)
    assert emf == 130.0

def test_emf_from_field_current_clamps_below_first_point():
    curve = make_curve()

    emf = curve.emf_from_field_current(field_current=-0.0, desired_speed_rpm=1000.0)
    assert emf == pytest.approx(10.0)

def test_emf_from_field_current_clamps_above_last_point():
    curve = make_curve()

    emf = curve.emf_from_field_current(field_current=10.0, desired_speed_rpm=1000.0)
    assert emf == pytest.approx(100.0)

@pytest.mark.parametrize("field_current", [-0.1])
def test_emf_from_field_current_rejects_negative_current(field_current):
    curve = make_curve()

    with pytest.raises(ValueError, match="Field current"):
        curve.emf_from_field_current(field_current=field_current, desired_speed_rpm=1000.0)

@pytest.mark.parametrize("desired_speed_rpm", [0.0, -1000.0])
def test_emf_from_field_current_rejects_non_positive_speed(desired_speed_rpm):
    curve = make_curve()

    with pytest.raises(ValueError, match="speed"):
        curve.emf_from_field_current(field_current=1.0, desired_speed_rpm=desired_speed_rpm)

def test_field_current_from_emf_inverse_interpolates_at_reference_speed():
    curve = make_curve()

    field_current = curve.field_current_from_emf(emf=65.0, desired_speed_rpm=1000.0)
    assert field_current == 1.5

def test_field_current_from_emf_inverse_scales_with_speed():
    curve = make_curve()

    field_current = curve.field_current_from_emf(emf=130.0, desired_speed_rpm=2000.0)
    assert field_current == 1.5

def test_field_current_from_emf_clamps_below_first_point():
    curve = make_curve()

    field_current = curve.field_current_from_emf(emf=1.0, desired_speed_rpm=1000.0)
    assert field_current == 0.0

def test_field_current_from_emf_clamps_above_last_point():
    curve = make_curve()

    field_current = curve.field_current_from_emf(emf=1000.0, desired_speed_rpm=1000.0)
    assert field_current == 3.0

@pytest.mark.parametrize("emf", [-0.1])
def test_field_current_from_emf_rejects_negative_emf(emf):
    curve = make_curve()

    with pytest.raises(ValueError, match="EMF"):
        curve.field_current_from_emf(emf=emf, desired_speed_rpm=1000.0)


@pytest.mark.parametrize("desired_speed_rpm", [0.0, -1000.0])
def test_field_current_from_emf_rejects_non_positive_speed(desired_speed_rpm):
    curve = make_curve()

    with pytest.raises(ValueError, match="speed"):
        curve.field_current_from_emf(emf=50.0, desired_speed_rpm=desired_speed_rpm)
