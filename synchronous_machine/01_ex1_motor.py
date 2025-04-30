import helpers_motor as model

# Un motor síncrono 208 V, 45 hp, un factor de potencia de 0.8 en adelanto, conec-
# tado en delta, a 60 Hz, alimenta a una carga de 15 hp con un factor de potencia inicial de 0.85 en retraso. La
# corriente de campo IF en estas condiciones es de 4.0 A.
#   a) Dibuje el diagrama fasorial inicial del motor y encuentre los valores de IA y EA.
#   b) Dibuje el nuevo diagrama fasorial del motor si se incrementara el flujo del motor en 25%. ¿Cuál es el
#   valor de IA y EA y el factor de potencia del motor en este momento?
#   c) Suponga que el flujo en el motor varía linealmente con la corriente de campo IF. Haga una gráfica de
#   IA contra IF del motor síncrono con una carga de 15 hp.

# ---Inputs----
FP:         float = 0.8
TYPE_OF_LOAD: str = "lagging"
VOLTAJE: float = 208
# ---Inputs----


def main() -> None:
    fp_angle = model.power_factor_angle(FP, TYPE_OF_LOAD)

    print(f"{fp_angle:.2f}")


if __name__ == "__main__":
    main()
