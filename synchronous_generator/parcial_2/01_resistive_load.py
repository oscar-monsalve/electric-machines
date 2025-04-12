import helpers as h


# Input data
LOAD_TYPE:   str = "r"  # "r" or "c" or "l" for resistive, capacitive or inductive load type.
RL_CEDULA: float = 175  # Últimos dos dígitos de la cédula para definir a la impedancia de carga
ZL:      complex = RL_CEDULA + 0j
EA:        float = 2400
RA:        float = 17
XS:      complex = 144j


def main() -> None:
    power_factor_angle = h.power_factor_angle(ZL, LOAD_TYPE)
    print(power_factor_angle)


if __name__ == "__main__":
    main()
