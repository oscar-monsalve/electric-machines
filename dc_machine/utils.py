from math import pi
import csv
from pathlib import Path

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

def extract_magnetization_data_from_csv(
    file_path: str | Path,
    field_current_column: str = "field_current",
    emf_column: str = "emf",
) -> tuple[list[float], list[float]]:
    """Reads field current and emf data from a CSV file.

    The CSV file must contain a header row with one column for the field
    current and one column for the induced emf. By default, the expected
    column names are "field_current" and "emf".

    Args:
        file_path: path to the CSV file.
        field_current_column: name of the column containing the field current values, in amperes.
        emf_column: name of the column containing the induced emf values, in volts.

    Returns:
        A tuple containing two lists:
        1. field current values, in amperes.
        2. induced emf values, in volts.

    Raises:
        FileNotFoundError: if the CSV file does not exist.
        ValueError: if the CSV file is empty, if the required columns are missing,
            or if any value cannot be converted to float.
    """
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"The file does not exist: {file_path}")

    field_currents: list[float] = []
    emfs: list[float] = []

    with file_path.open(mode="r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError("The CSV file is empty or has no header row.")

        if field_current_column not in reader.fieldnames:
            raise ValueError(f"Missing required column: {field_current_column}")

        if emf_column not in reader.fieldnames:
            raise ValueError(f"Missing required column: {emf_column}")

        for row_number, row in enumerate(reader, start=2):
            try:
                field_current = float(row[field_current_column])
                emf = float(row[emf_column])
            except ValueError as error:
                raise ValueError(
                    f"Invalid numeric value in row {row_number}: {row}"
                ) from error

            field_currents.append(field_current)
            emfs.append(emf)

    return field_currents, emfs
