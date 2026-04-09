from base import DCMachine


class ShuntMotorGenerator(DCMachine):
    def field_current(self, terminal_voltage: float) -> float:
        """If = Vt / Rf"""
        ...

    def armature_current(self, terminal_voltage: float, back_emf: float) -> float:
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
