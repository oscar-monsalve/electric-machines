from .base import DCMachine
from .magnetization import MagnetizationCurve


class ShuntMotorGenerator(DCMachine):
    """Shunt DC motor/generator with field winding connected across the terminals.

    In a shunt machine, the shunt-field branch is connected in parallel with
    the armature terminals. Therefore the field current is set by the terminal
    voltage and the total field-branch resistance:

        If = Vt / (Rf + R_adj)

    where:
        Rf: shunt-field winding resistance
        R_adj: optional external field-adjusting resistance in series with the
            shunt-field winding

    The armature current and line current are different because terminal current
    splits between the armature branch and the shunt-field branch:

        Motor:     IL = IA + If
        Generator: IA = IL + If

    This class keeps those currents explicit. Armature voltage equations use
    armature current ``IA``. Terminal power calculations should use line current
    ``IL``.
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

    @staticmethod
    def _validate_non_negative_armature_voltage(terminal_voltage: float) -> None:
        """Validates terminal voltage for the simplified shunt-machine model."""
        if terminal_voltage < 0:
            raise ValueError("Terminal voltage must be >= 0.")

    def validate_resistance(self) -> None:
        """Validates the shunt-field resistance required by a shunt machine.

        A shunt machine must provide ``shunt_resistance`` because field current
        is computed from the shunt-field branch relation:

            If = Vt / (Rf + R_adj)

        The stored machine winding resistance ``Rf`` must be strictly positive.
        The optional external adjusting resistance ``R_adj`` is supplied to
        individual operating-point helpers and validated there.
        """
        if self.shunt_resistance is None:
            raise ValueError("Shunt machine requires shunt_resistance in ohms.")
        elif self.shunt_resistance <= 0:
            raise ValueError("Shunt resistance must be positive and non-zero.")

    def field_circuit_resistance(self, field_adjusting_resistance: float = 0.0) -> float:
        """Returns the total shunt-field branch resistance in ohms.

        The shunt-field winding may have an external field-adjusting resistor
        connected in series with it:

            R_field_total = Rf + R_adj

        where:
            Rf: shunt-field winding resistance
            R_adj: external field-adjusting resistance

        Args:
            field_adjusting_resistance: external field-adjusting resistance in
                ohms. Defaults to ``0.0``.

        Returns:
            Total shunt-field branch resistance in ohms.

        Raises:
            ValueError: if ``field_adjusting_resistance`` is negative.
        """
        if field_adjusting_resistance < 0:
            raise ValueError("The field-adjusting resistance, in ohms, must be >= 0.")

        return self.shunt_resistance + field_adjusting_resistance

    def field_current(
        self,
        applied_field_voltage: float,
        field_adjusting_resistance: float = 0.0
    ) -> float:
        """Returns shunt-field current from terminal voltage.

        For a shunt machine, the field branch is connected across the machine
        terminals. Therefore the voltage applied to the field branch is the
        terminal voltage:

            If = Vt / (Rf + R_adj)

        where:
            Rf: shunt-field winding resistance
            R_adj: optional external field-adjusting resistance in series with
                the shunt-field winding

        The parameter name ``applied_field_voltage`` is inherited from the base
        class interface. In this subclass it should be interpreted as terminal
        voltage across the shunt-field branch.

        Args:
            applied_field_voltage: terminal voltage across the shunt-field
                branch, in volts.
            field_adjusting_resistance: external field-adjusting resistance in
                ohms. Defaults to ``0.0``.

        Returns:
            Shunt-field current in amps.

        Raises:
            ValueError: if ``applied_field_voltage`` is negative.
            ValueError: if ``field_adjusting_resistance`` is negative.
        """
        self._validate_non_negative_armature_voltage(applied_field_voltage)

        total_field_resistance = self.field_circuit_resistance(
            field_adjusting_resistance=field_adjusting_resistance
        )

        return applied_field_voltage / total_field_resistance

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
