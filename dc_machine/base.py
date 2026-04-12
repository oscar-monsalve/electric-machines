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
        supply_voltage: float,
        speed: float,
        flux: float,
        k_constant: float,
        operation_mode: str,
        shunt_resistance: float | None = None,
        series_resistance: float | None = None,
    ) -> None:

        if armature_resistance <= 0:
            raise ValueError("Armature resistance must be positive and non-zero.")
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
        self.supply_voltage = supply_voltage
        self.speed = speed
        self.flux = flux
        self.k_constant = k_constant
        self.shunt_resistance = shunt_resistance
        self.series_resistance = series_resistance
        self.operation_mode = operation_mode

        self.validate_resistance()

    def __str__(self) -> str:
        class_name = type(self).__name__
        indent = "    "
        label_w = 25

        lines = [f"{class_name}:"]
        lines.append(f"{indent}{'Armature resistance:':<{label_w}} {self.armature_resistance} Ω")

        if self.shunt_resistance is not None:
            lines.append(f"{indent}{'Shunt resistance:':<{label_w}} {self.shunt_resistance} Ω")

        if self.series_resistance is not None:
            lines.append(f"{indent}{'Series resistance:':<{label_w}} {self.series_resistance} Ω")

        lines.append(f"{indent}{'Supply voltage:':<{label_w}} {self.supply_voltage} V")
        lines.append(f"{indent}{'Speed:':<{label_w}} {self.speed} rpm")
        lines.append(f"{indent}{'Flux:':<{label_w}} {self.flux} Wb")
        lines.append(f"{indent}{'K constant:':<{label_w}} {self.k_constant}")
        lines.append(f"{indent}{'Operation mode:':<{label_w}} {self.operation_mode}\n")

        return "\n".join(lines)

    def induced_emf(self) -> float:
        """Calculates the induced electromotive force "emf".

        Returns the emf in volts using the equation: E = K * Φ * ω.

        Where:
            K: Machine constant (includes unit conversion factor).
            Φ: Magnetic flux per pole in webers (Wb).
            ω: Angular speed in rpm (K is assumed to include the 60/(2π) conversion).

        Note:
            The constant K must be consistent with the speed unit used:
            - If speed is in rpm, K must include the 60/(2π) factor.
            - If speed is in rad/s, K is the pure machine constant (P·Z·N / 60·A).

        Returns:
            The induced emf in volts.
        """
        return self.k_constant * self.flux * self.speed

    @abstractmethod
    def validate_resistance(self) -> None:
        """Validates if the machine has the required resistances configured."""
        ...

    @abstractmethod
    def field_current(self, terminal_voltage: float) -> float:
        """If = Vt / Rf"""
        ...

    @abstractmethod
    def armature_current(self, terminal_voltage: float, induced_emf: float) -> float:
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
