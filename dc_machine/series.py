from base import DCMachine


class SeriesMotorGenerator(DCMachine):
    """Series DC machine: field winding in series with armature.

    Characteristics: High starting torque, poor speed regulation.
    Field current equals armature current.
    """

    def field_current(self, terminal_voltage: float) -> float:
        """If = Vt / (RArmature + RFSeries)"""
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
