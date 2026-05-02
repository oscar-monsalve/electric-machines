from pathlib import Path

import pytest

from dc_machine.magnetization import MagnetizationCurve
from dc_machine.utils import (
    extract_magnetization_data_from_csv,
    make_magnetization_curve,
    power_to_watts,
    rpm_to_rad_s,
    speed_regulation,
)

def test_power_to_watts_converts_supported_units():
    assert power_to_watts(10.0, "watts") == pytest.approx(10.0)
    assert power_to_watts(1.0, "hp") == pytest.approx(745.7)
    assert power_to_watts(1.0, "cv") == pytest.approx(735.5)

def test_power_to_watts_rejects_invalid_unit():
    with pytest.raises(ValueError, match="active power units"):
        power_to_watts(1.0, "kw")

def test_rpm_to_rad_s_converts_speed_units():
    assert rpm_to_rad_s(60.0) == pytest.approx(2 * 3.141592653589793)

def test_speed_regulation_computes_percentage():
    assert speed_regulation(speed_no_load=1050.0, speed_full_load=1000.0) == pytest.approx(5.0)

@pytest.mark.parametrize("speed_no_load,speed_full_load,error_msg", [(0.0, 1000.0, "No-load speed"), (1000.0, 0.0, "Full-load speed")])
def test_speed_regulation_rejects_zero_inputs(speed_no_load, speed_full_load, error_msg):
    with pytest.raises(ValueError, match=error_msg):
        speed_regulation(speed_no_load=speed_no_load, speed_full_load=speed_full_load)

def test_make_magnetization_curve_returns_curve_instance():
    curve = make_magnetization_curve(
        field_current_points=[0.0, 1.0],
        emf_points=[10.0, 20.0],
        reference_speed_rpm=1000.0,
    )

    assert isinstance(curve, MagnetizationCurve)
    assert curve.field_current_points == [0.0, 1.0]
    assert curve.emf_points == [10.0, 20.0]

def test_extract_magnetization_data_from_csv_reads_named_columns(tmp_path: Path):
    csv_path = tmp_path / "curve.csv"
    csv_path.write_text("If,E\n0.0,10.0\n1.0,50.0\n", encoding="utf-8")

    field_current_points, emf_points = extract_magnetization_data_from_csv(
        file_path=csv_path,
        field_current_column="If",
        emf_column="E",
    )

    assert field_current_points == [0.0, 1.0]
    assert emf_points == [10.0, 50.0]

def test_extract_magnetization_data_from_csv_rejects_missing_file(tmp_path: Path):
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="does not exist"):
        extract_magnetization_data_from_csv(file_path=missing_path)

def test_extract_magnetization_data_from_csv_rejects_missing_column(tmp_path: Path):
    csv_path = tmp_path / "curve.csv"
    csv_path.write_text("If,E\n0.0,10.0\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required column"):
        extract_magnetization_data_from_csv(
            file_path=csv_path,
            field_current_column="field_current",
            emf_column="E",
        )

def test_extract_magnetization_data_from_csv_rejects_invalid_numeric_value(tmp_path: Path):
    csv_path = tmp_path / "curve.csv"
    csv_path.write_text("If,E\n0.0,10.0\n1.0,not-a-number\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid numeric value"):
        extract_magnetization_data_from_csv(
            file_path=csv_path,
            field_current_column="If",
            emf_column="E",
        )
