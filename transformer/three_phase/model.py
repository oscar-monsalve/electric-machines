from math import cos, sin, acos, sqrt


def voltage_level_from_connection(primary_connection: int,
                                  secondary_connection: int,
                                  vl1: float,
                                  vl2: float) -> float:
    if primary_connection == 1 and secondary_connection == 1:
        pass

def transformation_ratio_simple(vf1: float, vf2: float) -> float:
    return vf1 / vf2

def transformation_ratio_complex(vl1: float, vl2: float) -> float:
    return vl1 / vl2
