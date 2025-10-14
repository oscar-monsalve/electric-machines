# Ejercicios 2 y 3 de la clase "Generador síncrono en operación aislada"

# Ejercicio 2:
# Un generador síncrono con seis polos de 480 V, a 50 Hz, conectado en Y, tiene una reactancia síncrona
# por fase de 1.0 Ω. Su corriente de inducido a plena carga es de 60 A con un factor de potencia de 0.8
# en retraso. Este generador tiene pérdidas por fricción y por rozamiento con el aire por 1.5 kW y
# pérdidas en el núcleo por 1.0 kW a 60 Hz a plena carga. Debido a que se desprecia la resistencia del
# inducido, se supone que las pérdidas I2R son insignificantes. La corriente de campo está ajustada de
# tal manera que el voltaje en las terminales es igual a 480 V en vacío.
#   a) ¿Cuál es la velocidad de rotación de este generador?
#   b) Si se cumplen los siguientes supuestos, ¿cuál es el voltaje en las terminales del generador?
#      1. Está cargado con una corriente nominal con un factor de potencia de 0.8 en retraso.
#      2. Está cargado con una corriente nominal con un factor de potencia de 1.0.
#      3. Está cargado con una corriente nominal con un factor de potencia de 0.8 en adelanto.
#   c) ¿Cuál es la eficiencia del generador (desprecie las pérdidas eléctricas) cuando opera a corriente
#      nominal con un factor de potencia de 0.8 en retraso?
#   d) ¿Cuánto par del eje debe aplicar el motor principal a plena carga? ¿Qué tan grande es el par
#      opositor inducido?
#   e) ¿Cuál es la regulación de voltaje de este generador con un factor de potencia de 0.8 en retraso?
#      ¿Y con un factor de potencia de 1.0? ¿Y con un factor de potencia de 0.8 en adelanto?

import helpers_generator as model

def main() -> None:
    # Input data
    VOLTAGE:     float = 480  # Nominal voltage in V.
    FREQ:        int = 50  # Frequency in Hz.
    P:           int = 6  # Number of poles.
    XS:          float = 1  # Synchronous reactance in ohms.
    FP:          float = 0.8  # Lagging power factor.
    LOAD:        str = "lagging"
    CONNECTION:  str = "delta"
    I_LOAD:      float = 1200  # Load current in amps.
    P_MECH_MISC: float = 40000  # Mechanical and miscellaneous losses in W.
    P_CORE:      float = 30000  # Core losses in W.

    # voltage drops at RA and JXS
    jxs = model.complex_reactance(XS)
    ra = model.complex_resistance(RA)

if __name__ == "__main__":
    main()
