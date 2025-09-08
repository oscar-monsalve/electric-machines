import equivalent_circuit_parameters as model
import regulation_efficiency
from numpy import linspace
from math import acos, degrees
import matplotlib.pyplot as plt
import scienceplots
plt.style.use(["science", "notebook", "grid"])

# --- Exercise example ---
# For a single-phase transformer of 15 kVA 7600/220 V, which in open-circuit takes 2 A and 200 W, and in
# short-circuit with 300 V at a nominal current dissipates 220 W. Determine the equivalent circuit parameters,
# the voltage regulation and the efficiency for the following loads:
# a) 12 kVA with power factor of 0.85 at 220 V.
# b) 12 kW with power factor of 0.85 at 220 V.
# b) At 75% of nominal load with power factor of 95% at 220 V.


def main() -> None:
    """
    The inputs to determine the equivalent circuit parameters are:
    - Nominal aparent power S_N.
    - Primary and secondary voltages V_N1 and V_N2, respectively.
    - Open-circuit current I_0.
    - Open-circuit active power P_0.
    - Short-circuit voltage V_cc.
    - Short-circuit power P_cc.
    """

    # Input parameters
    sn = 15000  # VA
    vn1 = 7600  # V
    vn2 = 220  # V
    i0 = 2  # A
    p0 = 200  # W
    vcc = 300  # V
    pcc = 220  # W
    is_load_percentage = False  # True: you are given a load percentage. False: you are not given a load percentage
    a = model.transformation_ratio(vn1, vn2)

    in1 = model.nominal_current(sn, vn1)
    in2 = model.nominal_current(sn, vn2)

    open_circuit_test_side = model.open_circuit_test_side(i0, in1, in2)
    s0 = model.open_circuit_aparent_power(open_circuit_test_side, vn1, vn2, i0)
    q0 = model.open_circuit_reactive_power(s0, p0)

    rm1, xm1, rm2, xm2 = model.core_resistance_and_reactance(open_circuit_test_side, a, vn1, vn2, p0, q0)
    if1, im1, if2, im2 = model.core_currents(open_circuit_test_side, vn1, vn2, rm1, xm1, rm2, xm2)
    i01, i02 = model.open_circuit_current(if1, im1, if2, im2)

    short_circuit_test_side = model.short_circuit_test_side(vcc, vn1, vn2)
    scc = model.short_circuit_aparent_power(short_circuit_test_side, vcc, in1, in2)
    qcc = model.short_circuit_reactive_power(scc, pcc)

    re1, xe1, re2, xe2 = model.equivalent_resistance_and_reactance(pcc, qcc, in1, in2)

    r1, x1, r2, x2 = model.primary_secondary_impedances(a, re1, xe1, re2, xe2)

    # Calculate voltage regulation and efficiency
    sc = regulation_efficiency.load_apparent_power(is_load_percentage, sn)
    ic2 = regulation_efficiency.load_current(sc, vn2)
    phase_angle = regulation_efficiency.phase_angle()
    pl, ql = regulation_efficiency.load_active_reactive_powers(sc, phase_angle)
    v20 = regulation_efficiency.secondary_open_circuit_voltage(phase_angle, vn2, ic2, re2, xe2)
    voltaje_regulation = regulation_efficiency.voltage_regulation(v20, vn2)
    efficiency = regulation_efficiency.efficiency(phase_angle, vn2, ic2, re2, p0)

    # --- Plot calculation for efficiency/voltage regulation vs %load (constant pf) ---
    solution_space = 200
    load_percentage_solution_space = linspace(0, 100, num=solution_space)
    power_factors_set = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]

    efficiency_plot_each_fp = []  # list of lists for each power factor
    voltage_regulation_each_fp = []  # list of lists for each power factor

    for pf in power_factors_set:
        fp_efficiencies = []
        fp_voltage_regulations = []
        for i in load_percentage_solution_space:
            sc_var = (sn * i) / 100
            ic2_var = regulation_efficiency.load_current(sc_var, vn2)
            phase_angle_var = degrees(acos(pf))

            # Voltage regulation
            v20_var = regulation_efficiency.secondary_open_circuit_voltage(phase_angle_var, vn2, ic2_var, re2, xe2)
            voltaje_regulation_var = regulation_efficiency.voltage_regulation(v20_var, vn2)

            # Efficiency
            efficiency_var = regulation_efficiency.efficiency(phase_angle_var, vn2, ic2_var, re2, p0)

            fp_efficiencies.append(efficiency_var)
            fp_voltage_regulations.append(voltaje_regulation_var)

        efficiency_plot_each_fp.append(fp_efficiencies)
        voltage_regulation_each_fp.append(fp_voltage_regulations)

    # --- Plot calculation for efficiency/voltage regulation vs fp (constat %load) ---
    power_factor_solution_space = linspace(0.1, 1, num=solution_space)
    load_percentage_set = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    efficiency_plot_each_load = []  # list of lists for each %load
    voltage_regulation_each_load = []  # list of lists for each %load

    for load in load_percentage_set:
        load_efficiencies = []
        load_voltage_regulations = []
        for pf in power_factor_solution_space:
            sc_var = (sn * (load/100))
            ic2_var = regulation_efficiency.load_current(sc_var, vn2)
            phase_angle_var = degrees(acos(pf))

            # Voltage regulation
            v20_var = regulation_efficiency.secondary_open_circuit_voltage(phase_angle_var, vn2, ic2_var, re2, xe2)
            voltaje_regulation_var = regulation_efficiency.voltage_regulation(v20_var, vn2)

            # Efficiency
            efficiency_var = regulation_efficiency.efficiency(phase_angle_var, vn2, ic2_var, re2, p0)

            load_efficiencies.append(efficiency_var)
            load_voltage_regulations.append(voltaje_regulation_var)

        efficiency_plot_each_load.append(load_efficiencies)
        voltage_regulation_each_load.append(load_voltage_regulations)

    # Print solution
    print(f"- Transformation ratio -> a: {a:.2f}.")
    print(f"- Primary nominal current -> IN1: {in1:.2f} A.")
    print(f"- Secondary nominal current -> IN2: {in2:.2f} A.\n")
    print(f"- The open-circuit test was performed at the {open_circuit_test_side.upper()} side.")
    print(f"- Open-circuit aparent power at the {open_circuit_test_side.upper()} -> S0: {s0:.2f} VA.")
    print(f"- Open-circuit reactive power at the {open_circuit_test_side.upper()} -> Q0: {q0:.2f} VAR.")
    print("- Core impedance at the primary:")
    print(f"        RM1: {rm1:.2f} ohm.\n        XM1: {xm1:.2f} ohm.")
    print("- Core impedance referred to the secondary:")
    print(f"        RM2: {rm2:.2f} ohm.\n        XM2: {xm2:.2f} ohm.")
    print("- Core currents at the primary:")
    print(f"        If1: {if1:.6f} A.\n        IM1: {im1:.6f} A.")
    print("- Core currents referred to the secondary:")
    print(f"        If2: {if2:.2f} A.\n        IM2: {im2:.2f} A.")
    print(f"- Open-circuit current at the primary -> I01: {i01:.6f} A.")
    print(f"- Open-circuit current referred to the secondary -> I02: {i02:.2f} A.\n")

    print(f"- The short-circuit test was performed at the {short_circuit_test_side.upper()} side.")
    print(f"- Short-circuit aparent power at the {short_circuit_test_side.upper()} -> Scc: {scc:.2f} VA.")
    print(f"- Short-circuit reactive power at the {short_circuit_test_side.upper()} -> Qcc: {qcc:.2f} VAR.")
    print("- Equivalent impendace at the primary:")
    print(f"        Re1: {re1:.2f} ohm.\n        Xe1: {xe1:.2f} ohm.")
    print("- Equivalent impendace at the secondary:")
    print(f"        Re1: {re2:.6f} ohm.\n        Xe1: {xe2:.6f} ohm.")
    print("- Primary impendace:")
    print(f"        R1: {r1:.2f} ohm.\n        X1: {x1:.2f} ohm.")
    print("- Secondary impendace:")
    print(f"        R2: {r2:.6f} ohm.\n        X2: {x2:.6f} ohm.\n")

    print("Voltage Regulation and efficiency:")
    print(f"- Load aparent power             -> S_L: {sc:.2f} VA")
    print(f"- Load current                   -> I_L2: {ic2:.2f} A.")
    print(f"- Phase angle                    -> phi: {phase_angle:.2f}°.")
    print(f"- Load active power              -> P_L: {pl:.2f} W.")
    print(f"- Load reactive power            -> Q_L: {ql:.2f} VAR.")
    print(f"- Secondary open-circuit voltage -> V20: {v20:.2f} V.")
    print(f"- Voltage regulation             -> ΔV%: {voltaje_regulation:.2f} %.")
    print(f"- Efficiency                     -> eta: {efficiency:.2f} %.")

    # --- Efficiency vs %load (pf constant) ---
    plt.figure()
    for index, pf in enumerate(power_factors_set):
        plt.plot(load_percentage_solution_space,
                 efficiency_plot_each_fp[index],
                 label=f"fp={pf}")

    plt.xlabel(r"Porcentaje de carga (%)")
    plt.ylabel(r"Eficiencia $\eta$ (%)")
    plt.title(r"Eficiencia en función del porcentaje de carga para cada condición de fp")
    plt.xlim(left=0, right=100)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.grid(True)
    # plt.show()

    # --- Voltage regulation vs %load (pf constant)---
    plt.figure()
    for index, pf in enumerate(power_factors_set):
        plt.plot(load_percentage_solution_space,
                 voltage_regulation_each_fp[index],
                 label=f"fp={pf}")

    plt.xlabel(r"Porcentaje de carga (%)")
    plt.ylabel(r"Regulación de voltaje (%)")
    plt.title(r"Regulación de voltaje en función del porcentaje de carga para cada condición de fp")
    plt.xlim(left=0, right=100)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.grid(True)
    # plt.show()

    # --- Efficiency vs pf (%load constant) ---
    plt.figure()
    for index, load in enumerate(load_percentage_set):
        plt.plot(power_factor_solution_space,
                 efficiency_plot_each_load[index],
                 label=rf"$S_C$={load}%")

    plt.xlabel(r"Factor de potencia $(-)$")
    plt.ylabel(r"Eficiencia $\eta$ (%)")
    plt.title(r"Eficiencia en función del factor de potencia para cada condición de carga")
    plt.xlim(left=0.1, right=1)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.grid(True)
    # plt.show()

    # --- Voltage regulation vs pf (%load constant) ---
    plt.figure()
    for index, load in enumerate(load_percentage_set):
        plt.plot(power_factor_solution_space,
                 voltage_regulation_each_load[index],
                 label=rf"$S_C$={load}%")

    plt.xlabel(r"Factor de potencia $(-)$")
    plt.ylabel(r"Regulación de voltaje $\Delta V\%$ (%)")
    plt.title(r"Regulación de voltaje en función del factor de potencia para cada condición de carga")
    plt.xlim(left=0.1, right=1)
    # plt.ylim(top=5)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.grid(True)

    plt.show()


if __name__ == "__main__":
    main()
