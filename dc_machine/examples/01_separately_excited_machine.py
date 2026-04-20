from dc_machine.separately_excited import SeparatelyExcitedMotorGenerator
from dc_machine.magnetization import MagnetizationCurve
# from utils import rpm_to_rad_s


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
    field_current = machine.field_current(applied_field_voltage=100.0)
    assert field_current == 1.0

    print(f"a). Field current: {field_current} A.")


if __name__ == "__main__":
    main()
