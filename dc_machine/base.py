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
        flux: float,
        machine_constant: float
    ) -> None:

        if armature_resistance <= 0:
            raise ValueError("Armature resistance must be positive")

        self.armature_resistance = armature_resistance
        self.field_resistance = field_resistance
        self.supply_voltage = supply_voltage
        self.speed = speed
        self.flux = flux
        self.machine_constant = machine_constant

    @abstractmethod
    def field_current(self) -> float:
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

        return ((speed_no_load - speed_full_load) / speed_full_load) * 100


class SeparatelyExcited(DCMachine):
    def field_current(self) -> float:
        pass

class ShuntMotorGenerator(DCMachine):
    def field_current(self) -> float:
        pass

class SeriesMotorGenerator(DCMachine):
    def field_current(self) -> float:
        pass

class CompoundMotorGenerator(DCMachine):
    def field_current(self) -> float:
        pass

class CumulativeCompound(CompoundMotorGenerator):
    def field_current(self) -> float:
        pass

class DifferentialCompound(CompoundMotorGenerator):
    def field_current(self) -> float:
        pass
