class DCMachine:
    '''
    DCMachine (abstract base class)
    ├── SeparatelyExcited
    ├── ShuntMotor/Generator
    ├── SeriesMotor/Generator
    └── CompoundMotor/Generator
        ├── CumulativeCompound
        └── DifferentialCompound
    '''

    def __init__(self, armature_resistance: float,
                 field_resistance: float,
                 supply_voltage: float,
                 speed: float,
                 flux: float,
                 machine_constant: float) -> None:
        self.armature_resistance = armature_resistance
        self.field_resistnace = field_resistance
        self.supply_voltage = supply_voltage
        self.speed = speed
        self.flux = flux
        self.machine_constant = machine_constant

class SeparatelyExcited(DCMachine):
    def __init__() -> None:
        pass

    def field_current() -> float:
        pass

class ShuntMotorGenerator(DCMachine):
    def __init__() -> None:
        pass

    def field_current() -> float:
        pass

class SeriesMotorGenerator(DCMachine):
    def __init__() -> None:
        pass

    def field_current() -> float:
        pass

class CompoundMotorGenerator(DCMachine):
    def __init__() -> None:
        pass

    def field_current() -> float:
        pass

class CumulativeCompound(CompoundMotorGenerator):
    def __init__() -> None:
        pass

    def field_current() -> float:
        pass

class DifferentialCompound(CompoundMotorGenerator):
    def __init__() -> None:
        pass

    def field_current() -> float:
        pass
