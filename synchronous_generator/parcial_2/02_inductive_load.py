import matplotlib.pyplot as plt
import helpers as h


# Input data
XL_CEDULA: complex = 72j  # Últimos dos dígitos de la cédula de los estudiantes para definir a la reactancia de carga

# Constants
ZL:      complex = 175 + XL_CEDULA
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
    ia_rec, ia_magnitude, ia_phase_angle = h.armature_current(EA, zeq, power_factor_angle)
    phase_voltage = h.phase_voltage(ia_magnitude, ZL)
    line_voltage = h.line_voltage(phase_voltage)
    p_in = h.input_power(line_voltage, ia_magnitude, power_factor_angle, RA)
    ea_magnitud, ea_phase_angle = h.internal_generated_voltage_phasor(phase_voltage, ia_rec, zs_phasor)
    v_ra_magnitude, v_ra_phase_angle = h.armature_resistance_voltage(ia_rec, RA)
    v_xs_magnitude, v_xs_phase_angle = h.syncrhonous_reactance_voltage(ia_rec, XS)
    phasors = [
        (phase_voltage, 0),
        (ea_magnitud, ea_phase_angle),
        (ia_magnitude, ia_phase_angle),
        (v_ra_magnitude, v_ra_phase_angle),
        (v_xs_magnitude, v_xs_phase_angle),
    ]
    phasor_xy_coordinates = h.phasor_xy_coordinates(phasors)
    v_phase_vec = phasor_xy_coordinates[0]
    ea_vec = phasor_xy_coordinates[1]
    ia_vec = phasor_xy_coordinates[2]
    v_ra_vec = phasor_xy_coordinates[3]
    v_xs_vec = phasor_xy_coordinates[4]

    print(f"a). Z_S   : {zs_magnitude} Ω")
    print(f"b). R_eq  : {req} Ω")
    print(f"    X_eq  : {xeq} Ω")
    print(f"    Z_eq  : {zeq} Ω")
    print(f"c). I_A   : {ia_magnitude:.2f} A ∠{ia_phase_angle:.2f}°")
    print(f"d). V_phi : {phase_voltage:.2f} V ∠0°")
    print(f"    V_L   : {line_voltage:.2f} V")
    print(f"e). P_in  : {p_in:.2f} W")
    print("f). Phasor diagram values:")
    print(f"         V_phi    : {phase_voltage:.2f} V ∠0°")
    print(f"         E_A      : {ea_magnitud:.2f} V ∠{ea_phase_angle:.2f}°")
    print(f"         I_A      : {ia_magnitude:.2f} A ∠{ia_phase_angle:.2f}°")
    print(f"         I_A*R_A  : {v_ra_magnitude:.2f} V  ∠{v_ra_phase_angle:.2f}°")
    print(f"         I_A*jX_S : {v_xs_magnitude:.2f} V ∠{v_xs_phase_angle:.2f}°")

    fig, ax = plt.subplots(figsize=(10, 8))

    # Phasor's start and end
    origin = (0, 0)
    v_ra_vec_start = (v_phase_vec[0], v_phase_vec[1])
    v_xs_vec_start = (v_phase_vec[0] + v_ra_vec[0], v_phase_vec[1] + v_ra_vec[1])

    ax.quiver(*origin, *v_phase_vec, angles="xy", scale_units="xy",
              scale=1, color="blue",
              label=fr"$V_{{\phi}}={{{phase_voltage:.2f}}}\; V \; \angle 0^{{\circ}}$")

    ax.quiver(*origin, *ia_vec, angles="xy", scale_units="xy",
              scale=0.04, color="red",
              label=fr"$I_A={{{ia_magnitude:.2f}}}\; A \; \angle {{{ia_phase_angle:.2f}}}^{{\circ}}$ (not to scale)")

    ax.quiver(*origin, *ea_vec, angles="xy", scale_units="xy",
              scale=1, color="purple",
              label=fr"$E_A={{{ea_magnitud:.2f}}}\; V \; \angle {{{ea_phase_angle:.2f}}}^{{\circ}}$")

    ax.quiver(*v_ra_vec_start, *v_ra_vec, angles="xy", scale_units="xy",
              scale=1, color="green",
              label=fr"$I_A R_A={{{v_ra_magnitude:.2f}}}\; V \; \angle {{{v_ra_phase_angle:.2f}}}^{{\circ}}$")

    ax.quiver(*v_xs_vec_start, *v_xs_vec, angles="xy", scale_units="xy",
              scale=1, color="black",
              label=fr"$I_A jX_S={{{v_xs_magnitude:.2f}}}\; V \; \angle {{{v_xs_phase_angle:.2f}}}^{{\circ}}$")

    # Phasor labels
    h.label_vector(ax, origin, v_phase_vec, r"$V_\phi$", "blue", offset_x=-90, offset_y=-100)
    h.label_vector(ax, origin, ia_vec, r"$I_A$", "red", offset_x=190, offset_y=-130)
    h.label_vector(ax, origin, ea_vec, r"$E_A$", "purple", offset_x=-130, offset_y=20)
    h.label_vector(ax, v_ra_vec_start, v_ra_vec, r"$I_A R_A$", "green", offset_y=-100)
    h.label_vector(ax, v_xs_vec_start, v_xs_vec, r"$I_A jX_S$", "black", offset_x=10, offset_y=-90)

    ax.set_xlim(min(0, ea_vec[0])-100, max(ea_vec[0], v_phase_vec[0]+v_ra_vec[0])+300)
    ax.set_ylim(min(0, ia_vec[1])-300, max(ea_vec[1], v_phase_vec[1])+100)
    ax.set_aspect("equal")
    ax.set_title('Phasor Diagram - Synchronous Generator')
    ax.set_xlabel('Re')
    ax.set_ylabel('Im')
    ax.legend(loc="upper left")
    ax.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
