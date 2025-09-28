"""
Un transformador trifásico de 100 MVA, con conexión Yd, recibe en el primario una tensión línea a línea
de 230 kV. Su relación de transformación simple es 𝑎𝑠 = 3.46. La impedancia equivalente del transformador referida
al secundario (por fase) es 𝑍𝑒𝑞,f2 = 𝑅𝑒,f2 + 𝑗𝑋e,f2 = 2 + 𝑗7.98 Ω. Las pérdidas trifásicas de vacío son
𝑃0,3𝜙 = 1.08 M𝑊. De acuerdo con lo anterior determinar:
    a) La tensión de línea del secundario 𝑉𝐿2 .
    b) La corriente de línea del primario 𝐼𝐿1 a plena carga.
    c) La eficiencia y regulación de voltaje del transformador para los siguientes casos:
        - A plena carga nominal para 𝑓𝑝 = 0.9 ↓.
        - Al 50% de la carga nominal para 𝑓𝑝 = 1.
"""

import model

# ---- Variable data ----
pf:            [float] = [0.7, 0.4]  # Load's power factor cases
load_percentage: float = 0.9         # Load's percentage of nominal apparent power

# ---- Constant data ----
S_N:   float = 100_000_000.0               # Nominal power in VA
A_S:   float = 3.46                        # Simple transformation ratio
V_L1:  float = 230_000                     # Primary line voltage in V
RE_F2: float = 2                           # Equivalent resistance refered to the secondary (per phase) in ohms
XE_F2: float = 7.98                        # Equivalent reactance refered to the secondary (per phase) in ohms
P_0:   float = 1_080_000                   # Secondary Open-circuit active power in W
S_C: [float] = [S_N, load_percentage*S_N]  # Load percentage cases


def main() -> None:
    vl2 = model.line_voltage_secondary(V_L1, A_S)
    vf2 = vl2
    il1 = model.line_current_primary(S_N, V_L1)

    phi_list = []
    icf2_list = []
    efficiency_list = []
    v20_list = []
    regulation_list = []

    for i in pf:
        phi_i = model.power_factor_angle(i)
        phi_list.append(phi_i)

    for i in S_C:
        icf2_i = model.load_current_phase(i, vl2)
        icf2_list.append(icf2_i)

    for i, _ in enumerate(S_C):
        efficiency_i = model.efficiency(vf2, icf2_list[i], phi_list[i], RE_F2, P_0)
        v20_i = model.open_circuit_voltage_secondary(vf2, icf2_list[i], phi_list[i], RE_F2, XE_F2)
        regulation_i = model.voltage_regulation(v20_i, vf2)
        efficiency_list.append(efficiency_i)
        v20_list.append(v20_i)
        regulation_list.append(regulation_i)

    # Print solution
    print(f"a). V_L2 : {vl2:.2f} V.")
    print(f"b). I_L1 : {il1:.2f} A.")
    print(f"c). Efficiency and voltage regulation for S_C = {S_C[0]:,} VA (fp={pf[0]}):")
    print(f"    - η: {efficiency_list[0]:.2f}%.")
    print(f"    - %ΔV: {regulation_list[0]:.2f}% (V_20 = {v20_list[0]:.2f} V).")
    print(f"c). Efficiency and voltage regulation for S_C = {S_C[1]:,} VA (fp={pf[1]}):")
    print(f"    - η: {efficiency_list[1]:.2f}%.")
    print(f"    - %ΔV: {regulation_list[1]:.2f}% (V_20 = {v20_list[1]:.2f} V).")


if __name__ == "__main__":
    main()
