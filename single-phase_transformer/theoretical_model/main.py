import equivalent_circuit_parameters as model

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

    a = model.transformation_ratio(vn1, vn2)

    in1 = model.nominal_current(sn, vn1)
    in2 = model.nominal_current(sn, vn2)

    open_circuit_test_side = model.open_circuit_test_side(i0, in1, in2)

    s0 = model.open_circuit_aparent_power(open_circuit_test_side, vn1, vn2, i0)
    q0 = model.open_circuit_reactive_power(s0, p0)

    rm1, xm1, rm2, xm2 = model.core_resistance_and_reactance(open_circuit_test_side, a, vn1, vn2, p0, q0)

    if1, im1, if2, im2 = model.core_currents(open_circuit_test_side, vn1, vn2, rm1, xm1, rm2, xm2)

    i01, i02 = model.open_circuit_current(if1, im1, if2, im2)

    print(f"- Transformation ratio -> a: {a:.2f}.")
    print(f"- Primary nominal current -> IN1: {in1:.2f} A.")
    print(f"- Secondary nominal current -> IN2: {in2:.2f} A.")
    print(f"- The open-circuit test was performed at the {open_circuit_test_side.upper()} side.")
    print(f"- Open-circuit aparent power at the {open_circuit_test_side.upper()} -> S0: {s0:.2f} VA.")
    print(f"- Open-circuit reactive power at the {open_circuit_test_side.upper()} -> Q0: {q0:.2f} VAR.")

    print("- Core impedance referred to the primary:")
    print(f"        RM1: {rm1:.2f} ohm.\n        XM1: {xm1:.2f} ohm.")
    print("- Core impedance referred to the secondary:")
    print(f"        RM2: {rm2:.2f} ohm.\n        XM2: {xm2:.2f} ohm.")

    print("- Core currents referred to the primary:")
    print(f"        If1: {if1:.6f} A.\n        IM1: {im1:.6f} A.")
    print("- Core impedance referred to the secondary:")
    print(f"        If2: {if2:.2f} A.\n        IM2: {im2:.2f} A.")

    print(f"- Open-circuit current at the primary -> I01: {i01:.6f} A.")
    print(f"- Open-circuit current at the secondary -> I02: {i02:.2f} A.")


if __name__ == "__main__":
    main()
