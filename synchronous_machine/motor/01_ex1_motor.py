# Un motor síncrono 208 V, 45 hp, conec- tado en delta, a 60 Hz, tiene una reactancia síncrona de j2.5 ohms,
# y una resistencia de armadura despreciable.
# Sus pérdidas por frcción y por rozamiento con el aire son de 1.5 kW y sus pérdidas en el núcleo son de 1 kW.
# El motor alimenta a una carga de 15 hp con un factor de potencia inicial de 0.85 en retraso. La corriente de
# campo IF en estas condiciones es de 4.0 A.
#   a) Dibuje el diagrama fasorial inicial del motor y encuentre los valores de IA y EA.
#   b) Dibuje el nuevo diagrama fasorial del motor si se incrementara el flujo del motor en 25%. ¿Cuál es el
#   valor de IA y EA y el factor de potencia del motor en este momento?
#   c) Suponga que el flujo en el motor varía linealmente con la corriente de campo IF. Haga una gráfica de
#   IA contra IF del motor síncrono con una carga de 15 hp.

import helpers_motor as model
from math import radians
from cmath import rect, polar
from numpy import linspace
import matplotlib.pyplot as plt
import scienceplots
plt.style.use(["science", "notebook", "grid"])

# ---Inputs----
TYPE_OF_LOAD:  str = "lagging"  # "lagging" or "leading"
CONNECTION:    str = "delta"  # "delta" or "star"
FP:          float = 0.85
VOLTAJE:     float = 208
XS:        complex = 2.5j
P_OUT:       float = 15  # in hp
P_MEC:       float = 1500  # in watts
P_CORE:      float = 1000  # in watts
I_FIELD_INITIAL:          float = 4  # field current in amps
I_FIELD_INCREASE: float = 25  # percentage increase of field current
# ---Inputs----


def main() -> None:
    p_out = model.hp2watts(P_OUT)
    p_in = model.input_power(p_out, P_MEC, P_CORE)

    pf_angle = model.power_factor_angle(FP, TYPE_OF_LOAD)
    ia_rec, ia_mag, ia_angle, v_phase = model.initial_armature_current(CONNECTION, VOLTAJE, pf_angle, p_in)
    il = model.line_current(ia_mag, CONNECTION)
    ea1_rec, ea1_mag, ea1_angle = model.initial_ea_voltage(v_phase, ia_rec, XS)

    ea2_mag = model.new_ea_voltage(ea1_mag, I_FIELD_INCREASE)
    ea2_angle = model.new_delta_angle(ea1_mag, ea2_mag, ea1_angle)
    ea2_rec = rect(ea2_mag, radians(ea2_angle))
    ia2_rec, ia2_mag, ia2_angle = model.new_armature_current(v_phase, ea2_rec, XS)
    new_pf = model.power_factor(ia2_angle)
    new_pf_type = ""
    if ia2_angle < 0:
        new_pf_type = "lagging"
    elif ia2_angle >= 0:
        new_pf_type = "leading"

    EA2_SLOPE = ea1_mag / I_FIELD_INITIAL  # EA2 = (EA1/I_FIELD_INITIAL) * i_field_range
    i_field_range = linspace(3.8, 5.8, 50)
    ia_range = []
    for i in i_field_range:
        ea2_mag_i = EA2_SLOPE * i
        ea2_angle_i = model.new_delta_angle(ea1_mag, ea2_mag_i, ea1_angle)
        ea2_rec_i = rect(ea2_mag_i, radians(ea2_angle_i))
        ia2_rec_i = (v_phase - ea2_rec_i) / XS
        ia_range.append(polar(ia2_rec_i)[0])

    print(f"P_out : {p_out:.2f} W.")
    print(f"P_in  : {p_in:.2f} W.")
    print(f"V_phase  : {v_phase.real:.2f} V.\n")

    print(f"a). I_A    : {ia_mag:.2f} A ∠{ia_angle:.2f}°.")
    print(f"    I_L    : {il:.2f} A")
    print(f"    E_A    : {ea1_mag:.2f} A ∠{ea1_angle:.2f}°.")
    print(f"b). E_A2   : {ea2_mag:.2f} V ∠{ea2_angle:.2f}°.")
    print(f"    I_A2   : {ia2_mag:.2f} A ∠{ia2_angle:.2f}°.")
    print(f"    PF2    : {new_pf:.3f} ({new_pf_type}).")

    plt.plot(i_field_range, ia_range, label=r"$R_2$ original")
    plt.xlabel(r"Field current $I_F$ (A)")
    plt.ylabel(r"Armature current $I_A$ (A)")
    plt.title(r"Synchronous motor V-Curve")
    plt.xlim(left=3.5, right=6)
    # plt.ylim(top=250)
    # plt.tight_layout()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
