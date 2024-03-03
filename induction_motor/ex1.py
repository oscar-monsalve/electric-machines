import numpy as np
import cmath

import functions as fn


# Exercise data

# Motor data
line_voltage = 440  # V
field_rpm = 1800

# Resistances (Ohm)
r_1 = 1.5
r_2 = 1.2
r_m = 900

# Reactances
jx = complex(0, 6)  # total
jx_m = complex(0, 110)

# Slip
s = 0.2

# Solution

# Preliminars
phase_voltage = complex(line_voltage / np.sqrt(3), 0)  # Phase voltage
r_l = r_2 / s  # Load resistance
z_eq = r_1 + jx + r_l  # Equivalent impedance

# a) Rotor velocity
rotor_rpm = fn.rotor_velocity(s, field_rpm)

# b) Rotor current
i_r = phase_voltage / z_eq
i_r_polar = cmath.polar(i_r)

# c) Rotor power == output power
p_r = 3 * i_r_polar[0]**2 * r_l

# d) Torque
omega = rotor_rpm * (2 * np.pi / 60)  # rad/s
t = p_r / omega

# e) Motor efficiency


# __________________________________

# Print results
print(f"a) The rotor velocity is: {rotor_rpm} rpm")
print(f"b) The rotor current is: ({i_r_polar[0]} < {np.degrees(i_r_polar[1])}°) A")
print(f"c) The rotor power (output power) is: {p_r} W")
print(f"d) The rotor torque is: {t} Nm")
