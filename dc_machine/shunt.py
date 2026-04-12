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

    def field_current(self, terminal_voltage: float) -> float:
        """If = Vt / Rf"""
        ...

    def armature_current(self, terminal_voltage: float, induced_emf: float) -> float:
        """Ia = (Vt - E) / Ra"""
        ...

    def terminal_voltage(self, supply_voltage: float, armature_current: float) -> float:
        """For motor: Vt = V - Ia*Ra | For generator: Vt = E - Ia*Ra"""
        ...

    def induced_torque(self, armature_current: float) -> float:
        """T = K * Φ * Ia"""
        ...

    def shaft_speed(
        self,
        terminal_voltage: float,
        armature_resistance: float,
        induced_torque: float
    ) -> float:
        ...
