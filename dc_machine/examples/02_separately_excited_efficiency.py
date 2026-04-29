from dc_machine.separately_excited import SeparatelyExcitedMotorGenerator
from dc_machine.magnetization import MagnetizationCurve
from dc_machine.utils import extract_magnetization_data_from_csv


def main() -> None:
    """
    A DC motor has the following information:

    P_rated = 30 hh         IL_rated = 110 A
    V_T = 240 V             N_F = 2700 turns per pole
    n_rated = 1800 r/min    N_SE = 14 turns per pole
    R_A = 0.19 Ω            R_shunt = 75 Ω
    R_series = 0.02 Ω       R_adj = 100 to 400 Ω

    Rotational losses = 3550 W at full load
    Magnetization curve data available in csv file '02_mag_curve_for_example02.csv'
    """

    # Machine data
    NOMINAL_VOLTAGE = 240.0
    ARMATURE_RESISTANCE = 0.19
    SHUNT_RESISTANCE = 100.0
    NOMINAL_SPEED_RPM = 1500.0
    MAG_CURVE_RPM = 1000.0

    # Extract magnetization data from csv
    file_path = "dc_machine/examples/02_mag_curve_example_02.csv"
    field_current_points, emf_points = extract_magnetization_data_from_csv(
        file_path=file_path,
        field_current_column="Shunt field current (A)",
        emf_column="Internal generated voltage E_A (V)"
    )

    # Helper function to generate the magnetization_curve object from the MagnetizationCurve class
    def make_magnetization_curve() -> MagnetizationCurve:
        return MagnetizationCurve(
            field_current_points=field_current_points,
            emf_points=emf_points,
            reference_speed_rpm=MAG_CURVE_RPM,
        )

    # Instantiate machine object and use custom function 'make_magnetization_curve()' to pass magnetization data.
    machine: SeparatelyExcitedMotorGenerator = SeparatelyExcitedMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_VOLTAGE,
        speed_rpm=NOMINAL_SPEED_RPM,
        operation_mode="generator",
        magnetization_curve=make_magnetization_curve(),
        shunt_resistance=SHUNT_RESISTANCE,
    )

    # Print solutions
    print("Solution for the following DC machine data:\n")
    print(machine)

    print(field_current_points)
    print(emf_points)


if __name__ == "__main__":
    main()
