from dc_machine.separately_excited import SeparatelyExcitedMotorGenerator
from dc_machine.utils import make_magnetization_curve


def main() -> None:
    """
    Exercise statement

    A separately excited 220 V DC generator rotates at 1500 rpm. Its armature resistance
    is 2.0 ohm, its field resistance is 100.0 ohm, and the brush drop is 2.0 V.
    The machine magnetization curve, measured at 1000 rpm, is:

        If = [0.0, 1.0, 2.0, 3.0] A
        E  = [10.0, 50.0, 80.0, 100.0] V

    Determine:

    a) The field current and the internal generated emf when the external field
       supply is 100 V.
    b) The field current and the field voltage required to generate 75 V internally
       at 1500 rpm.
    c) If the machine supplies a terminal voltage of 60 V under the excitation of
       part (a), find the armature current.
    d) For the operating condition in part (c), determine the induced torque.
     """

    # Machine data
    NOMINAL_VOLTAGE = 220.0
    ARMATURE_RESISTANCE = 2.0
    FIELD_RESISTANCE = 100.0
    BRUSH_DROP = 2.0
    NOMINAL_SPEED_RPM = 1500.0
    MAG_CURVE_RPM = 1000.0

    # Build the machine with OCC data so the example can use the public excitation helpers.
    machine: SeparatelyExcitedMotorGenerator = SeparatelyExcitedMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_VOLTAGE,
        speed_rpm=NOMINAL_SPEED_RPM,
        operation_mode="generator",
        magnetization_curve=make_magnetization_curve(
            field_current_points=[0.0, 1.0, 2.0, 3.0],
            emf_points=[10.0, 50.0, 80.0, 100.0],
            reference_speed_rpm=MAG_CURVE_RPM,
        ),
        shunt_resistance=FIELD_RESISTANCE,
        brush_drop_voltage=BRUSH_DROP,
    )

    # Part (a)
    # Direct field-circuit calculation plus OCC-based emf calculation.
    field_current_part_a = machine.field_current(applied_field_voltage=100.0)
    emf_part_a = machine.induced_emf_from_field_voltage(applied_field_voltage=100.0)

    # Part (b)
    # Inverse OCC use: first obtain the required field voltage, then recover the
    # corresponding field current through the machine API.
    field_voltage_part_b = machine.field_voltage_from_emf(emf=75.0)
    field_current_part_b = machine.field_current(applied_field_voltage=field_voltage_part_b)

    # Part (c)
    armature_current_part_c = machine.armature_current(terminal_voltage=60.0, induced_emf=emf_part_a)

    # Part (d)
    induced_torque_part_d = machine.induced_torque_from_emf(
        armature_current=armature_current_part_c,
        induced_emf=emf_part_a
    )

    # Print solutions
    print(
        "----------------------------\n"
        "Machine(s) data\n"
        "----------------------------"
    )

    print(machine)

    print(
        "----------------------------\n"
        "Solution\n"
        "----------------------------"
    )
    print("a) The field current and the internal generated emf when the external field supply is 100 V:")
    print(f"    Field current: {field_current_part_a:.2f} A.")
    print(f"    EMF: {emf_part_a:.2f} V.")

    print("b) The field current and the field voltage required to generate 75 V internally at 1500 rpm:")
    print(f"    Field current: {field_current_part_b:.2f} A.")
    print(f"    Field voltage: {field_voltage_part_b:.2f} V.")

    print("c) If the machine supplies a terminal voltage of 60 V under the excitation of part (a), find the armature current:")
    print(f"    Armature current: {armature_current_part_c:.2f} A.")

    print("d) For the operating condition in part (c), determine the induced torque:")
    print(f"    Induced torque: {induced_torque_part_d:.2f} N·m.")


if __name__ == "__main__":
    main()
