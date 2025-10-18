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
from numpy import linspace
from math import sqrt

def main() -> None:
    # Input data
    VOLTAGE_NOM: float = 480  # Nominal voltage in V
    CURRENT_NOM: float = 60   # Nominal armature current in A
    RA:          float = 0.0  # Armature resistance in ohms
    XS:          float = 1    # Synchronous reactance in ohms

    # Load conditions
    pf_loads: [float, str] = [
        0.8, "lagging",
        0.8, "leading"
    ]

    pf_sign_list = [
        model.power_factor_sign(pf_loads[1], pf_loads[0]),
        model.power_factor_sign(pf_loads[3], pf_loads[2])
    ]

    # pf angles in degrees for the different loads
    pf_angle_list = [
        model.power_factor_angle(pf_sign_list[0]),
        model.power_factor_angle(pf_sign_list[1])
    ]

    jxs = model.complex_reactance(XS)
    ra = model.complex_resistance(RA)
    ea = VOLTAGE_NOM / sqrt(3)

    # Due to the star connection, I_A = I_load
    ia_range = linspace(50, CURRENT_NOM, 10)
    for ia_indx, ia_value in enumerate(ia_range):
        pass


if __name__ == "__main__":
    main()
