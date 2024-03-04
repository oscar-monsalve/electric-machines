import numpy as np
import functions as fn


# Exercise data
# Motor data
line_voltage = 440  # V
field_rpm = 1800
fp = 0.8

# Resistances (Ohm)
r_1 = 1.5
r_2 = 1.2
r_m = 900

# Reactances
jx = complex(0, 6)  # total
jx_m = complex(0, 110)

# Slip
s = 0.2

########################################################

# Solution
# Preliminars
phase_voltage, r_l, z_eq = fn.preliminars(line_voltage, r_2, s, r_1, jx)

# a) Rotor velocity
rotor_rpm = fn.rotor_velocity(s, field_rpm)

# b) Rotor current
i_r, i_r_polar = fn.rotor_current(phase_voltage, z_eq)

# c) Rotor power == output power
p_r = fn.rotor_power(i_r_polar, r_l)

# d) Torque
t = fn.torque(rotor_rpm, p_r)

# e) Motor efficiency
eta, i_en_polar = fn.motor_efficiency(phase_voltage, r_m, jx_m, i_r, p_r, fp)

########################################################

# Print results
print(f"a) The rotor velocity is: {rotor_rpm} rpm")
print(f"b) The rotor current is: ({i_r_polar[0]} < {np.degrees(i_r_polar[1])}°) A")
print(f"c) The rotor power (output power) is: {p_r} W")
print(f"d) The rotor torque is: {t} Nm")
print(f"e) The motor efficiency is: {eta} %")
