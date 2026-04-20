from separately_excited import SeparatelyExcitedMotorGenerator
from shunt import ShuntMotorGenerator
from series import SeriesMotorGenerator
from compound import LongCompoundMotorGenerator, ShortCompoundMotorGenerator
from magnetization import MagnetizationCurve
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
    # self,
    # armature_resistance: float,
    # nominal_voltage: float,
    # speed_rpm: float,
    # operation_mode: str,
    # flux: float | None = None,
    # k_constant: float | None = None,
    # magnetization_curve: MagnetizationCurve = None,
    # shunt_resistance: float | None = None,
    # series_resistance: float | None = None,
    # brush_drop_voltage: float | None = None

    # DC Machine nominal parameters
    ARMATURE_RESISTANCE:                     float = 10.1
    NOMINAL_VOLTAGE:                         float = 220
    SPEED_RPM:                               float = 1500
    FLUX:                             float | None = None
    K_CONSTANT:                       float | None = None
    MAGNETIZATION_CURVE: MagnetizationCurve | None = MagnetizationCurve(
        field_current_points=[0.0, 1.0, 2.0, 3.0],
        emf_points=[10.0, 50.0, 80.0, 100.0],
        reference_speed_rpm=1000.0
    )
    SHUNT_RESISTANCE:                 float | None = 685.0
    SERIES_RESISTANCE:                float | None = 5.9
    BRUSH_DROP_VOLTAGE:               float | None = None

    # Instantiate machine objects
    separately_excited_machine = SeparatelyExcitedMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_VOLTAGE,
        speed_rpm=SPEED_RPM,
        flux=FLUX,
        k_constant=K_CONSTANT,
        magnetization_curve=MAGNETIZATION_CURVE,
        operation_mode="generator",
        shunt_resistance=SHUNT_RESISTANCE,
        brush_drop_voltage=BRUSH_DROP_VOLTAGE
    )

    # series_machine = SeriesMotorGenerator(
    #     armature_resistance=ARMATURE_RESISTANCE,
    #     nominal_voltage=NOMINAL_VOLTAGE,
    #     speed_rpm=SPEED_RPM,
    #     flux=FLUX,
    #     k_constant=K_CONSTANT,
    #     operation_mode="generator",
    #     series_resistance=SERIES_RESISTANCE,
    # )
    #
    # shunt_machine = ShuntMotorGenerator(
    #     armature_resistance=ARMATURE_RESISTANCE,
    #     nominal_voltage=NOMINAL_VOLTAGE,
    #     speed_rpm=SPEED_RPM,
    #     flux=FLUX,
    #     k_constant=K_CONSTANT,
    #     operation_mode="generator",
    #     shunt_resistance=SHUNT_RESISTANCE,
    # )
    #
    # long_compound_machine = LongCompoundMotorGenerator(
    #     armature_resistance=ARMATURE_RESISTANCE,
    #     nominal_voltage=NOMINAL_VOLTAGE,
    #     speed_rpm=SPEED_RPM,
    #     flux=FLUX,
    #     k_constant=K_CONSTANT,
    #     operation_mode="motor",
    #     shunt_resistance=SHUNT_RESISTANCE,
    #     series_resistance=SERIES_RESISTANCE,
    # )
    #
    # short_compound_machine = ShortCompoundMotorGenerator(
    #     armature_resistance=ARMATURE_RESISTANCE,
    #     nominal_voltage=NOMINAL_VOLTAGE,
    #     speed_rpm=SPEED_RPM,
    #     flux=FLUX,
    #     k_constant=K_CONSTANT,
    #     operation_mode="motor",
    #     shunt_resistance=SHUNT_RESISTANCE,
    #     series_resistance=SERIES_RESISTANCE,
    # )

    print(separately_excited_machine)
    # print(shunt_machine)
    # print(series_machine)
    # print(long_compound_machine)
    # print(short_compound_machine)


if __name__ == "__main__":
    main()
