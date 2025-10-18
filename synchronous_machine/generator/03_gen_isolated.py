# Solución de ejercicios de la clase "Generador síncrono en operación aislada"
# Solución para el ejercicio 3 con base en el ejercicio 2.

# ---- Ejercicio 2 ----
# Un generador síncrono con seis polos de 480 V, a 50 Hz, conectado en Y, tiene una reactancia síncrona
# por fase de 1.0 Ω. Su corriente de inducido a plena carga es de 60 A con un factor de potencia de 0.8
# en retraso. Este generador tiene pérdidas por fricción y por rozamiento con el aire por 1.5 kW y
# pérdidas en el núcleo por 1.0 kW a 60 Hz a plena carga. Debido a que se desprecia la resistencia del
# inducido, se supone que las pérdidas I2R son insignificantes. La corriente de campo está ajustada de
# tal manera que el voltaje en las terminales es igual a 480 V en vacío.

# ---- Ejercicio 2 ----
# Suponga que el generador del ejemplo 4-3 opera en vacío con un voltaje en las terminales de 480 V.
# Haga la gráfica de la característica de las terminales (el voltaje en las terminales y la corriente de
# línea) de este generador conforme varía la corriente en su inducido desde vacío hasta plena carga con
# un factor de potencia:
#    a) de 0.8 en retraso.
#    b) de 0.8 en adelanto.
#
# Suponga que la corriente de campo permanece constante.

import helpers_generator as model
import matplotlib.pyplot as plt
from numpy import linspace, sqrt
import scienceplots
plt.style.use(["science", "notebook", "grid"])

def main() -> None:
    # Input data
    VOLTAGE_NOMINAL: float = 480  # Nominal voltage in V
    CURRENT_NOMINAL: float = 60   # Nominal armature current in A
    XS:              float = 1    # Synchronous reactance in ohms
    CONNECTION:        str = "star"  # start or delta of the generator

    ea = VOLTAGE_NOMINAL / sqrt(3)

    # Load conditions
    pf_loads: [float, str] = [
        0.8, "lagging",
        0.8, "leading"
    ]

    # pf angles for the different loads in degrees
    pf_angle_list: [float] = [
        model.power_factor_angle(pf_loads[0], pf_loads[1]),
        model.power_factor_angle(pf_loads[2], pf_loads[3])
    ]

    # Due to the star connection, I_A = I_load
    vt_lagging = []
    vt_leading = []
    ia_range = linspace(0, CURRENT_NOMINAL, 100)

    # V_T calculation for the inductive load
    for ia_value in ia_range:
        vt_indx = model.voltage_at_terminals_if_no_ra(
            ea, ia_value, XS, pf_angle_list[0], pf_loads[1], CONNECTION
        )
        vt_lagging.append(vt_indx)

    # V_T calculation for the capacitive load
    for ia_value in ia_range:
        vt_indx = model.voltage_at_terminals_if_no_ra(
            ea, ia_value, XS, pf_angle_list[0], pf_loads[3], CONNECTION
        )
        vt_leading.append(vt_indx)

    # Plots
    plt.plot(ia_range, vt_lagging, label=r"fp = 0.8↓ (lagging)")
    plt.plot(ia_range, vt_leading, label=r"fp = 0.8↑ (leading)")
    plt.xlabel(r"Load current $I_L$ (A)")
    plt.ylabel(r"Voltage ar terminal $V_T$ (V)")
    plt.title(r"Terminal characteristic plots - Isolated Synchronous generator")
    plt.legend()
    # plt.xlim(left=3.5, right=6)
    # plt.ylim(top=250)
    # plt.tight_layout()
    # plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
