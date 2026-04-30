from dc_machine.separately_excited import SeparatelyExcitedMotorGenerator
# from dc_machine.magnetization import MagnetizationCurve
from dc_machine.utils import extract_magnetization_data_from_csv, make_magnetization_curve
from pathlib import Path


def main() -> None:
    """
    A DC motor has the following information:

    P_rated = 30 hp         IL_rated = 110 A
    V_T = 240 V             N_F = 2700 turns per pole
    V_F = 240.0             N_SE = 14 turns per pole
    n_rated = 1800 r/min    R_shunt = 75 Ω
    R_A = 0.19 Ω            R_adj = 100 to 400 Ω
    R_series = 0.02 Ω

    Rotational losses = 3550 W at full load
    Magnetization curve data available (at 1800 rpm) in csv file '02_mag_curve_example_02.csv'

    Exercise statement

    a) What is the no-load speed of the motor, if it is separately excited, when R_adj = 175 Ω, and
        (a.1) V_T = 120 V, (a.2) V_T = 180 V, (a.3) V_T = 240 V.

    b) What is the maximum no-load speed attainable by varying both V_T and R_adj?

    c) What is the minimum no-load speed attainable by varying both V_T and R_adj?

    d) What is the motor's efficiency at rated conditions? Assume that: (1) the brush voltage drop
       is 2 V; (2) the core loss is to be determined at an armature voltage equal to the armature
       voltage under full load; and (3) stray load losses are 1 percent of full load.
    """

    # Machine data
    NOMINAL_TERMINAL_VOLTAGE = 240.0
    NOMINAL_FIELD_VOLTAGE = 240.0
    ARMATURE_RESISTANCE = 0.19
    SHUNT_RESISTANCE = 75.0
    NOMINAL_SPEED_RPM = 1800.0
    r_adj = [100.0, 175.0, 400.0]

    # Extract magnetization data from csv
    file_path = Path("dc_machine") / "examples" / "02_mag_curve_example_02.csv"

    field_current_points, emf_points = extract_magnetization_data_from_csv(
        file_path=file_path,
        field_current_column="Shunt field current (A)",
        emf_column="Internal generated voltage E_A (V)"
    )

    # Instantiate machine object and use custom function 'make_magnetization_curve()' to pass magnetization data.
    machine: SeparatelyExcitedMotorGenerator = SeparatelyExcitedMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        speed_rpm=NOMINAL_SPEED_RPM,
        operation_mode="motor",
        magnetization_curve=make_magnetization_curve(  # Using helper function to generate the magnetization_curve object from the MagnetizationCurve class
            field_current_points=field_current_points,
            emf_points=emf_points,
            reference_speed_rpm=NOMINAL_SPEED_RPM,
        ),
        shunt_resistance=SHUNT_RESISTANCE,
    )

    # Part a) What is the no-load speed of the motor, if it is separately excited, when R_adj = 175 Ω, and
    #     (a.1) V_T = 120 V, (a.2) V_T = 180 V, (a.3) V_T = 240 V.
    # R/. To achieve the maximum speed, R_adj must be at its maximum value (so the magnetic field is minimum), and
    # the terminal voltage V_T at its maximum value. This is because ω = emf / kϕ
    armature_current = ...

    machine.shaft_speed_rpm_from_field_voltage(
        terminal_voltage=120.0,
        armature_current=armature_current,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE
    )

    # Print solutions
    print("Solution for the following DC machine data:\n")
    print(machine)


if __name__ == "__main__":
    main()
