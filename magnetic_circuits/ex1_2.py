"""
La figura 1-8a) muestra un núcleo ferromagnético cuya longitud media es de 40 cm. Hay un pequeño en-
trehierro de 0.05 cm en la estructura del núcleo. El área de la sección transversal del núcleo es de 12 cm2,
la permeabilidad relativa del núcleo es de 4 000 y la bobina de alambre en el núcleo tiene 400 vueltas. Su-
ponga que el efecto marginal en el entrehierro incrementa 5% la sección transversal efectiva del entrehie-
rro. Dada esta información, encuentre a) la reluctancia total del camino del flujo (hierro más entrehierro)
y b) la corriente requerida para producir una densidad de flujo de 0.5 T en el entrehierro.
"""

import numpy as np

# Number of turns
N = 400

# Permeabilities (H/m)
u_r = 4000  # Relative
u_0 = 4 * np.pi * (10**-7)  # Space

# lengths (m)
l_n = 0.4
l_eh = 0.0005

# Areas (m^2)
a_n = 0.0012
a_eh = 0.0012 * 1.05  # Marginal effect of 5% included to the core area

# Magnetic flux required at entrehierro (Wb/m^2)
b_eh = 0.5

# Solution for literal a)
r_n = l_n / (a_n * u_r * u_0)  # Core reluctance
r_eh = l_eh / (a_eh * u_0)  # Entrehierro reluctance
r_eq = r_n + r_eh  # Equivalent reluctance

##############################################################################

# Solutions for literal b)

# First solution
i_1 = (b_eh * a_eh * r_eq) / N

# Second solution
# Calculate the circuit's magnetic flux
phi = b_eh * a_eh  # (Wb/m^2)

# Calculate the magnetic flux density
b_n = phi / a_n
b_eh = phi / a_eh

i_2 = (1/(u_0 * N)) * (((b_n * l_n)/(u_r)) + (b_eh * l_eh))

##############################################################################

# Print results
print("Reluctances (A-turn/Wb):")
print(f"{r_n:.4f} (core)")
print(f"{r_eh:.4f} (entrehierro)")
print(f"{r_eq:.4f} (equivalent)\n")

print(f"The circuit's magnetic flux is:{phi:.5f} Wb\n")

print("Magnetic flux densities (Wb/m^2):")
print(f"b_n:{b_n:.4f} (core)")
print(f"b_eh:{b_eh:.4f} (entrehierro)\n")

print("Current required:")
print(f"i (first method):{i_1:.4f} A")
print(f"i (second method):{i_2:.4f} A")
