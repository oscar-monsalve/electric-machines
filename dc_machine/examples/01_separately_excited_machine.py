from separately_excited import SeparatelyExcitedMotorGenerator
from magnetization import MagnetizationCurve
from utils import rpm_to_rad_s


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

    machine: SeparatelyExcitedMotorGenerator = SeparatelyExcitedMotorGenerator(
        armature_resistance=2.0,
        nominal_voltage=220.0,

    )

if __name__ == "__main__":
    main()
