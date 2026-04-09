from separately_excited import SeparatelyExcitedMotorGenerator
from shunt import ShuntMotorGenerator
from series import SeriesMotorGenerator
from compound import (CumulativeCompoundMotorGenerator,
                      DifferentialCompoundMotorGenerator)

# ---- Input description ----
# ARMATURE_RESISTANCE -> Armature winding resistance in ohms. Must be non-zero and a positive value (RA > 0).
# SHUNT_RESISTANCE    -> Shunt winding field resistance in ohms. Must be non-zero and a positive value (RFShunt > 0).
# SERIES_RESISTANCE   -> Series winding field resistance in ohms. Must be non-zero and a positive value (RFSeries > 0).
# VOLTAGE             -> Nominal operation voltage in volts. Must be a positive value (VN ≥ 0).
# SPEED               -> Nominal rotational speed in rpm. Must be non-zero and a positive value (N > 0).
# FLUX                -> Magnetic flux magnitude in webber. Must be non-zero and a positive value (ϕ > 0).
# K_CONSTANT          -> Constant. Must be non-zero and a positive value (K > 0).

def main() -> None:
    # Machine nominal parameters
    ARMATURE_RESISTANCE: float = 10.1
    SHUNT_RESISTANCE:    float = 685.0
    SERIES_RESISTANCE:   float = 5.9
    VOLTAGE:             float = 220
    SPEED:               float = 1500
    FLUX:                float = 1.0
    K_CONSTANT:          float = 1.0

    # Instantiate machine objects
    separately_excited_machine = SeparatelyExcitedMotorGenerator(
        ARMATURE_RESISTANCE,
        SHUNT_RESISTANCE,
        SERIES_RESISTANCE,
        VOLTAGE,
        SPEED,
        FLUX,
        K_CONSTANT,
        operation_mode="generator"
    )

    series_machine = SeriesMotorGenerator(
        ARMATURE_RESISTANCE,
        SHUNT_RESISTANCE,
        SERIES_RESISTANCE,
        VOLTAGE,
        SPEED,
        FLUX,
        K_CONSTANT,
        operation_mode="generator"
    )

    shunt_machine = ShuntMotorGenerator(
        ARMATURE_RESISTANCE,
        SHUNT_RESISTANCE,
        SERIES_RESISTANCE,
        VOLTAGE,
        SPEED,
        FLUX,
        K_CONSTANT,
        operation_mode="generator"
    )

    cumulative_compound_machine = CumulativeCompoundMotorGenerator(
        ARMATURE_RESISTANCE,
        SHUNT_RESISTANCE,
        SERIES_RESISTANCE,
        VOLTAGE,
        SPEED,
        FLUX,
        K_CONSTANT,
        operation_mode="motor"
    )

    differential_compound_machine = DifferentialCompoundMotorGenerator(
        ARMATURE_RESISTANCE,
        SHUNT_RESISTANCE,
        SERIES_RESISTANCE,
        VOLTAGE,
        SPEED,
        FLUX,
        K_CONSTANT,
        operation_mode="motor"
    )

    print(separately_excited_machine)
    print(shunt_machine)
    print(series_machine)
    print(cumulative_compound_machine)
    print(differential_compound_machine)


if __name__ == "__main__":
    main()
