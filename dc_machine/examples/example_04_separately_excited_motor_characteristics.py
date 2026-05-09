from pathlib import Path
import matplotlib.pyplot as plt
from dc_machine.plot_helpers import (
    motor_torque_current_characteristic_data,
    motor_torque_speed_characteristic_data,
    plot_motor_torque_current_characteristic,
    plot_motor_torque_speed_characteristic,
)
from dc_machine.separately_excited import SeparatelyExcitedMotorGenerator
from dc_machine.utils import (
    extract_magnetization_data_from_csv,
    make_magnetization_curve,
    rpm_to_rad_s,
)


exercise_statement = """
Exercise statement:

A separately excited dc motor uses the same machine data and magnetization curve from example 03. The magnetization
curve is available in "03_mag_curve_example_03.csv" and was measured at 1800 r/min.

This machine has the following characteristics:

R_A = 0.05 ohms         V_F = 430 V
R_F = 20 ohms           N_F = 1000 turns per pole
R_adj = 0 to 300 ohms

a) If the variable resistor R_adj in the field circuit is adjusted to 63 ohms and the motor terminal voltage is
430 V, what is the no-load speed? Use the no-load approximation I_A = 0 A.

b) If the motor is supplying a load that draws I_A = 360 A at the same terminal voltage and field setting, what are
the motor speed, induced emf, and induced torque?

c) What is the electromagnetic converted power at the load condition from part b?

d) Plot the motor torque-speed characteristic for this terminal voltage and field setting.

e) Plot the motor torque-armature-current characteristic for this terminal voltage and field setting.

For parts d) and e), compare the compensated case with the uncompensated case. Assume the uncompensated motor has a
fixed demagnetizing armature reaction of 450 A-turns.
"""


def main() -> None:
    # Main machine data
    NOMINAL_TERMINAL_VOLTAGE: float = 430.0
    NOMINAL_FIELD_VOLTAGE:    float = 430.0
    ARMATURE_RESISTANCE:      float = 0.05
    SHUNT_RESISTANCE:         float = 20.0
    NOMINAL_SPEED_RPM:        float = 1800.0
    SHUNT_FIELD_TURNS:        float = 1000.0
    ARMATURE_REACTION_MMF:    float = 450.0

    # Operating data
    FIELD_ADJUSTING_RESISTANCE = 63.0
    LOAD_ARMATURE_CURRENT = 360.0

    # Extract magnetization data from csv
    examples_dir = Path(__file__).resolve().parent
    file_path = examples_dir / "03_mag_curve_example_03.csv"
    field_current_points, emf_points = extract_magnetization_data_from_csv(
        file_path=file_path,
        field_current_column="Shunt field current (A)",
        emf_column="Internal generated voltage E_A (V)",
    )

    # Make magnetization curve object
    magnetization_curve = make_magnetization_curve(
        field_current_points=field_current_points,
        emf_points=emf_points,
        reference_speed_rpm=NOMINAL_SPEED_RPM,
    )

    # Instantiate motor objects. The characteristic helpers used here are OCC-based.
    machine_without_armature_reaction: SeparatelyExcitedMotorGenerator = SeparatelyExcitedMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        speed_rpm=NOMINAL_SPEED_RPM,
        operation_mode="motor",
        magnetization_curve=magnetization_curve,
        shunt_resistance=SHUNT_RESISTANCE,
    )

    machine_with_armature_reaction: SeparatelyExcitedMotorGenerator = SeparatelyExcitedMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        speed_rpm=NOMINAL_SPEED_RPM,
        operation_mode="motor",
        magnetization_curve=magnetization_curve,
        shunt_resistance=SHUNT_RESISTANCE,
        field_turns=SHUNT_FIELD_TURNS,
        armature_reaction_mmf=ARMATURE_REACTION_MMF,
    )

    # Part a)
    field_current_part_a = machine_without_armature_reaction.field_current(
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=FIELD_ADJUSTING_RESISTANCE,
    )
    no_load_speed_rpm = machine_without_armature_reaction.shaft_speed_rpm_from_field_voltage(
        terminal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        armature_current=0.0,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=FIELD_ADJUSTING_RESISTANCE,
    )

    # Parts b) and c)
    load_speed_rpm = machine_without_armature_reaction.shaft_speed_rpm_from_field_voltage(
        terminal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        armature_current=LOAD_ARMATURE_CURRENT,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=FIELD_ADJUSTING_RESISTANCE,
    )
    load_induced_emf = machine_without_armature_reaction.induced_emf_from_terminal_conditions(
        terminal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        armature_current=LOAD_ARMATURE_CURRENT,
    )
    load_induced_torque = (load_induced_emf * LOAD_ARMATURE_CURRENT) / rpm_to_rad_s(load_speed_rpm)
    load_electromagnetic_power = machine_without_armature_reaction.electromagnetic_power(
        armature_current=LOAD_ARMATURE_CURRENT,
        induced_emf=load_induced_emf,
    )

    # Parts d) and e): motor characteristic curves
    step = 50
    armature_current_sweep = [i for i in range(0, 400 + step, step)]

    torque_points, speed_points = motor_torque_speed_characteristic_data(
        machine=machine_without_armature_reaction,
        armature_current_points=armature_current_sweep,
        terminal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=FIELD_ADJUSTING_RESISTANCE,
        include_armature_reaction=False,
    )

    torque_points_with_armature_reaction, speed_points_with_armature_reaction = motor_torque_speed_characteristic_data(
        machine=machine_with_armature_reaction,
        armature_current_points=armature_current_sweep,
        terminal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=FIELD_ADJUSTING_RESISTANCE,
        include_armature_reaction=True,
    )

    _, current_points = motor_torque_current_characteristic_data(
        machine=machine_without_armature_reaction,
        armature_current_points=armature_current_sweep,
        terminal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=FIELD_ADJUSTING_RESISTANCE,
        include_armature_reaction=False,
    )

    _, current_points_with_armature_reaction = motor_torque_current_characteristic_data(
        machine=machine_with_armature_reaction,
        armature_current_points=armature_current_sweep,
        terminal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=FIELD_ADJUSTING_RESISTANCE,
        include_armature_reaction=True,
    )

    fig_speed, ax_speed = plot_motor_torque_speed_characteristic(
        torque_points=torque_points,
        speed_points=speed_points,
        label="With compensating windings (no armature reaction)",
        title="Motor torque-speed characteristic",
    )

    plot_motor_torque_speed_characteristic(
        torque_points=torque_points_with_armature_reaction,
        speed_points=speed_points_with_armature_reaction,
        ax=ax_speed,
        label="Without compensating windings (armature reaction)",
    )

    fig_current, ax_current = plot_motor_torque_current_characteristic(
        torque_points=torque_points,
        armature_current_points=current_points,
        label="With compensating windings (no armature reaction)",
        title="Motor torque-current characteristic",
    )

    plot_motor_torque_current_characteristic(
        torque_points=torque_points_with_armature_reaction,
        armature_current_points=current_points_with_armature_reaction,
        ax=ax_current,
        label="Without compensating windings (armature reaction)",
    )

    # Print solutions
    print(exercise_statement)

    print(
        "----------------------------\n"
        "Machine data\n"
        "----------------------------"
    )
    print("\nMachine without armature reaction:\n")
    print(machine_without_armature_reaction)
    print("Machine with armature reaction:\n")
    print(machine_with_armature_reaction)

    print(
        "----------------------------\n"
        "Solution\n"
        "----------------------------"
    )

    print(
        f"a) Motor no-load speed at V_T = {NOMINAL_TERMINAL_VOLTAGE:.0f} V, "
        f"V_F = {NOMINAL_FIELD_VOLTAGE:.0f} V, and R_adj = {FIELD_ADJUSTING_RESISTANCE:.0f} ohms:"
    )
    print(f"    I_F : {field_current_part_a:.2f} A")
    print(f"    n_m : {no_load_speed_rpm:.2f} rpm\n")

    print(f"b) Motor loaded condition at I_A = {LOAD_ARMATURE_CURRENT:.0f} A:")
    print(f"    E_A : {load_induced_emf:.2f} V")
    print(f"    n_m : {load_speed_rpm:.2f} rpm")
    print(f"    T_ind : {load_induced_torque:.2f} N·m\n")

    print("c) Electromagnetic converted power at the loaded condition:")
    print(f"    P_conv : {load_electromagnetic_power:.2f} W")

    print("\nd) and e) Motor characteristic plots were generated.")

    plt.show()


if __name__ == "__main__":
    main()
