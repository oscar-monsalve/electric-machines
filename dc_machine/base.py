from abc import ABC, abstractmethod


class DCMachine(ABC):  # Inherit from the abc module (Abstract Base Classses)
    '''
    Abstract base class for DC machines.

    Supports both motor and generator operation modes.
    '''

    VALID_MODES = ("motor", "generator")

    def __init__(
        self,
        armature_resistance: float,
        shunt_resistance: float,
        series_resistance: float,
        supply_voltage: float,
        speed: float,
        flux: float,
        k_constant: float,
        operation_mode: str
    ) -> None:

        if armature_resistance <= 0:
            raise ValueError("Armature resistance must be positive and non-zero.")
        elif shunt_resistance <= 0:
            raise ValueError("Field resistance must be positive and non-zero.")
        elif series_resistance <= 0:
            raise ValueError("Series resistance must be positive and non-zero.")
        elif supply_voltage <= 0:
            raise ValueError("The supply voltage must be positive and non-zero.")
        elif speed <= 0:
            raise ValueError("The machine's speed must be positive and non-zero.")
        elif flux <= 0:
            raise ValueError("The magnetic flux magnitude must be positive and non-zero.")
        elif k_constant <= 0:
            raise ValueError("The machine's constant K must be positive and non-zero.")
        elif operation_mode not in self.VALID_MODES:
            raise ValueError(f"Must provide one of the operation modes: {self.VALID_MODES}")

        self.armature_resistance = armature_resistance
        self.shunt_resistance = shunt_resistance
        self.series_resistance = series_resistance
        self.supply_voltage = supply_voltage
        self.speed = speed
        self.flux = flux
        self.k_constant = k_constant
        self.operation_mode = operation_mode

    def __str__(self) -> str:
        class_name = type(self).__name__
        indent = "    "
        label_w = 25
        return (
            f"{class_name}:\n"
            f"{indent}{'Armature resistance:':<{label_w}} {self.armature_resistance} Ω\n"
            f"{indent}{'Shunt resistance:':<{label_w}} {self.shunt_resistance} Ω\n"
            f"{indent}{'Series resistance:':<{label_w}} {self.series_resistance} Ω\n"
            f"{indent}{'Supply voltage:':<{label_w}} {self.supply_voltage} V\n"
            f"{indent}{'Speed:':<{label_w}} {self.speed} rpm\n"
            f"{indent}{'Flux:':<{label_w}} {self.flux} Wb\n"
            f"{indent}{'K constant:':<{label_w}} {self.k_constant}\n"
            f"{indent}{'Operation mode:':<{label_w}} {self.operation_mode}\n"
        )

    def back_emf(self) -> float:
        """E = K * Φ * ω"""
        return self.k_constant * self.flux * self.speed

    @abstractmethod
    def field_current(self, terminal_voltage: float) -> float:
        """If = Vt / Rf"""
        ...

    @abstractmethod
    def armature_current(self, terminal_voltage: float, back_emf: float) -> float:
        """Ia = (Vt - E) / Ra"""
        ...

    @abstractmethod
    def terminal_voltage(self, supply_voltage: float, armature_current: float) -> float:
        """For motor: Vt = V - Ia*Ra | For generator: Vt = E - Ia*Ra"""
        ...

    @abstractmethod
    def induced_torque(self, armature_current: float) -> float:
        """T = K * Φ * Ia"""
        ...

    @abstractmethod
    def shaft_speed(
        self,
        terminal_voltage: float,
        armature_resistance: float,
        induced_torque: float
    ) -> float:
        ...
