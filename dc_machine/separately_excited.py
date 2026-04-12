from base import DCMachine


class SeparatelyExcitedMotorGenerator(DCMachine):
    """Separately excited: field current is externally controlled.

    It is required to provide the shunt winding resistance.

    It is optional to provide the series winding resistance.
    """

    def validate_resistance(self) -> None:
        if self.shunt_resistance is None:
            raise ValueError("Separately excited machine requires shunt_resistance in ohms.")
        elif self.shunt_resistance <= 0:
            raise ValueError("Shunt resistance must be positive and non-zero.")

    def field_current(self, field_voltage: float) -> float:
        """Calculates the field current for the separately excited machine using the equation: If = Vf / Rf.

        Args:
            field_voltage: External DC voltage supplying the shunt winding ().

        Returns:
            Separately excited field current in amps.
        """

        return field_voltage / self.shunt_resistance

    def armature_current(self, terminal_voltage: float, induced_emf: float) -> float:
        """Calculates the armature current with the following equations:
             Motor: Ia = (Vt - E) / Ra
             Generator: Ia = (E - Vt) / Ra

        Args:
            terminal_voltage: output voltage (generator) or input voltage (motor) at terminal in volts.
            induced_emf: emf (motor) or back-emf (generator) in volts.

        Returns:
            The armature current in amps depending the machine operating mode (motor or generator).
        """

        return self._current_sign() * (terminal_voltage - induced_emf) / self.armature_resistance

    def terminal_voltage(self, nominal_voltage: float, armature_current: float) -> float:
        """For motor: Vt = V - Ia*Ra | For generator: Vt = E - Ia*Ra"""
        if self.operation_mode == "motor":
            return nominal_voltage - armature_current * self.armature_resistance
        else:  # generator
            return self.induced_emf() - armature_current * self.armature_resistance

    def induced_torque(self, armature_current: float) -> float:
        """T = (E * Ia) / ω
        Args:
            armature_current: armature current (rotor current) in amps.
        Returns:
            The induced torque in Nm.
        """
        return (self.induced_emf() * armature_current) / self.speed
        ...

    def shaft_speed(
        self,
        terminal_voltage: float,
        armature_resistance: float,
        induced_torque: float
    ) -> float:
        ...
