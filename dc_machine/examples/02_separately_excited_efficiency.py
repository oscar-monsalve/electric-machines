from dc_machine.separately_excited import SeparatelyExcitedMotorGenerator
from dc_machine.magnetization import MagnetizationCurve


def main() -> None:
    """
    A DC motor has the following information:

    P_rated = 30 hh         IL_rated = 110 A
    V_T = 240 V             N_F = 2700 turns per pole
    n_rated = 1800 r/min    N_SE = 14 turns per pole
    R_A = 0.19 Ω            R_F = 75 Ω
    R_S = 0.02 Ω            R_adj = 100 to 400 Ω

    Rotational losses = 3550 W at full load
    Magnetization curve data available in csv file '02_mag_curve_for_example02.csv'
    """

    # Machine data
    NOMINAL_VOLTAGE = 220.0
    ARMATURE_RESISTANCE = 2.0
    FIELD_RESISTANCE = 100.0
    BRUSH_DROP = 2.0
    NOMINAL_SPEED_RPM = 1500.0
    MAG_CURVE_RPM = 1000.0

    # Helper function to generate the magnetization_curve object from the MagnetizationCurve class
    def make_magnetization_curve() -> MagnetizationCurve:
        return MagnetizationCurve(
            field_current_points=[0.0, 1.0, 2.0, 3.0],
            emf_points=[10.0, 50.0, 80.0, 100.0],
            reference_speed_rpm=MAG_CURVE_RPM,
        )

    # Instantiate machine object and use custom function 'make_magnetization_curve()' to pass magnetization data.
    machine: SeparatelyExcitedMotorGenerator = SeparatelyExcitedMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_VOLTAGE,
        speed_rpm=NOMINAL_SPEED_RPM,
        operation_mode="generator",
        magnetization_curve=make_magnetization_curve(),
        shunt_resistance=FIELD_RESISTANCE,
        brush_drop_voltage=BRUSH_DROP,
    )

    # Part (a)
    field_current_part_a = machine.field_current(applied_field_voltage=100.0)
    emf_part_a = machine.induced_emf_from_field_voltage(applied_field_voltage=100.0)
    assert field_current_part_a == 1.0

    # Part (b)
    field_current_part_b = machine.magnetization_curve.field_current_from_emf(
        emf=75.0,
        desired_speed_rpm=NOMINAL_SPEED_RPM
    )
    field_voltage_part_b = machine.field_voltage_from_emf(emf=75.0)

    # Part (c)
    armature_current_part_c = machine.armature_current(terminal_voltage=60.0, induced_emf=emf_part_a)

    # Part (d)
    induced_torque_part_d = machine.induced_torque_from_emf(
        armature_current=armature_current_part_c,
        induced_emf=emf_part_a
    )

    # Print solutions
    print("Solution for the following DC machine data:\n")
    print(machine)

    print("a) The field current and the internal generated emf when the external field supply is 100 V:")
    print(f"    Field current: {field_current_part_a:.2f} A.")
    print(f"    EMF: {emf_part_a:.2f} V.")

    print("b). Field winding parameters to generatate 75 V internally at 1500 rpm:")
    print(f"    Field current: {field_current_part_b:.2f} A.")
    print(f"    Field voltage: {field_voltage_part_b:.2f} V.")

    print("c) If the machine supplies a terminal voltage of 60 V under the excitation of part (a), find the armature current:")
    print(f"    Armature current: {armature_current_part_c:.2f} A.")

    print("d) For the operating condition in part (c), determine the induced torque:")
    print(f"    Induced torque: {induced_torque_part_d:.2f} Nm.")


if __name__ == "__main__":
    main()
