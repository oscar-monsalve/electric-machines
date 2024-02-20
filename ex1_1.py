"""
En la figura 1-7a) se observa un núcleo ferromagnético. Tres lados de este núcleo tienen una anchura
uniforme, mientras que el cuarto es un poco más delgado. La profundidad del núcleo visto es de 10 cm
(hacia dentro de la página), mientras que las demás dimensiones se muestran en la figura. Hay una bobina
de 200 vueltas enrollada sobre el lado izquierdo del núcleo. Si la permeabilidad relativa mr es de 2 500,
¿qué cantidad de flujo producirá una corriente de 1 A en la bobina?
"""

import numpy as np

# Available data

i = 1  # current in A
N = 200  # number of turns
depth = 0.1  # Core depth in m
l1 = (7.5 + 30 + 7.5)/100  # Average length at streched path in m
l2 = (2*(5 + 30 + 7.5) + 45)/100  # Average length at widest path in m
a1 = (10 * 10) / 100**2  # Cross-sectional area of streched path in m^2
a2 = (15 * 10) / 100**2  # Cross-sectional area of widest path in m^2
mu = 2500 * 4 * np.pi * 10**-7  # Material permeability in H/m

# Reluctances calculation

r1 = l1 / (a1 * mu)
r2 = l2 / (a2 * mu)
r_eq = r1 + r2

# Magnetic flux phi

f = N * i
phi = f / r_eq

# Print vaues

print(f"- The average lengths of the streched and widest paths are l1: {l1} m, l2: {l2} m, respectively.")
print(f"- The reluctances are R1: {r1:.4f} and R2: {r2:.4f} in H/m.")
print(fr"- The magnetic flux is phi: {phi:.4f} Wb.")
