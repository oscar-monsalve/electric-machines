import matplotlib.pyplot as plt
import math_model as model
import scienceplots
plt.style.use(["science", "notebook", "grid"])


def main() -> None:

    # No-load and blocked (short circuit SC) rotor tests lab data
    I_NO_LOAD: float = 6.5  # A
    V_NO_LOAD: float = 220  # V
    P_NO_LOAD: float = 300  # W
    PF_NO_LOAD: float = 0.9  # Power factor

    I_SC: float = 16  # A
    # V_SC: float = 50  # V
    P_SC: float = 800  # W
    # PF_SC: float = 0.9  # Power factor

    # Additional data
    # FREQ = 60  # Hz
    VEL: float = 1750  # rpm
    loads: list[float] = [0.25, 0.5, 0.75, 1, 1.25, 1.5]

    # Solution
    # Total resistance
    r_e = model.total_resistance(P_SC, I_SC)

    # Rotational losses
    p_r = model.rotation_losses(P_NO_LOAD, I_NO_LOAD, r_e)

    # Copper losses per load, efficiency and torque
    input_power = model.input_power(V_NO_LOAD, I_SC, PF_NO_LOAD)
    p_cu_per_load = []
    eff_per_load = []
    output_power_per_load = []
    torque_per_load = []

    for i in loads:
        # Copper losses per load
        p_cu_i = model.copper_losses_per_load(P_SC, i)

        # efficiency per load
        eff_i = model.efficiency(input_power, i, p_r, p_cu_i)

        # Output power
        output_power_i_watts, output_power_i_hp = model.output_power(input_power, i, p_r, p_cu_i)

        # Torque per load
        torque_i = model.torque(output_power_i_watts, VEL)

        p_cu_per_load.append(p_cu_i)
        eff_per_load.append(eff_i)
        output_power_per_load.append(output_power_i_watts)
        torque_per_load.append(torque_i)

    # Print results
    print(f"The motor total resistance r_e is: {r_e: .2f} ohms.")
    print(f"The rotational losses P_r is: {p_r: .2f} W.")
    print(f"The input power is: {input_power: .2f} W.")

    print("The copper losses, efficiencies, output powers and torques per load are:")
    for load, p_cu, eff, output_power, torque in zip(loads, p_cu_per_load, eff_per_load, output_power_per_load, torque_per_load):
        print(f"    Load: {load} -> P_Cu: {p_cu: .2f} W, eff: {eff: .2f} %, P_out: {output_power: .2f} W, torque: {torque: .2f} Nm")

    # Plotting
    titles = ["Load vs. Copper losses", "Load vs. Efficiency", "Load vs. Output power", "Load vs. Torque"]
    x_label = "Load"
    y_labels = [r"Copper losses $P_{cu}$", r"Efficiency $\eta_M$ (%)", r"Output power $P_{out}$ (W)", r"Torque $T$ (Nm)"]

    for i, y_data in enumerate([p_cu_per_load, eff_per_load, output_power_per_load, torque_per_load]):
        plt.figure()
        plt.plot(loads, y_data)
        plt.title(titles[i])
        plt.xlabel(x_label)
        plt.ylabel(y_labels[i])
        plt.show()


if __name__ == "__main__":
    main()
