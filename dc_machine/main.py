from separately_excited import SeparatelyExcitedMotorGenerator
from shunt import ShuntMotorGenerator
from series import SeriesMotorGenerator
from compound import CompoundMotorGenerator

# ---- Input description ----
# OPERATION_MODE        -> Operation mode as "motor" or "generator". The user must specify one of the two.
# ARMATURE_RESISTANCE   -> Armature resistance in ohms. Must be non-zero and a positive value (RA > 0).
# FIELD_RESISTANCE      -> Field resistance in ohms. Must be non-zero and a positive value (RF > 0).
# VOLTAGE               -> Nominal operation voltage in volts. Must be a positive value (VN ≥ 0).
# SPEED                 -> Nominal rotational speed in rpm. Must be non-zero and a positive value (N > 0).
# FLUX                  -> Magnetic flux magnitude in webber. Must be non-zero and a positive value (ϕ > 0).
# K_CONSTANT            -> Constant. Must be non-zero and a positive value (K > 0).

def main() -> None:
    OPERATION_MODE = "generator"
    ARMATURE_RESISTANCE: float = 0.2
    FIELD_RESISTANCE:    float = 0.2
    VOLTAGE:             float = 110
    SPEED:               float = 1800
    FLUX:                float = 0.12
    K_CONSTANT:          float = 1

    shunt_machine: ShuntMotorGenerator = ShuntMotorGenerator(
        ARMATURE_RESISTANCE,
        FIELD_RESISTANCE,
        VOLTAGE,
        SPEED,
        FLUX,
        K_CONSTANT,
        operation_mode=OPERATION_MODE
    )

    print("Shunt_machine:")
    print(f"    Armature resistance: {shunt_machine.armature_resistance}")


if __name__ == "__main__":
    main()
