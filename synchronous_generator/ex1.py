import numpy as np
import math_model as model
import cmath


"""
A 480 V, 60 Hz, 4-pole, delta-connected, synchronous generator has a synchronous reactance of 0.1 Ω and an
armature resistance of 0.015 Ω.

a. What is the speed of the generator?
b. If a load is connected in delta drawing 1200 A with fp= 0.8 in lagging, how much field current is required to
   bring the load voltage to nominal (see the motor magnetization curve).
c. Draw the phasor diagram.
d. If mechanical and miscellaneous losses add up to 40 kW, core losses are 30 kW and field losses are neglected
   what is the efficiency of the generator?
e. Calculate P, Q and S at the load.
f. Induced torque for the load conditions.
g. Applied torque for load conditions.
"""


def main() -> None:
    # Data
    VOLTAGE: float = 480  # Nominal voltage in V.
    FREQ: int = 60  # Frequency in Hz.
    P: int = 4  # Number of poles.
    XS: float = 0.1  # Synchronous reactance in ohms.
    RA: float = 0.015  # Armature resistance in ohms.
    FP: float = 0.8  # Lagging power factor.
    LOAD: int = "lagging"
    CONNECTION: int = "delta"
    I_LOAD: float = 1200  # Load current in amps.

    pf_angle = model.power_factor_angle(model.power_factor_sign(LOAD, FP))

    velocity = model.velocity(FREQ, P)

    i_a_rec, i_a_pol, v_phi = model.armature_current(CONNECTION, I_LOAD, VOLTAGE, pf_angle)

    print(f"The armature current is: {i_a_pol[0]} < {np.rad2deg(i_a_pol[1])}°")


if __name__ == "__main__":
    main()
