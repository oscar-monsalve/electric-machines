from separately_excited import SeparatelyExcitedMotorGenerator
from shunt import ShuntMotorGenerator
from series import SeriesMotorGenerator
from compound import LongCompoundMotorGenerator, ShortCompoundMotorGenerator
# from utils import power_to_watts

# ---- Input description ----
# ARMATURE_RESISTANCE -> Armature winding resistance in ohms. Must be non-zero and a positive value (RA > 0).
# SHUNT_RESISTANCE    -> Shunt winding field resistance in ohms. Must be non-zero and a positive value (RFShunt > 0).
# SERIES_RESISTANCE   -> Series winding field resistance in ohms. Must be non-zero and a positive value (RFSeries > 0).
# NOMINAL_VOLTAGE     -> Nominal operation voltage in volts. Must be a positive value (Vn ≥ 0).
# SPEED_RPM           -> Nominal rotational speed in rpm. Must be non-zero and a positive value (N > 0).
# FLUX                -> Magnetic flux magnitude in webber. Must be non-zero and a positive value (ϕ > 0).
# K_CONSTANT          -> Constant. Must be non-zero and a positive value (K > 0).

def main() -> None:
    # DC Machine nominal parameters
    ARMATURE_RESISTANCE: float = 10.1
    SHUNT_RESISTANCE:    float = 685.0
    SERIES_RESISTANCE:   float = 5.9
    NOMINAL_VOLTAGE:     float = 220
    SPEED_RPM:           float = 1500
    FLUX:                float = 1.0
    K_CONSTANT:          float = 1.0

    # Instantiate machine objects
    separately_excited_machine = SeparatelyExcitedMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_VOLTAGE,
        speed_rpm=SPEED_RPM,
        flux=FLUX,
        k_constant=K_CONSTANT,
        operation_mode="generator",
        shunt_resistance=SHUNT_RESISTANCE,
    )

    series_machine = SeriesMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_VOLTAGE,
        speed_rpm=SPEED_RPM,
        flux=FLUX,
        k_constant=K_CONSTANT,
        operation_mode="generator",
        series_resistance=SERIES_RESISTANCE,
    )

    shunt_machine = ShuntMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_VOLTAGE,
        speed_rpm=SPEED_RPM,
        flux=FLUX,
        k_constant=K_CONSTANT,
        operation_mode="generator",
        shunt_resistance=SHUNT_RESISTANCE,
    )

    long_compound_machine = LongCompoundMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_VOLTAGE,
        speed_rpm=SPEED_RPM,
        flux=FLUX,
        k_constant=K_CONSTANT,
        operation_mode="motor",
        shunt_resistance=SHUNT_RESISTANCE,
        series_resistance=SERIES_RESISTANCE,
    )

    short_compound_machine = ShortCompoundMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_VOLTAGE,
        speed_rpm=SPEED_RPM,
        flux=FLUX,
        k_constant=K_CONSTANT,
        operation_mode="motor",
        shunt_resistance=SHUNT_RESISTANCE,
        series_resistance=SERIES_RESISTANCE,
    )

    print(separately_excited_machine)
    print(shunt_machine)
    print(series_machine)
    print(long_compound_machine)
    print(short_compound_machine)


if __name__ == "__main__":
    main()
