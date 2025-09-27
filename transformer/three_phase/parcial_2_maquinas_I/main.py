"""
Un transformador trifásico de 500 kVA, con conexión Yd, recibe en el primario una tensión línea a línea
de 13.8 kV. Su relación de transformación simple es 𝑎𝑠 = 10. La impedancia equivalente del transformador referida
al secundario (por fase) es 𝑍𝑒𝑞,f2 = 𝑅𝑒,f2 + 𝑗𝑋e,f2 = 4.2 + 𝑗10 Ω. Las pérdidas trifásicas de vacío son
𝑃0,3𝜙 = 2200 𝑊. De acuerdo con lo anterior determinar:
    a) La tensión de línea del secundario 𝑉𝐿2 .
    b) La corriente de línea del primario 𝐼𝐿1 a plena carga.
    c) La eficiencia y regulación de voltaje del transformador para los siguientes casos:
        - A plena carga nominal para 𝑓𝑝 = 0.9 ↓.
        - Al 50% de la carga nominal para 𝑓𝑝 = 1.
"""

import model

# ---- Input data ----
S_N:   float = 500_000.0   # Nominal power in VA
A_S:   float = 10.0        # Simple transformation ratio
V_L1:  float = 13800.0     # Primary line voltage in V
RE_F2: float = 4.2         # Equivalent resistance refered to the secondary (per phase) in ohms
XE_F2: float = 10.0        # Equivalent reactance refered to the secondary (per phase) in ohms
P_0:   float = 2200.0      # Secondary Open-circuit active power in W

PARTIAL_LOAD: float = 0.5
S_C: list(float) = [S_N, PARTIAL_LOAD*S_N]
F_P: list(float) = [0.9, 1.0]

# S_C1:   float = S_N        # Load's apparent power for full load case
# FP_1:   float = 0.9        # Power factor for full load case
# S_C2:   float = 0.5 * S_N  # Load's apparent power for partial load case
# FP_2:   float = 1.0        # Power factor for full partial load case


def main() -> None:
    vl2 = model.line_voltage_secondary(V_L1, A_S)
    vf2 = vl2
    il1 = model.line_current_primary(S_N, V_L1)
    icf2 = model.load_current_phase(S_C1, vl2)
    phi1 = model.power_factor_angle(FP_1)
    phi2 = model.power_factor_angle(FP_2)
    efficiency_1, p_out, p_cu = model.efficiency(vf2, icf2, phi1, RE_F2, P_0)

    # Print solution
    print(f"a). V_L2 : {vl2:.2f} V.")
    print(f"b). I_L1 : {il1:.2f} A.")
    print(f"angle 1: {phi1:.2f}°.")
    print(f"c). efficiency_1.  : {efficiency_1:.2f} %.")
    print(f"c). p_out : {p_out:.2f} W.")
    print(f"c). p_cu  : {p_cu:.2f} W.")


if __name__ == "__main__":
    main()
