from base import DCMachine


class ShuntMotorGenerator(DCMachine):
    """Shunt: field winding in parallel with armature.

    It is required to provide the shunt winding resistance.

    It is optional to provide the series winding resistance.
    """

    def validate_resistance(self) -> None:
        if self.shunt_resistance is None:
            raise ValueError("Shunt machine requires shunt_resistance in ohms.")
        elif self.shunt_resistance <= 0:
            raise ValueError("Shunt resistance must be positive and non-zero.")

    def field_current(self, applied_field_voltage: float) -> float:
        """If = Vt / Rf"""
        raise NotImplementedError("field_current is not implemented yet for shunt machine.")

    def armature_current(self, terminal_voltage: float, induced_emf: float) -> float:
        """Ia = (Vt - E) / Ra"""
        raise NotImplementedError("armature_current is not implemented yet for shunt machine.")

    def terminal_voltage(self, armature_current: float) -> float:
        """For motor: Vt = V - Ia*Ra | For generator: Vt = E - Ia*Ra"""
        raise NotImplementedError("terminal_voltage is not implemented yet for shunt machine.")

    def induced_torque(self, armature_current: float) -> float:
        """T = K * Φ * Ia"""
        raise NotImplementedError("induced_torque is not implemented yet for shunt machine.")

    def shaft_speed_rpm(self, terminal_voltage: float, armature_current: float) -> float:
        raise NotImplementedError("shaft_speed_rpm is not implemented yet for shunt machine.")
