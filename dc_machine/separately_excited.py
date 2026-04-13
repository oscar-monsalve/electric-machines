from base import DCMachine
from utils import rpm_to_rad_s


class SeparatelyExcitedMotorGenerator(DCMachine):
    """Separately excited (motor/generator): field current is externally controlled.

    It is required to provide the shunt winding resistance.

    Optional:
        Series winding resistance in ohms.
        Brush drop voltage Vb in volts.

    Convention used in this class:
        - E = K * flux * speed_rpm
        - T = (E * Ia) / omega, with omega = rpm_to_rad_s(speed_rpm)
        - Therefore K must be calibrated for the rpm-based emf equation.

    Assumptions kept for now:
    - Linear magnetics (no saturation)
    - No armature reaction
    - Constant flux (externally controlled field)
    """

    def validate_resistance(self) -> None:
        if self.shunt_resistance is None:
            raise ValueError("Separately excited machine requires shunt_resistance in ohms.")
        elif self.shunt_resistance <= 0:
            raise ValueError("Shunt resistance must be positive and non-zero.")

    def field_current(self, applied_field_voltage: float) -> float:
        """Calculates the field current for the separately excited machine using the equation: If = Vf / Rf.

        Args:
            applied_field_voltage: External DC voltage supplying the shunt winding.

        Returns:
            Field circuit current in amps.
        """

        return applied_field_voltage / self.shunt_resistance

    def armature_current(self, terminal_voltage: float, induced_emf: float) -> float:
        """Calculates the armature current with optional brush voltage drop (Vb).
             Motor:     Ia = (Vt - E - Vb) / Ra
             Generator: Ia = (E - Vt - Vb) / Ra

        Args:
            terminal_voltage: output voltage (generator) or input voltage (motor) at terminals in volts.
            induced_emf: emf (motor) or back-emf (generator) in volts.

        Returns:
            The armature current in amps depending the machine operating mode (motor or generator).
        """
        vb = self._brush_drop_value()
        return (self._current_sign() * (terminal_voltage - induced_emf) - vb) / self.armature_resistance

    def terminal_voltage(self, armature_current: float) -> float:
        """Terminal voltage with optional brush voltage drop.
            Motor:     Vt = Vnom - Ia*Ra - Vb
            Generator: Vt = E - Ia*Ra - Vb

        Args:
            armature_current: armature current (rotor current) in amps.

        Returns:
            The voltage at terminals in volts.
        """
        vb = self._brush_drop_value()

        if self.operation_mode == "motor":
            return self.nominal_voltage - (armature_current * self.armature_resistance) - vb
        else:  # generator
            return self.induced_emf() - (armature_current * self.armature_resistance) - vb

    def induced_torque(self, armature_current: float) -> float:
        """T = (E * Ia) / ω
        Args:
            armature_current: armature current (rotor current) in amps.
        Returns:
            The induced torque in Nm.
        """
        omega = rpm_to_rad_s(self.speed_rpm)
        if omega == 0:
            raise ValueError("speed_rpm cannot be zero when computing torque.")
        return (self.induced_emf() * armature_current) / omega

    def shaft_speed_rpm(self, terminal_voltage: float, armature_current: float) -> float:
        """Solve speed from electrical equation with optional brush drop.
        Motor:     E = Vt - Ia*Ra - Vb
        Generator: E = Vt + Ia*Ra + Vb
        and E = K * flux * n_rpm
        """
        k_phi = self.k_constant * self.flux
        if k_phi == 0:
            raise ValueError("k_constant * flux must be non-zero.")

        vb = self._brush_drop_value()
        if self.operation_mode == "motor":
            emf = terminal_voltage - (armature_current * self.armature_resistance) - vb
        else:
            emf = terminal_voltage + (armature_current * self.armature_resistance) + vb

        return emf / k_phi
