from separately_excited import SeparatelyExcitedMotorGenerator
from shunt import ShuntMotorGenerator
from series import SeriesMotorGenerator
from compound import CompoundMotorGenerator


def main() -> None:
    RA:  float = 0.2
    RF:  float = 0.2
    V:   float = 110
    N:   float = 1800
    # PHI: float = 0.12
    # K:   float = 1

    shunt_machine: ShuntMotorGenerator = ShuntMotorGenerator(RA, RF, V, N)

    print(f"Shunt_machine:")
    print(f"    Armature resistance: {shunt_machine.armature_resistance}")


if __name__ == "__main__":
    main()
