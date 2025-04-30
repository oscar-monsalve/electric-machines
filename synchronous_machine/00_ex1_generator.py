import numpy as np
import helpers_generator as model
# import cmath

# Exercise 1. A 480 V, 60 Hz, 4-pole, delta-connected, synchronous generator has a synchronous reactance of 0.1 Ω
# and an armature resistance of 0.015 Ω:
#    a. What is the speed of the generator?
#    b. If a load is connected in delta drawing 1200 A with fp= 0.8 in lagging, how much field current is required to
#       bring the load voltage to nominal (see the motor magnetization curve).
#    c. Draw the phasor diagram.
#    d. If mechanical and miscellaneous losses add up to 40 kW, core losses are 30 kW and field losses are neglected
#       what is the efficiency of the generator?
#    e. Calculate P, Q and S at the load.
#    f. Induced torque for the load conditions.
#    g. Applied torque for load conditions.


def main() -> None:
    # Input data
    VOLTAGE:     float = 480  # Nominal voltage in V.
    FREQ:        int = 60  # Frequency in Hz.
    P:           int = 4  # Number of poles.
    XS:          float = 0.1  # Synchronous reactance in ohms.
    RA:          float = 0.015  # Armature resistance in ohms.
    FP:          float = 0.8  # Lagging power factor.
    LOAD:        str = "lagging"
    CONNECTION:  str = "delta"
    I_LOAD:      float = 1200  # Load current in amps.
    P_MECH_MISC: float = 40000  # Mechanical and miscellaneous losses in W.
    P_CORE:      float = 30000  # Core losses in W.

    pf_angle = model.power_factor_angle(model.power_factor_sign(LOAD, FP))
    velocity = model.velocity(FREQ, P)
    i_a_rec, i_a_pol, v_phi = model.armature_current(CONNECTION, I_LOAD, VOLTAGE, pf_angle)

    # Voltage drops at jXsIA and RaIa
    jxs = model.complex_reactance(XS)
    ra = model.complex_resistance(RA)
    v_jxs_pol, v_ra_pol, e_a_pol = model.internal_voltage(v_phi, jxs, ra, i_a_rec)

    # Efficiency
    p_cu = model.copper_losses(i_a_pol, ra)
    p_out = model.output_power(VOLTAGE, I_LOAD, FP)
    p_conv = model.converted_power(p_cu, p_out)
    p_in = model.input_power(P_MECH_MISC, P_CORE, p_cu, p_out)
    eff = model.efficiency(p_in, p_out)

    # Apparent and reactive powers
    apparent_power = model.apparent_power(p_out, FP)
    reactive_power = model.reactive_power(apparent_power, p_out)

    # Torques
    t_ind = model.induced_torque(p_conv, velocity)
    t_ap = model.applied_torque(p_in, velocity)

    # Printing results
    print(f"a). The angular velocity is: {velocity} rpm.")
    print("b). Equivalent circuit results:")
    print(f"        The phase voltage V_phi is: {v_phi.real:.2f} V < {v_phi.imag}°.")
    print(f"        The armature current IA is: {i_a_pol[0]:.2f} A < {np.rad2deg(i_a_pol[1]):.2f}°.")
    print(f"        The voltage at jXs is: {v_jxs_pol[0]:.2f} V < {np.rad2deg(v_jxs_pol[1]):.2f}°.")
    print(f"        The voltage at RA is: {v_ra_pol[0]:.2f} V < {np.rad2deg(v_ra_pol[1]):.2f}°.")
    print(f"        The internal voltage E_A is: {e_a_pol[0]:.2f} V < {np.rad2deg(e_a_pol[1]):.2f}°.")
    print(f"        The field current to generate {e_a_pol[0]:.2f} V is aprox. 5.5 A based on the magnetization curve.")
    print("d). Efficiency:")
    print(f"        The cooper losses are: {p_cu:.2f} W.")
    print(f"        The ouput power is: {p_out:.2f} W.")
    print(f"        The input power is: {p_in:.2f} W.")
    print(f"        The efficiency is: {eff:.2f} %.")
    print("e). Power triangle:")
    print(f"        The active power is: {p_out:.2f} W.")
    print(f"        The apparent power is: {apparent_power:.2f} VA.")
    print(f"        The reactive power is: {reactive_power:.2f} VAR.")
    print(f"f). The induced torque is: {t_ind:.2f} Nm.")
    print(f"g). The applied torque is: {t_ap:.2f} Nm.")


if __name__ == "__main__":
    main()
