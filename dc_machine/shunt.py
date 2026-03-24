from base import DCMachine


class ShuntMotorGenerator(DCMachine):
    def field_current(self) -> float:
        pass

    def armature_current(self) -> float:
        pass

    def voltage_at_terminals(self) -> float:
        pass

    def shaft_speed(self, voltage_at_terminals: float, armature_resistance: float, induced_torque: float) -> float:
        pass
