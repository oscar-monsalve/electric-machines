from base import DCMachine


class SeparatelyExcitedMotorGenerator(DCMachine):
    def field_current(self) -> float:
        ...

    def armature_current(self) -> float:
        ...

    def voltage_at_terminals(self) -> float:
        ...

    def shaft_speed(self, voltage_at_terminals: float, armature_resistance: float, induced_torque: float) -> float:
        ...
