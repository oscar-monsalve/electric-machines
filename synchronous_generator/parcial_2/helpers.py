from cmath import rect, polar
from math import cos, sin, sqrt, radians, degrees


def syncrhonous_impedance_magnitude(armature_resistance: float, syncrhonous_reactance: complex, ) -> complex:
    return sqrt(armature_resistance**2 + syncrhonous_reactance.imag**2)


def equivalent_circuit_resistance(armature_resistance: float, load_resistance: float, ) -> float:
    return armature_resistance + load_resistance


def equivalent_circuit_reactance(syncrhonous_reactance: float, load_reactance: complex) -> complex:
    return complex(0, syncrhonous_reactance.imag + load_reactance.imag)


def equivalent_circuit_impedance_magnitude(circuit_equivalent_resistance: float, circuit_equivalent_reactance: complex, ) -> float:
    return sqrt(circuit_equivalent_resistance**2 + circuit_equivalent_reactance.imag**2)


def power_factor_angle(load_impedance: complex) -> float:
    if load_impedance.imag == 0:
        return degrees(polar(load_impedance)[1])
    elif load_impedance.imag > 0:
        return degrees(polar(load_impedance)[1]) * -1
    elif load_impedance.imag < 0:
        return degrees(polar(load_impedance)[1]) * -1


def armature_current(internal_generated_voltage: float, equivalent_impedance: complex,
                     pf_angle: float) -> tuple[complex, float, float]:
    ia = internal_generated_voltage / sqrt(equivalent_impedance.real**2 + equivalent_impedance.imag**2)
    i_a_rec = rect(ia, radians(pf_angle))
    i_a_magnitude = polar(i_a_rec)[0]
    i_a_phase_angle = degrees(polar(i_a_rec)[1])
    return i_a_rec, i_a_magnitude, i_a_phase_angle


def phase_voltage(armature_current_magnitude: float, load_impedance: float) -> float:
    return armature_current_magnitude * sqrt(load_impedance.real**2 + load_impedance.imag**2)


def line_voltage(phase_voltage: float) -> float:
    return phase_voltage * sqrt(3)


def input_power(line_voltage: float, armature_current: float, pf_angle: float, armature_resistance: float) -> float:
    p_out = sqrt(3) * line_voltage * armature_current * cos(radians(pf_angle))
    p_cu = 3 * armature_current**2 * armature_resistance
    return p_out + p_cu


def internal_generated_voltage_phasor(phase_voltage: float, armature_current: complex,
                                      syncrhonous_reactance: complex) -> tuple[float, float]:
    ea_rec = phase_voltage + armature_current * (syncrhonous_reactance)
    ea_magnitud = polar(ea_rec)[0]
    ea_phase_angle = degrees(polar(ea_rec)[1])
    return ea_magnitud, ea_phase_angle


def armature_resistance_voltage(armature_current: complex, armature_resistance: float) -> tuple[float, float]:
    v_ra = armature_current * armature_resistance
    v_ra_magnitud = polar(v_ra)[0]
    v_ra_angle = degrees(polar(v_ra)[1])
    return v_ra_magnitud, v_ra_angle


def syncrhonous_reactance_voltage(armature_current: complex, syncrhonous_reactance: complex) -> tuple[float, float]:
    v_xs = armature_current * syncrhonous_reactance
    v_xs_magnitud = polar(v_xs)[0]
    v_xs_angle = degrees(polar(v_xs)[1])
    return v_xs_magnitud, v_xs_angle


def phasor_xy_coordinates(phasors: list[tuple[float, float]]) -> list[tuple[float, float]]:
    phasor_xy_coordinates = []
    for r, theta in phasors:
        x = r * cos(radians(theta))
        y = r * sin(radians(theta))
        phasor_xy_coordinates.append((x, y))
    return phasor_xy_coordinates


def label_vector(ax, start: tuple[float, float], vec: tuple[float, float], text: str, color: str,
                 scale: float = 0, offset_x: float = 0, offset_y: float = 0) -> None:
    dx, dy = vec
    vec_magnitude = sqrt(dx**2 + dy**2)

    if vec_magnitude == 0:
        perp_offset_x, perp_offset_y = 0, 0
    else:
        perp_dx = -dy / vec_magnitude
        perp_dy = dx / vec_magnitude
        perp_offset_x = perp_dx * scale * vec_magnitude
        perp_offset_y = perp_dy * scale * vec_magnitude

    # Final label position
    end_x = start[0] + dx + perp_offset_x + offset_x
    end_y = start[1] + dy + perp_offset_y + offset_y

    ax.text(end_x, end_y, text, color=color, fontsize=18, weight="bold")
