"""
La figura 1-9a) muestra un rotor y un estator sencillos de un motor de cd. La longitud media del recorrido
del flujo en el estator es de 50 cm, y el área de su sección transversal es de 12 cm2. La longitud media
correspondiente al rotor es de 5 cm y el área de su sección transversal también es de 12 cm2. Cada entre-
hierro entre el rotor y el estator tiene un ancho de 0.05 cm y el área de su sección transversal (incluyendo
el efecto marginal) es de 14 cm2. El hierro del núcleo tiene una permeabilidad relativa de 2 000, y hay 200
vueltas alrededor del núcleo. Si la corriente en el alambre se ajusta a l A, ¿cuál será la densidad de flujo
resultante en el entrehierro?
"""

import numpy as np


def calculate_reluctance(length, relative_permeability, area, vacuum_permeability=4*np.pi*10**-7):
    """
    Calculates the magnetic reluctance in (H/m)
    """
    return length / (vacuum_permeability * relative_permeability * area)


def calculate_flux(turns, current, eq_reluctance):
    """
    Calculates the magnetic flux in (Wb)
    """
    return (turns * current) / (eq_reluctance)


def calculate_flux_density(flux, area):
    """
    Calculates the flux density in (Wb/m^2) or (T)
    """
    return flux / area


# Exercise data
# Lengths in (m)
l_n = 0.5  # Core
l_r = 0.05  # Rotor
l_eh = 0.0005  # Air gap

# Areas (m^2)
a_n = 0.0012
a_eh = 0.0014

# Turns and current
N = 200  # turns
i = 1  # current (A)

# Relative permeability
muh_r = 2000  # Material
muh_a = 1  # Air

# Solution
# Relucatances
r_n = calculate_reluctance(l_n, muh_r, a_n)  # Core
r_r = calculate_reluctance(l_r, muh_r, a_n)  # Rotor
r_eh = calculate_reluctance(l_eh, muh_a, a_eh)  # Air gap
r_eq = r_n + r_r + (2 * r_eh)

# Equivalent flux
eq_flux = calculate_flux(N, i, r_eq)

# Flux density at air gap
b_eh = calculate_flux_density(eq_flux, a_eh)

print(f"The flux density at the air gap is B_eh: {b_eh} T")
