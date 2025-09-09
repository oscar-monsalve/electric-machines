# Three-phase transformer exercise
# Un transformador de 630kVA 44000/13200V con conexión delta-estrella, se le realizaron las pruebas
# de vacío y de corto circuito y se obtuvieron los resultados expuestos a continuación:
#
# Prueba  Vacío (BT)  Cortocircuito (AT)
# V       13200 V     2641 V
# I       0.357 A     8.27 A
# P       1650 W      6800 W

# Calcular:
# - La relación de transformación simple y compuesta.
# - Los parámetros del circuito equivalente,
# - La regulación y la eficiencia si alimenta una carga que consume el 70% de la potencia nominal, con
#   un factor de potencia de 0.8.

# ---- Transformer's input data ----
S_N:                  float = 630_0000.0  # Nominal power in VA
V_L1:                 float = 44_000.0    # Primary line voltage in V
V_L2:                 float = 13_200.0    # Secondary line voltage in V
V_0:                  float = 13_200.0    # SECONDARY Open-circuit voltage in V
I_0:                  float = 0.375       # SECONDARY Open-circuit current in A
P_0:                  float = 1650.0      # SECONDARY Open-circuit active power in W
V_CC:                 float = 2641.0      # PRIMARY Short-circuit voltage in V
I_CC:                 float = 8.27        # PRIMARY Short-circuit current in A
P_CC:                 float = 6800.0      # PRIMARY Short-circuit active power in W
PRIMARY_CONNECTION:   int = 2             # 1 for star connection, 2 for delta connection
SECONDARY_CONNECTION: int = 1             # 1 for star connection, 2 for delta connection


def main() -> None:
    pass


if __name__ == "__main__":
    main()
