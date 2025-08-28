import helpers_ex2
from numpy import linspace
import matplotlib.pyplot as plt
import scienceplots
plt.style.use(["science", "notebook", "grid"])

# inputs
LINE_VOLTAGE = 200.92  # line-to-line nominal motor voltage (V).
CONNECTION = 2      # 1 if connected in "wye" or 2 if connected in "delta".
FREQUENCY = 60      # motor frequency (Hz).
POLES = 4           # total number of motor poles
R1 = 10.1          # stator resistance (ohms).
X1 = 7.036j         # stator reactance (ohms).
X2 = 10.554j         # stator reactance (ohms).
XM = 130.394j          # magnetizing reactance (ohms).
R2 = 1.72          # rotor resistance (ohms).


def main() -> None:
    phase_voltage = helpers_ex2.phase_voltage(LINE_VOLTAGE, CONNECTION)
    sync_velocity_rpm = helpers_ex2.synchronous_velocity(FREQUENCY, POLES)
    sync_velocity_radsec = helpers_ex2.rpm2radsec(sync_velocity_rpm)

    # Thevenin equivalent
    v_th = helpers_ex2.thevenin_voltage(phase_voltage, R1, X1, XM)
    z_th = helpers_ex2.thevenin_impedance(R1, X1, XM)
    r_th, x_th = z_th.real, z_th.imag

    # solution for a)
    torque_max = helpers_ex2.max_torque_induced(v_th, r_th, x_th, X2, sync_velocity_radsec)
    s_max = helpers_ex2.max_slip_at_max_torque(r_th, x_th, R2, X2)
    velocity_at_torque_max = helpers_ex2.shaft_velocity(sync_velocity_rpm, s_max)

    # solution for b)
    torque_at_startup = helpers_ex2.torque_induced(v_th, r_th, x_th, R2, X2, sync_velocity_radsec, 1)  # s=1 at startup

    # solution for c)
    r2_doubled = R2 * 2
    s_max_at_r2_doubled = helpers_ex2.max_slip_at_max_torque(r_th, x_th, r2_doubled, X2)
    velocity_at_r2_doubled = helpers_ex2.shaft_velocity(sync_velocity_rpm, s_max_at_r2_doubled)
    torque_at_startup_at_r2_doubled = helpers_ex2.torque_induced(v_th, r_th, x_th, r2_doubled, X2, sync_velocity_radsec, 1)  # s=1 at startup

    # solution for d)
    solution_space = 200
    s_values = linspace(0, solution_space, num=solution_space)
    s_values[0] = 0.001  # replacing the first element of s_values from 0 to 0.0001 to avoid zero division

    # Init lists
    shaft_velocity_list = []
    torque_list_r2 = []
    torque_list_doubled_r2 = []

    for i in s_values:
        shaft_velocity = helpers_ex2.shaft_velocity(sync_velocity_rpm, i/solution_space)
        torque_r2 = helpers_ex2.torque_induced(v_th, r_th, x_th, R2, X2, sync_velocity_radsec, i/solution_space)
        torque_r2_doubled = helpers_ex2.torque_induced(v_th, r_th, x_th, r2_doubled, X2, sync_velocity_radsec, i/solution_space)
        shaft_velocity_list.append(shaft_velocity)
        torque_list_r2.append(torque_r2)
        torque_list_doubled_r2.append(torque_r2_doubled)

    # Print results
    print("Resultados:\n")

    # print(f"V_TH: {v_th:.2f}")
    # print(f"Z_TH: {z_th:.2f}\n")

    print(f"a). - Par máximo                  -> T_max: {torque_max:.2f} Nm.")
    print(f"    - Deslizamiento en par máximo -> s_max: {s_max:.4f}.")
    print(f"    - Velocidad en par máximo     -> N_m @T_max: {velocity_at_torque_max:.2f} rpm\n")

    print(f"b). Par en el arranque -> T en arranque: {torque_at_startup:.2f} Nm.\n")

    print(f"c). Si se duplica R2 (2R2: {r2_doubled} ohms),el deslizamiento se duplica,\n    al cual se presenta el par máximo:")
    print(f"    - Deslizamiento duplicando R2          -> s_max @2R2: {s_max_at_r2_doubled:.4f}.")
    print(f"    - Velocidad del rotor con 2R2          -> N_m @2R2: {velocity_at_r2_doubled:.2f} rpm.")
    print(f"    - El torque máximo no depende de R2    -> T_max: {torque_max:.2f} Nm.")
    print(f"    - Torque al arranque del rotor con 2R2 -> T_arranque @2R2: {torque_at_startup_at_r2_doubled:.2f} Nm.")

    plt.plot(shaft_velocity_list, torque_list_r2, label=r"$R_2$ original")
    plt.plot(shaft_velocity_list, torque_list_doubled_r2, '-.', label=r"$R_2$ doble")
    plt.plot(shaft_velocity_list, [torque_max]*solution_space, '--', label=fr"$\tau_{{máx}}={torque_max:.2f}$ Nm", color='red')
    plt.xlabel(r"Velocidad angular $n_m$ (rpm)")
    plt.ylabel(r"Torque inducido $\tau_{ind}$ (Nm)")
    plt.title(r"Característica par-velocidad del motor")
    plt.xlim(left=0, right=1800)
    # plt.ylim(top=250)
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
