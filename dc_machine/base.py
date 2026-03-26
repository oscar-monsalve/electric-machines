from abc import ABC, abstractmethod


class DCMachine(ABC):  # Inherit from the abc module (Abstract Base Classses)
    '''
    Abstract base class for DC machines.

    Supports both motor and geneator operation modes.
    '''

    VALID_MODES = ("motor", "generator")

    def __init__(
        self,
        armature_resistance: float,
        field_resistance: float,
        supply_voltage: float,
        speed: float,
        flux: float,
        k_constant: float,
        operation_mode: str
    ) -> None:

        if armature_resistance <= 0:
            raise ValueError("Armature resistance must be positive and non-zero.")
        elif field_resistance <= 0:
            raise ValueError("Field resistance must be positive and non-zero.")
        elif supply_voltage <= 0:
            raise ValueError("The supply voltage must be positive and non-zero.")
        elif speed <= 0:
            raise ValueError("The machine's speed must be positive and non-zero.")
        elif flux <= 0:
            raise ValueError("The magnetic flux magnitud must be positive and non-zero.")
        elif k_constant <= 0:
            raise ValueError("The machine's constant K must be positive and non-zero.")
        elif operation_mode not in self.VALID_MODES:
            raise ValueError(f"Must provide of the operation modes of {self.VALID_MODES}")

        self.armature_resistance = armature_resistance
        self.field_resistance = field_resistance
        self.supply_voltage = supply_voltage
        self.speed = speed
        self.flux = flux
        self.operaiton_mode = operation_mode

    @abstractmethod
    def armature_current(self) -> float:
        ...

    @abstractmethod
    def field_current(self) -> float:
        ...

    @abstractmethod
    def voltage_at_terminals(self) -> float:
        ...

    @abstractmethod
    def shaft_speed(self, voltage_at_terminals: float, armature_resistance: float, induced_torque: float) -> float:
        ...
