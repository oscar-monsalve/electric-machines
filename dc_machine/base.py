from abc import ABC, abstractmethod


class DCMachine(ABC):  # Inherit from the abc module (Abstract Base Classses)
    '''
    Abstract base class for DC machines.

    DCMachine (abstract base class)
    ├── SeparatelyExcited
    ├── ShuntMotor/Generator
    ├── SeriesMotor/Generator
    └── CompoundMotor/Generator
        ├── CumulativeCompound
        └── DifferentialCompound
    '''

    def __init__(
        self,
        armature_resistance: float,
        field_resistance: float,
        supply_voltage: float,
        speed: float,
    ) -> None:

        if armature_resistance <= 0:
            raise ValueError("Armature resistance must be positive and non-zero.")
        elif field_resistance <= 0:
            raise ValueError("Field resistance must be positive and non-zero.")
        elif supply_voltage < 0:
            raise ValueError("The supply voltage must be positive.")
        elif speed < 0:
            raise ValueError("The motor's speed must be positive.")

        self.armature_resistance = armature_resistance
        self.field_resistance = field_resistance
        self.supply_voltage = supply_voltage
        self.speed = speed

    @abstractmethod
    def armature_current(self) -> float:
        pass

    @abstractmethod
    def field_current(self) -> float:
        pass

    @abstractmethod
    def voltage_at_terminals(self) -> float:
        pass

    @abstractmethod
    def shaft_speed(self, voltage_at_terminals: float, armature_resistance: float, induced_torque: float) -> float:
        pass

    @staticmethod
    def speed_regulation(speed_no_load: float, speed_full_load: float) -> float:
        """
        Calculates the machine's speed regulation as a percentage. Both velocities must have the same units.

        Args:
            speed_no_load: machine's shaft speed at no load in rad/s or rpm.
            speed_full_load: machine's shaft speed at full load in rad/s or rpm.

        Returns:
            The calculated speed regulation percentage.

        """

        if speed_full_load == 0:
            raise ValueError("Full-load speed cannot be zero.")
        elif speed_no_load == 0:
            raise ValueError("No-load speed cannot be zero.")

        return ((speed_no_load - speed_full_load) / speed_full_load) * 100
