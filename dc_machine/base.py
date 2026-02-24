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
    pass

class ShuntMotorGenerator(DCMachine):
    pass

class SeriesMotorGenerator(DCMachine):
    pass

class CompoundMotorGenerator(DCMachine):
    pass

class CumulativeCompound(CompoundMotorGenerator):
    pass

class DifferentialCompound(CompoundMotorGenerator):
    pass
