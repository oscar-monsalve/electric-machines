import numpy as np
# import cmath


def power_factor_sign(type_of_load: str, fp: float) -> float:
    if type_of_load == "lagging":
        return fp * -1
    if type_of_load == "leading":
        return fp


def power_factor_angle(fp: float) -> float:
    if fp < 0:
        return np.rad2deg(np.arccos(fp)) - 180
    if fp >= 0:
        return np.rad2deg(np.arccos(fp))
