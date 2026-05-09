from .base import DCMachine
from .magnetization import MagnetizationCurve


class ShuntMotorGenerator(DCMachine):
    """Shunt wound: field winding in parallel with armature.

    It is required to provide the shunt winding resistance.

    It is optional to provide the series winding resistance.
    """

    def __init__(
        self,
        armature_resistance: float,
        nominal_voltage: float,
        speed_rpm: float,
        operation_mode: str,
        flux: float | None = None,
        k_constant: float | None = None,
        magnetization_curve: MagnetizationCurve | None = None,
        shunt_resistance: float | None = None,
        series_resistance: float | None = None,
        compensating_resistance: float | None = None,
        brush_drop_voltage: float | None = None,
        mechanical_losses: float | None = None,
        core_losses: float | None = None,
        miscellaneous_losses: float | None = None,
        field_turns: float | None = None,
        armature_reaction_mmf: float | None = None,
    ) -> None:
        super().__init__(
            armature_resistance=armature_resistance,
            nominal_voltage=nominal_voltage,
            speed_rpm=speed_rpm,
            operation_mode=operation_mode,
            flux=flux,
            k_constant=k_constant,
            magnetization_curve=magnetization_curve,
            shunt_resistance=shunt_resistance,
            series_resistance=series_resistance,
            compensating_resistance=compensating_resistance,
            brush_drop_voltage=brush_drop_voltage,
            mechanical_losses=mechanical_losses,
            core_losses=core_losses,
            miscellaneous_losses=miscellaneous_losses,
            field_turns=field_turns,
            armature_reaction_mmf=armature_reaction_mmf,
        )

    def validate_resistance(self) -> None:
        if self.shunt_resistance is None:
            raise ValueError("Shunt machine requires shunt_resistance in ohms.")
        elif self.shunt_resistance <= 0:
            raise ValueError("Shunt resistance must be positive and non-zero.")

    def field_circuit_resistance(self, field_adjusting_resistance: float = 0.0) -> float:
        """Returns the total field-circuit resistance in ohms.

        An external adjustable resistor may be connected in series with the shunt
        field winding:

            R_field_total = Rf + R_adj

        Args:
            field_adjusting_resistance: external field-adjusting resistance in ohms.

        Returns:
            Total field-circuit resistance in ohms.

        Raises:
            ValueError: if ``field_adjusting_resistance`` is negative.
        """
        if field_adjusting_resistance < 0:
            raise ValueError("The field-adjusting resistance, in ohms, must be >= 0.")

        return self.shunt_resistance + field_adjusting_resistance

    def field_current(self, applied_field_voltage: float) -> float:
        """If = Vt / Rf"""
        raise NotImplementedError("field_current is not implemented yet for shunt machine.")

    def armature_current(self, terminal_voltage: float, induced_emf: float) -> float:
        """Ia = (Vt - E) / Ra"""
        raise NotImplementedError("armature_current is not implemented yet for shunt machine.")

    def terminal_voltage(self, armature_current: float) -> float:
        """For motor: Vt = V - Ia*Ra | For generator: Vt = E - Ia*Ra"""
        raise NotImplementedError("terminal_voltage is not implemented yet for shunt machine.")

    def induced_torque(self, armature_current: float) -> float:
        """T = K * phi * Ia"""
        raise NotImplementedError("induced_torque is not implemented yet for shunt machine.")

    def shaft_speed_rpm(self, terminal_voltage: float, armature_current: float) -> float:
        raise NotImplementedError("shaft_speed_rpm is not implemented yet for shunt machine.")
