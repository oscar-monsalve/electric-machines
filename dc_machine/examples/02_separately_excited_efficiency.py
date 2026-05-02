from dc_machine.separately_excited import SeparatelyExcitedMotorGenerator
from pathlib import Path
from dc_machine.utils import (
    extract_magnetization_data_from_csv,
    make_magnetization_curve,
)

exercise_statement = """
A DC motor has the following information:

P_rated = 30 hp         I_A,rated = 110 A
V_T = 240 V             N_F = 2700 turns per pole
V_F = 240 V             N_SE = 14 turns per pole
n_rated = 1800 r/min    R_shunt = 75 Ω
R_A = 0.19 Ω            R_adj = 100 to 400 Ω
R_series = 0.02 Ω

Rotational losses = 3550 W at full load
Magnetization curve data available (at 1800 rpm) in csv file '02_mag_curve_example_02.csv'

Exercise statement

a) What is the no-load speed of the motor, if it is separately excited, when R_adj = 175 Ω, and
    (a.1) V_T = 120 V, (a.2) V_T = 180 V, (a.3) V_T = 240 V.

b) What is the maximum no-load speed attainable by varying both V_T and R_adj?

c) What is the minimum no-load speed attainable by varying both V_T and R_adj?

d) At rated conditions, determine:
   (d.1) the armature copper losses,
   (d.2) the field copper losses,
   (d.3) the total copper losses,
   (d.4) the electromagnetic converted power,
   (d.5) the input power excluding field-supply power,
   (d.6) the overall input power,
   (d.7) the output power,
   (d.8) the efficiency excluding field-supply power, and
   (d.9) the overall efficiency.

   Assume:
   - Brush voltage drop is 2 V.
   - Armature current at rated conditions is 110 A.
   - Field-adjusting resistance is R_adj = 175 Ω.
   - Mechanical losses are 1200 W.
   - Core losses are 1700 W.
   - miscellaneous losses are 650 W.
"""

def main() -> None:
    # Main machine data
    NOMINAL_TERMINAL_VOLTAGE: float = 240.0
    NOMINAL_FIELD_VOLTAGE:    float = 240.0
    NOMINAL_ARMATURE_CURRENT: float = 110.0
    ARMATURE_RESISTANCE:      float = 0.19
    SHUNT_RESISTANCE:         float = 75.0
    NOMINAL_SPEED_RPM:        float = 1800.0
    BRUSH_DROP_VOLTAGE:       float = 2.0
    MECHANICAL_LOSSES:        float = 1200.0
    CORE_LOSSES:              float = 1700.0
    MISCELLANEOUS_LOSSES:     float = 650.0

    # Additional machine data
    field_adjusting_resistances = [100.0, 175.0, 400.0]
    terminal_voltages = [120.0, 180.0, NOMINAL_TERMINAL_VOLTAGE]

    # Extract magnetization data from csv
    file_path = Path("dc_machine") / "examples" / "02_mag_curve_example_02.csv"
    field_current_points, emf_points = extract_magnetization_data_from_csv(
        file_path=file_path,
        field_current_column="Shunt field current (A)",
        emf_column="Internal generated voltage E_A (V)"
    )

    magnetization_curve = make_magnetization_curve(
        field_current_points=field_current_points,
        emf_points=emf_points,
        reference_speed_rpm=NOMINAL_SPEED_RPM,
    )

    # Instantiate machine objects. Parts (a) to (c) use the OCC-based speed helpers,
    # while part (d) uses the power/efficiency API together with E solved from the
    # rated terminal conditions.
    machine_parts_a_to_c: SeparatelyExcitedMotorGenerator = SeparatelyExcitedMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        speed_rpm=NOMINAL_SPEED_RPM,
        operation_mode="motor",
        magnetization_curve=magnetization_curve,
        shunt_resistance=SHUNT_RESISTANCE,
    )

    machine_part_d: SeparatelyExcitedMotorGenerator = SeparatelyExcitedMotorGenerator(
        armature_resistance=ARMATURE_RESISTANCE,
        nominal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        speed_rpm=NOMINAL_SPEED_RPM,
        operation_mode="motor",
        magnetization_curve=magnetization_curve,
        shunt_resistance=SHUNT_RESISTANCE,
        brush_drop_voltage=BRUSH_DROP_VOLTAGE,
        mechanical_losses=MECHANICAL_LOSSES,
        core_losses=CORE_LOSSES,
        miscellaneous_losses=MISCELLANEOUS_LOSSES
    )

    # Part a)
    field_current_part_a = machine_parts_a_to_c.field_current(
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=field_adjusting_resistances[1]  # R_adj = 175 ohm
    )

    no_load_speeds = []
    for i in terminal_voltages:
        speed = machine_parts_a_to_c.shaft_speed_rpm_from_field_current(
            terminal_voltage=i,
            armature_current=0.0,  # At no-load condition, E_A = V_T (simplified no-load approximation)
            field_current=field_current_part_a
        )
        no_load_speeds.append(speed)

    # Part b). To achieve the maximum no-load speed, R_adj must be at its maximum value
    # (so the magnetic field is minimum), and the terminal voltage V_T at its maximum value (ω = emf / kϕ)

    r_adj_max = field_adjusting_resistances[2]  # Maximum adjusting resistance
    v_t_max = terminal_voltages[2]  # Maximum terminal voltage

    field_current_part_b = machine_parts_a_to_c.field_current(
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=r_adj_max
    )

    maximum_speed = machine_parts_a_to_c.shaft_speed_rpm_from_field_current(
        terminal_voltage=v_t_max,
        armature_current=0.0,
        field_current=field_current_part_b
    )

    # Part c). To achieve the minimum no-load speed, R_adj must be at its minimum value
    # (so the magnetic field is maximum), and the terminal voltage V_T at its minimum value (ω = emf / kϕ).

    r_adj_min = field_adjusting_resistances[0]  # Minimum adjusting resistance
    v_t_min = terminal_voltages[0]  # Minimum terminal voltage
    field_current_part_c = machine_parts_a_to_c.field_current(
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=r_adj_min
    )
    minimum_speed = machine_parts_a_to_c.shaft_speed_rpm_from_field_current(
        terminal_voltage=v_t_min,
        armature_current=0.0,
        field_current=field_current_part_c
    )

    # Part d)

    field_adjusting_resistance_part_d = field_adjusting_resistances[1]  # 175 Ω
    induced_emf = machine_part_d.induced_emf_from_terminal_conditions(
        terminal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        armature_current=NOMINAL_ARMATURE_CURRENT
    )
    armature_copper_losses = machine_part_d.armature_copper_losses(
        armature_current=NOMINAL_ARMATURE_CURRENT
    )
    field_copper_losses = machine_part_d.field_copper_losses(
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=field_adjusting_resistance_part_d
    )
    field_adjusting_resistor_losses = machine_part_d.field_adjusting_resistor_losses(
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=field_adjusting_resistance_part_d
    )
    total_machine_copper_losses = machine_part_d.copper_losses(
        armature_current=NOMINAL_ARMATURE_CURRENT,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=field_adjusting_resistance_part_d,
        include_field_adjusting_resistor_losses=False
    )
    total_field_circuit_resistive_losses = machine_part_d.copper_losses(
        armature_current=NOMINAL_ARMATURE_CURRENT,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=field_adjusting_resistance_part_d,
        include_field_adjusting_resistor_losses=True
    )
    electromagnetic_converted_power = machine_part_d.electromagnetic_power(
        armature_current=NOMINAL_ARMATURE_CURRENT,
        induced_emf=induced_emf
    )
    field_input_power = machine_part_d.field_input_power(
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=field_adjusting_resistance_part_d
    )
    input_power_excluding_field_power = machine_part_d.input_power(
        terminal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        armature_current=NOMINAL_ARMATURE_CURRENT,
        induced_emf=induced_emf,
        applied_field_voltage=None,
        include_field_power=False
    )
    overall_input_power = machine_part_d.input_power(
        terminal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        armature_current=NOMINAL_ARMATURE_CURRENT,
        induced_emf=induced_emf,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=field_adjusting_resistance_part_d,
        include_field_power=True
    )
    output_power = machine_part_d.output_power(
        terminal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        armature_current=NOMINAL_ARMATURE_CURRENT,
        induced_emf=induced_emf,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=field_adjusting_resistance_part_d,
        include_field_power=True
    )
    eff_excluding_field_power = machine_part_d.efficiency_excluding_field_power(
        terminal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        armature_current=NOMINAL_ARMATURE_CURRENT,
        induced_emf=induced_emf
    )
    eff_overall = machine_part_d.overall_efficiency(
        terminal_voltage=NOMINAL_TERMINAL_VOLTAGE,
        armature_current=NOMINAL_ARMATURE_CURRENT,
        induced_emf=induced_emf,
        applied_field_voltage=NOMINAL_FIELD_VOLTAGE,
        field_adjusting_resistance=field_adjusting_resistance_part_d
    )

    # Print solutions

    print(exercise_statement)

    print("\nDC machine (parts a to c):\n")
    print(machine_parts_a_to_c)

    print("DC machine (part d):\n")
    print(machine_part_d)

    print("a) Motor's no-load speeds when R_adj = 175 Ω:")
    print(f"    a.1) n_m@V_T = 120 V : {no_load_speeds[0]:.2f} rpm")
    print(f"    a.2) n_m@V_T = 180 V : {no_load_speeds[1]:.2f} rpm")
    print(f"    a.3) n_m@V_T = 240 V : {no_load_speeds[2]:.2f} rpm")

    print("\nb) Motor's maximum no-load speed:")
    print(f"    n_m_max : {maximum_speed:.2f} rpm")
    print(f"    (at I_F: {field_current_part_b:.2f} A, V_T: {v_t_max:.2f} V, R_adj: {r_adj_max:.2f} Ω)")

    print("\nc) Motor's minimum no-load speed:")
    print(f"    n_m_min : {minimum_speed:.2f} rpm")
    print(f"    (at I_F: {field_current_part_c:.2f} A, V_T: {v_t_min:.2f} V, R_adj: {r_adj_min:.2f} Ω)")

    print(f"\nd) At rated conditions (V_T: {NOMINAL_TERMINAL_VOLTAGE:.2f} V, I_A: {NOMINAL_ARMATURE_CURRENT:.2f} A), losses and efficiencies are:")
    print(f"    d.1) P_Cu_armature : {armature_copper_losses:.2f} W")
    print(f"    d.2) P_Cu_F : {field_copper_losses:.2f} W")
    print(f"    d.3) P_Cu_total_machine : {total_machine_copper_losses:.2f} W")
    print(f"    d.4) P_conv : {electromagnetic_converted_power:.2f} W")
    print(f"    d.5) P_in (excluding field power) : {input_power_excluding_field_power:.2f} W")
    print(f"    d.6) P_in_overall (including field power) : {overall_input_power:.2f} W")
    print(f"    d.7) P_out : {output_power:.2f} W")
    print(f"    d.8) eff (excluding field power) : {eff_excluding_field_power:.2f} %")
    print(f"    d.9) eff_overall : {eff_overall:.2f} %")
    print("\nAdditional field-circuit quantities at rated conditions:")
    print(f"    P_F : {field_input_power:.2f} W")
    print(f"    P_R_adj : {field_adjusting_resistor_losses:.2f} W")
    print(f"    Total resistive losses in armature + field circuit : {total_field_circuit_resistive_losses:.2f} W")


if __name__ == "__main__":
    main()
