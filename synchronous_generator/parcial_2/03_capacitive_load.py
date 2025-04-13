import helpers as h


# Input data
RL_CEDULA: float = 53  # Últimos dos dígitos de la cédula de los estudiantes para definir a la resistencia de carga

# Constants
ZL:      complex = RL_CEDULA - 80j
EA:        float = 2400
RA:        float = 17
XS:      complex = 144j


def main() -> None:
    zs_phasor = RA + XS
    zs_magnitude = h.syncrhonous_impedance_magnitude(RA, XS)
    req = h.equivalent_circuit_resistance(RA, ZL.real)
    xeq = h.equivalent_circuit_reactance(XS, ZL)
    zeq = req + xeq
    power_factor_angle = h.power_factor_angle(ZL)
    ia_rec, ia_pol = h.armature_current(EA, zeq, power_factor_angle)
    phase_voltage = h.phase_voltage(ia_pol[0], ZL)
    line_voltage = h.line_voltage(phase_voltage)
    p_in = h.input_power(line_voltage, ia_pol[0], power_factor_angle, RA)
    ea_magnitud, ea_phase_angle = h.internal_generated_voltage_phasor(phase_voltage, ia_rec, zs_phasor)
    v_ra_magnitude, v_ra_phase_angle = h.armature_resistance_voltage(ia_rec, RA)
    v_xs_magnitude, v_xs_phase_angle = h.syncrhonous_reactance_voltage(ia_rec, XS)

    print(f"a). Z_S   : {zs_magnitude} Ω")
    print(f"b). R_eq  : {req} Ω")
    print(f"    X_eq  : {xeq} Ω")
    print(f"    Z_eq  : {zeq} Ω")
    print(f"c). I_A   : {ia_pol[0]:.2f} A ∠{power_factor_angle:.2f}°")
    print(f"d). V_phi : {phase_voltage:.2f} V ∠0°")
    print(f"    V_L   : {line_voltage:.2f} V")
    print(f"e). P_in  : {p_in:.2f} W")
    print("f). Phasor diagram values:")
    print(f"         V_phi    : {phase_voltage:.2f} V ∠0°")
    print(f"         E_A      : {ea_magnitud:.2f} V ∠{ea_phase_angle:.2f}°")
    print(f"         I_A*R_A  : {v_ra_magnitude:.2f} V  ∠{v_ra_phase_angle:.2f}°")
    print(f"         I_A*jX_S : {v_xs_magnitude:.2f} V ∠{v_xs_phase_angle:.2f}°")


if __name__ == "__main__":
    main()
