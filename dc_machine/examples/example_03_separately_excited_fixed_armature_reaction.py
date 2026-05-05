from dc_machine.separately_excited import SeparatelyExcitedMotorGenerator
from pathlib import Path
from dc_machine.utils import (
    extract_magnetization_data_from_csv,
    make_magnetization_curve,
)

exercise_statement = """
Exercise statement:

A separately excited dc generator is rated at 172 kW, 430 V, 400 A, and 1800 r/min. A magnetization curve is
available in "03_mag_curve_example_03.csv".

This machine has the following characteristics:

R_A = 0.05 ohms         V_F = 430 V
R_F = 20 ohms           N_F = 1000 turns per pole
R_adj = 0 to 300 ohms

a) If the variable resistor R_adj in this generator's field circuit is adjusted to 63 ohms, and the genertor's prime
mover is driving it at 1600 r/min, what is this generator's no-load terminal voltage?

b) What would its voltage be if a 360 A load were connected to its terminals? Assume that the generator has
compensating windings.

c) What would its voltage be if a 360 A load were connected to its terminals but the generator does not have
compensating windings? Assume its armature reaction at this load is 450 A-turns.

d) What adjustment could be made to the generator to restore its terminal voltage to the value found in part a?

e) How much field current would be needed to retore the terminal voltage to its no-load value? (Assume that the
machine has compensating windings). What is the required value for te resistor R_adj to accomplish this?
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

    # Extract magnetization data from csv
    examples_dir = Path(__file__).resolve().parent  # Make example CSV paths independent of current working directory
    file_path = examples_dir / "03_mag_curve_example_03.csv"
    field_current_points, emf_points = extract_magnetization_data_from_csv(
        file_path=file_path,
        field_current_column="Shunt field current (A)",
        emf_column="Internal generated voltage E_A (V)"
    )

    # Make magnetization curve object
    magnetization_curve = make_magnetization_curve(
        field_current_points=field_current_points,
        emf_points=emf_points,
        reference_speed_rpm=NOMINAL_SPEED_RPM,
    )

    # Instantiate machine objects with:
    # no armature reaction (compensating windings), and with armature reaction (without compensating windings)
    machine_without_armature_reaction: SeparatelyExcitedMotorGenerator = SeparatelyExcitedMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        speed_rpm=NOMINAL_SPEED_RPM,
        operation_mode="generator",
        magnetization_curve=magnetization_curve,
        shunt_resistance=SHUNT_RESISTANCE,
    )

    machine_with_armature_reaction: SeparatelyExcitedMotorGenerator = SeparatelyExcitedMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        speed_rpm=NOMINAL_SPEED_RPM,
        operation_mode="generator",
        magnetization_curve=magnetization_curve,
        shunt_resistance=SHUNT_RESISTANCE,
        field_turns=SHUNT_FIELD_TURNS,
        armature_reaction_mmf=ARMATURE_REACTION_MMF
    )

    # Part a)
    # Problem: If the variable resistor R_adj in this generator's field circuit is adjusted to 63 ohms, and the
    # genertor's prime mover is driving it at 1600 r/min, what is this generator's no-load terminal voltage?
    # Analysis: it is assumed that the machine has compensating windings (no armature reaction), and for the no-load
    # condition, E_A = V_T.

    FIELD_ADJUSTING_RESISTANCE_PART_A = 63.0
    SPEED_PART_A = 1600.0
    terminal_voltage_no_load_part_a = machine_without_armature_reaction.terminal_voltage_from_field_voltage(
        armature_current=0.0,  # No-load condition
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=FIELD_ADJUSTING_RESISTANCE_PART_A,
        desired_speed_rpm=SPEED_PART_A
    )
    # Calculate field current for solution completeness
    field_current_part_a = machine_without_armature_reaction.field_current(
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=FIELD_ADJUSTING_RESISTANCE_PART_A
    )

    # Part b)
    # What would its voltage be if a 360 A load were connected to its terminals? Assume that the generator has
    # compensating windings.
    # Analysis: the machine as compensating windings, so there is no armature reaction

    LOAD_CURRENT_PART_B = 360.0
    terminal_voltage_part_b = machine_without_armature_reaction.terminal_voltage_from_field_voltage(
        armature_current=LOAD_CURRENT_PART_B,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=FIELD_ADJUSTING_RESISTANCE_PART_A,
        desired_speed_rpm=SPEED_PART_A
    )

    # Part c)
    # What would its voltage be if a 360 A load were connected to its terminals but the generator does not have
    # compensating windings? Assume its armature reaction at this load is 450 A-turns.
    # Analysis: Same load condition from part b, and same condition for speed from part a. Armature reaction
    # has to be accounted for now.

    terminal_voltage_part_c = machine_with_armature_reaction.terminal_voltage_from_field_voltage_with_armature_reaction(
        armature_current=LOAD_CURRENT_PART_B,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=FIELD_ADJUSTING_RESISTANCE_PART_A,
        desired_speed_rpm=SPEED_PART_A
    )
    # Calculate the emf and the effective field current due to the armature reaction for solution completeness
    emf_armature_reaction_part_c = machine_with_armature_reaction.induced_emf_with_armature_reaction(
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=FIELD_ADJUSTING_RESISTANCE_PART_A,
        desired_speed_rpm=SPEED_PART_A
    )
    effective_field_current_part_c = machine_with_armature_reaction.equivalent_field_current_with_armature_reaction(
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=FIELD_ADJUSTING_RESISTANCE_PART_A
    )

    # Part d)
    # How much field current would be needed to retore the terminal voltage to its no-load value? (Assume that the
    # machine has compensating windings). What is the required value for te resistor R_adj to accomplish this?
    # R/. The voltage across the generator terminals has dropped, so to restore it to its original value,
    # the generator voltage must be increased. This requires an increase in E_A, which means that R_adj must be
    # decreased to increase the generator’s field current I_F*.

    # Part e)
    # How much field current would be needed to retore the terminal voltage to its no-load value? (Assume that the
    # machine has compensating windings). What is the required value for te resistor R_adj to accomplish this?
    # Analysis: calculate E_A without armature reaction for a load current of 360 A from part b) and a terminal
    # voltage of 381.6 V, which is that of part a). Then, calculate the field current from that EMF, and lastly,
    # calculate the required field adjusting resistance.

    required_induced_emf_part_e = machine_without_armature_reaction.induced_emf_from_terminal_conditions(
        terminal_voltage=terminal_voltage_no_load_part_a,
        armature_current=LOAD_CURRENT_PART_B
    )

    required_field_current_part_e = machine_without_armature_reaction.equivalent_field_current_from_emf(
        emf=required_induced_emf_part_e,
        desired_speed_rpm=SPEED_PART_A
    )

    required_field_adjusting_resistance_part_e = (
        machine_without_armature_reaction.field_adjusting_resistance_required_for_field_current(
            applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
            field_current=required_field_current_part_e
        )
    )

    # Print solutions

    print(exercise_statement)

    print(
        "----------------------------\n"
        "Machine(s) data\n"
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

    print(f"a) Generator's no-load terminal voltage at {SPEED_PART_A} rpm and R_adj: {FIELD_ADJUSTING_RESISTANCE_PART_A} ohms:")
    print(f"    V_T : {terminal_voltage_no_load_part_a:.2f} V")
    print(f"    for I_F : {field_current_part_a:.2f} A\n")

    print(f"b) Generator's terminal voltage at I_A: {LOAD_CURRENT_PART_B}, {SPEED_PART_A} rpm and R_adj: {FIELD_ADJUSTING_RESISTANCE_PART_A} ohms:")
    print(f"    V_T : {terminal_voltage_part_b:.2f} V\n")

    print(
        f"c) Generator's terminal voltage at I_A: {LOAD_CURRENT_PART_B}, {SPEED_PART_A} rpm and R_adj: {FIELD_ADJUSTING_RESISTANCE_PART_A} ohms\n"
        f"   and armature reaction F_AR: {ARMATURE_REACTION_MMF} A-turns:"
    )
    print(f"    V_T : {terminal_voltage_part_c:.2f} V")
    print(f"    for an effective field current I_F* : {effective_field_current_part_c:.2f} A and E_A: {emf_armature_reaction_part_c:.2f} V\n")

    print("d) What adjustment could be made to the generator to restore its terminal voltage to the value found in part a?")
    print(
        "   R/. The voltage across the generator terminals has dropped, so to restore it to its original value,\n"
        "   the generator voltage must be increased. This requires an increase in E_A, which means that R_adj must be\n"
        "   decreased to increase the generator’s field current I_F\n"
    )

    print(
        f"e) Field current I_F and R_adj values to restore the generator's terminal voltage to "
        f"{terminal_voltage_no_load_part_a:.2f} V:"
    )
    print(f"    Required field current I_F : {required_field_current_part_e:.2f} A")
    print(f"    Required R_adj : {required_field_adjusting_resistance_part_e:.2f} ohms")
    print(f"    For a required induced emf E_A : {required_induced_emf_part_e:.2f} V")


if __name__ == "__main__":
    main()
