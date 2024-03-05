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
