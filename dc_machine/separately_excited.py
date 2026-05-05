from .base import DCMachine
from .magnetization import MagnetizationCurve
from .utils import rpm_to_rad_s


class SeparatelyExcitedMotorGenerator(DCMachine):
    """Separately excited DC motor/generator with externally supplied field current.

    This machine requires ``shunt_resistance`` to model the field winding supplied
    by an external DC source. The armature circuit may also include optional brush
    drop and optional compensating resistance.

    An external adjustable resistor may also be connected in series with the shunt
    field winding during field-voltage-based calculations. This operating-point
    resistor is represented through ``field_adjusting_resistance`` in the relevant
    helper methods and is not stored as a permanent machine parameter.

    ``compensating_resistance`` models the resistance of a compensating or
    auxiliary winding placed in series with the armature path. It is distinct
    from ``series_resistance``, which is reserved for series-field topology
    modeling.

    This class also supports power-flow and efficiency calculations. Optional
    constant losses may be supplied through the base class as mechanical, core,
    and miscellaneous losses. For separately excited operation, field-supply
    power is handled explicitly through ``applied_field_voltage``.

    Two efficiency views are supported:
        - ``overall_efficiency(...)`` includes external field-supply power.
        - ``efficiency_excluding_field_power(...)`` excludes only the field-supply
          power, while still accounting for the other machine losses through the
          power-flow model.

    A first nonlinear OCC armature-reaction workflow is also intended for this
    class. That workflow requires:
        - ``magnetization_curve``
        - ``field_turns``
        - ``armature_reaction_mmf``

    EMF model used in this class:
        - Preferred: magnetization curve ``E = f(If)`` scaled by speed.
        - Fallback: ``E = K * flux * speed_rpm``.
        - Torque: ``T = (E * Ia) / omega``, with ``omega = rpm_to_rad_s(speed_rpm)``.

    Assumptions kept for now:
        - fixed armature-reaction MMF for the first nonlinear iteration
        - no load-dependent armature-reaction model yet
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

    def _validate_nonlinear_occ_requirements(self) -> None:
        """Validates the common requirements for nonlinear OCC armature-reaction analysis."""
        if not self.has_magnetization_curve():
            raise ValueError("Nonlinear armature-reaction analysis requires a magnetization curve.")
        self._validate_field_turns()
        self._validate_armature_reaction_mmf()

    def validate_resistance(self) -> None:
        """Validates the winding resistances required for a separately excited machine.

        A separately excited machine must provide ``shunt_resistance`` because the
        externally supplied field current is computed from the field-circuit
        relation ``If = Vf / Rf``. Therefore, the shunt-field resistance must be
        configured and strictly positive.
        """
        if self.shunt_resistance is None:
            raise ValueError("Separately excited machine requires shunt_resistance in ohms.")
        elif self.shunt_resistance <= 0:
            raise ValueError("Shunt resistance must be positive and non-zero.")

    def field_circuit_resistance(self, field_adjusting_resistance: float = 0.0) -> float:
        """Returns the total field-circuit resistance in ohms.

        For the separately excited field circuit, an external adjustable resistor
        may be connected in series with the shunt field winding:

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

    def field_current(self, applied_field_voltage: float, field_adjusting_resistance: float = 0.0) -> float:
        """Calculates field current for the separately excited field circuit.

        Uses:

            If = Vf / (Rf + R_adj)

        where:
            Rf: shunt-field resistance
            R_adj: optional external field-adjusting resistance connected in series

        Args:
            applied_field_voltage: external DC voltage supplying the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.

        Returns:
            Field current in amps.
        """
        total_field_resistance = self.field_circuit_resistance(field_adjusting_resistance)
        return applied_field_voltage / total_field_resistance

    def induced_emf_from_field_voltage(
        self,
        applied_field_voltage: float,
        field_adjusting_resistance: float = 0.0,
        desired_speed_rpm: float | None = None
    ) -> float:
        """Returns induced emf using the preferred excitation model.

        Preferred order:
            1. magnetization curve, if available.
            2. analytic model ``E = K * flux * speed_rpm`` (fallback).

        For the field circuit, the excitation current is computed using the total
        field resistance ``Rf + R_adj`` when an external adjusting resistor is present.

        If ``desired_speed_rpm`` is omitted, the machine's configured ``speed_rpm``
        is used.

        Args:
            applied_field_voltage: external DC voltage applied to the field winding, in volts.
            field_adjusting_resistance: external field-adjusting resistance in ohms.
            desired_speed_rpm: shaft speed at which the induced emf is desired, in rpm.

        Returns:
            The induced emf in volts.

        Raises:
            ValueError: if no emf model is available.
        """
        effective_speed_rpm = self.speed_rpm if desired_speed_rpm is None else desired_speed_rpm

        field_current = self.field_current(
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance
        )

        if self.has_magnetization_curve():
            return self.magnetization_curve.emf_from_field_current(
                field_current=field_current,
                desired_speed_rpm=effective_speed_rpm
            )
        if self.has_analytic_model():
            return self.k_constant * self.flux * effective_speed_rpm

        raise ValueError("Cannot compute induced emf: provide either magnetization_curve or both flux and k_constant.")

    def field_voltage_from_emf(
        self,
        emf: float,
        field_adjusting_resistance: float = 0.0,
        desired_speed_rpm: float | None = None,
    ) -> float:
        """Returns the external field-supply voltage required to produce the desired induced emf.

        This method requires a magnetization curve. The required field current is first
        obtained by inverse OCC interpolation, and then the corresponding field-supply
        voltage is computed using the total field-circuit resistance:

            Vf = If * (Rf + R_adj)

        If ``desired_speed_rpm`` is omitted, the machine's configured ``speed_rpm``
        is used.

        Args:
            emf: desired induced emf in volts.
            field_adjusting_resistance: external field-adjusting resistance in ohms.
            desired_speed_rpm: shaft speed at which the induced emf is desired, in rpm.

        Returns:
            Required external field-supply voltage in volts.

        Raises:
            ValueError: if no magnetization curve is available.
        """
        if not self.has_magnetization_curve():
            raise ValueError("field_voltage_from_emf requires a magnetization curve.")

        effective_speed_rpm = self.speed_rpm if desired_speed_rpm is None else desired_speed_rpm

        field_current = self.magnetization_curve.field_current_from_emf(
            emf=emf,
            desired_speed_rpm=effective_speed_rpm
        )

        return field_current * self.field_circuit_resistance(field_adjusting_resistance)

    def armature_current(self, terminal_voltage: float, induced_emf: float) -> float:
        """Calculates the armature current with optional brush voltage drop (Vb).

          Motor:     Ia = (Vt - E - Vb) / Ra
          Generator: Ia = (E - Vt - Vb) / Ra

        Args:
            terminal_voltage: output voltage (generator) or input voltage (motor) at terminals in volts.
            induced_emf: emf (generator) or back-emf (motor) in volts.

        Returns:
            The armature current in amps depending the machine operating mode (motor or generator).

        Note:
            The textbook form uses ``Ra``. In implementation, the armature-path
            resistance is ``Ra + Ri`` when a compensating resistance is configured.
        """
        armature_path_resistance = self._armature_path_resistance()
        brush_drop_voltage = self._brush_drop_value()
        return (self._current_sign() * (terminal_voltage - induced_emf) - brush_drop_voltage) / armature_path_resistance

    def induced_emf_from_terminal_conditions(
        self,
        terminal_voltage: float,
        armature_current: float,
    ) -> float:
        """Returns the operating-point induced emf from terminal conditions.

        Electrical equation:
            Motor:     E = Vt - Ia*Ra - Vb
            Generator: E = Vt + Ia*Ra + Vb

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.

        Returns:
            Induced emf in volts.

        Raises:
            ValueError: if ``armature_current`` is negative.

        Note:
            The textbook form uses ``Ra``. In implementation, the armature-path
            resistance is ``Ra + Ri`` when a compensating resistance is configured.
        """
        self._validate_non_negative_armature_current(armature_current)

        armature_path_resistance = self._armature_path_resistance()
        brush_drop_voltage = self._brush_drop_value()

        if self.operation_mode == "motor":
            return terminal_voltage - (armature_current * armature_path_resistance) - brush_drop_voltage

        return terminal_voltage + (armature_current * armature_path_resistance) + brush_drop_voltage

    def terminal_voltage(self, armature_current: float) -> float:
        """Returns terminal voltage using the analytic EMF model only.

        Electrical equation:
            Motor:     Vt = Vnom - Ia*Ra - Vb
            Generator: Vt = E - Ia*Ra - Vb

        For generator operation, E is obtained from the analytic model:
            E = K * flux * speed_rpm

        This method is intentionally analytic-only. When the operating point is
        defined by a magnetization curve / OCC, use:
            - terminal_voltage_from_emf(...)
            - terminal_voltage_from_field_voltage(...)

        Args:
            armature_current: armature current in amps.

        Returns:
            Terminal voltage in volts.

        Raises:
            ValueError: if ``armature_current`` is negative.

        Note:
            The textbook form uses ``Ra``. In implementation, the armature-path
            resistance is ``Ra + Ri`` when a compensating resistance is configured.
        """
        self._validate_non_negative_armature_current(armature_current)

        armature_path_resistance = self._armature_path_resistance()
        brush_drop_voltage = self._brush_drop_value()

        if self.operation_mode == "motor":
            return self.nominal_voltage - (armature_current * armature_path_resistance) - brush_drop_voltage
        else:  # generator
            return self.induced_emf() - (armature_current * armature_path_resistance) - brush_drop_voltage

    def terminal_voltage_from_emf(self, armature_current: float, induced_emf: float) -> float:
        """Returns terminal voltage from a known operating-point EMF.

        Electrical equation:
            Motor:     Vt = E + Ia*Ra + Vb
            Generator: Vt = E - Ia*Ra - Vb

        Args:
            armature_current: armature current in amps.
            induced_emf: induced emf corresponding to the operating point, in volts.

        Returns:
            Terminal voltage in volts.

        Raises:
            ValueError: if ``armature_current`` is negative.

        Note:
            The textbook form uses ``Ra``. In implementation, the armature-path
            resistance is ``Ra + Ri`` when a compensating resistance is configured.
        """
        self._validate_non_negative_armature_current(armature_current)

        armature_path_resistance = self._armature_path_resistance()
        brush_drop_voltage = self._brush_drop_value()

        if self.operation_mode == "motor":
            return induced_emf + (armature_current * armature_path_resistance) + brush_drop_voltage
        else:  # generator
            return induced_emf - (armature_current * armature_path_resistance) - brush_drop_voltage

    def terminal_voltage_from_field_voltage(
        self,
        armature_current: float,
        applied_field_voltage: float,
        field_adjusting_resistance: float = 0.0,
        desired_speed_rpm: float | None = None,
    ) -> float:
        """Returns terminal voltage using the preferred excitation model.

        Preferred order:
            1. magnetization curve, if available.
            2. analytic model ``E = K * flux * speed_rpm`` (fallback).

        When an external field-adjusting resistor is present, the excitation current is
        computed from the total field-circuit resistance ``Rf + R_adj``.

        If ``desired_speed_rpm`` is omitted, the machine's configured ``speed_rpm``
        is used.

        Args:
            armature_current: armature current in amps.
            applied_field_voltage: external DC voltage applied to the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.
            desired_speed_rpm: shaft speed at which the induced emf is desired, in rpm.

        Returns:
            Terminal voltage in volts.

        Raises:
            ValueError: if ``armature_current`` is negative.
        """
        induced_emf = self.induced_emf_from_field_voltage(
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance,
            desired_speed_rpm=desired_speed_rpm
        )
        return self.terminal_voltage_from_emf(
            armature_current=armature_current,
            induced_emf=induced_emf
        )

    def induced_torque(self, armature_current: float) -> float:
        """Returns induced torque using the analytic EMF model only.

        Uses:
            T = (E * Ia) / omega

        where E is obtained from the analytic fallback model:
            E = K * flux * speed_rpm

        This method is intentionally analytic-only. When the operating point is
        defined by a magnetization curve / OCC, use:
            - induced_torque_from_emf(...)
            - induced_torque_from_field_voltage(...)

        Args:
            armature_current: armature current in amps.

        Returns:
            The induced torque in N·m.

        Raises:
            ValueError: if ``armature_current`` is negative.
        """
        self._validate_non_negative_armature_current(armature_current)

        omega = rpm_to_rad_s(self.speed_rpm)
        if omega == 0:
            raise ValueError("speed_rpm cannot be zero when computing torque.")

        return (self.induced_emf() * armature_current) / omega

    def shaft_speed_rpm(self, terminal_voltage: float, armature_current: float) -> float:
        """Solves shaft speed using the analytic EMF model only.

        Electrical equation:
            Motor:     E = Vt - Ia*Ra - Vb
            Generator: E = Vt + Ia*Ra + Vb

        Analytic speed model:
            E = K * flux * n_rpm

        This method is intentionally analytic-only. When excitation is defined by
        a magnetization curve / OCC, use:
            - shaft_speed_rpm_from_field_voltage(...)
            - shaft_speed_rpm_from_field_current(...)

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.

        Returns:
            Shaft speed in rpm.

        Raises:
            ValueError: if ``armature_current`` is negative.

        Note:
            The textbook form uses ``Ra``. In implementation, the armature-path
            resistance is ``Ra + Ri`` when a compensating resistance is configured.
        """
        self._validate_analytic_model()

        k_phi = self.k_constant * self.flux

        emf = self.induced_emf_from_terminal_conditions(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
        )

        return emf / k_phi

    def induced_torque_from_emf(self, armature_current: float, induced_emf: float) -> float:
        """Returns induced torque from a known operating-point EMF.

        Uses:
            T = (E * Ia) / omega

        Args:
            armature_current: armature current in amps.
            induced_emf: induced emf corresponding to the operating point, in volts.

        Returns:
            The induced torque in N·m.

        Raises:
            ValueError: if ``armature_current`` is negative.
        """
        self._validate_non_negative_armature_current(armature_current)

        omega = rpm_to_rad_s(self.speed_rpm)

        if omega == 0:
            raise ValueError("speed_rpm cannot be zero when computing torque.")

        return (induced_emf * armature_current) / omega

    def induced_torque_from_field_voltage(
        self,
        armature_current: float,
        applied_field_voltage: float,
        field_adjusting_resistance: float = 0.0,
        desired_speed_rpm: float | None = None,
    ) -> float:
        """Returns induced torque using the preferred excitation model.

        Preferred order:
            1. magnetization curve, if available.
            2. analytic model ``E = K * flux * speed_rpm`` (fallback).

        When an external field-adjusting resistor is present, the excitation current is
        computed from the total field-circuit resistance ``Rf + R_adj``.

        If ``desired_speed_rpm`` is omitted, the machine's configured ``speed_rpm``
        is used.

        Args:
            armature_current: armature current in amps.
            applied_field_voltage: external DC voltage applied to the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.
            desired_speed_rpm: shaft speed at which the induced emf is desired, in rpm.

        Returns:
            The induced torque in N·m.

        Raises:
            ValueError: if ``armature_current`` is negative.
        """
        self._validate_non_negative_armature_current(armature_current)

        induced_emf = self.induced_emf_from_field_voltage(
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance,
            desired_speed_rpm=desired_speed_rpm
        )

        effective_speed_rpm = self.speed_rpm if desired_speed_rpm is None else desired_speed_rpm
        omega = rpm_to_rad_s(effective_speed_rpm)

        if omega == 0:
            raise ValueError("speed_rpm cannot be zero when computing torque.")

        return (induced_emf * armature_current) / omega

    def shaft_speed_rpm_from_field_current(
        self,
        terminal_voltage: float,
        armature_current: float,
        field_current: float
    ) -> float:
        """Solves shaft speed from terminal conditions and field current.
        Electrical equation:
            Motor:     E = Vt - Ia*Ra - Vb
            Generator: E = Vt + Ia*Ra + Vb

        For a fixed field current, the magnetization curve gives the induced emf at
        the reference speed. Since E is proportional to speed for the same field
        current, the shaft speed is:

            n = E_required * n_ref / E_ref

        where:
            E_required: emf required by the terminal operating point.
            E_ref: emf from the OCC at the same field current and reference speed.
            n_ref: reference speed of the OCC data.

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.
            field_current: field current in amps.

        Returns:
            Shaft speed in rpm.

        Raises:
            ValueError: if no magnetization curve is available.
            ValueError: if the OCC gives zero reference emf for the given field current.
            ValueError: if ``armature_current`` is negative.

        Note:
            The textbook form uses ``Ra``. In implementation, the armature-path
            resistance is ``Ra + Ri`` when a compensating resistance is configured.
        """
        if not self.has_magnetization_curve():
            raise ValueError("shaft_speed_rpm_from_field_current requires a magnetization curve.")

        required_emf = self.induced_emf_from_terminal_conditions(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
        )

        reference_speed_rpm = self.magnetization_curve.reference_speed_rpm
        emf_at_reference_speed = self.magnetization_curve.emf_from_field_current(
            field_current=field_current,
            desired_speed_rpm=reference_speed_rpm
        )

        if emf_at_reference_speed == 0:
            raise ValueError(
                "Cannot solve speed: OCC gives zero emf at the reference speed for the given field current."
            )

        return required_emf * (reference_speed_rpm / emf_at_reference_speed)

    def shaft_speed_rpm_from_field_voltage(
        self,
        terminal_voltage: float,
        armature_current: float,
        applied_field_voltage: float,
        field_adjusting_resistance: float = 0.0
    ) -> float:
        """Solves shaft speed from terminal conditions and applied field voltage.

        This helper is intended for separately excited OCC operation, where the field
        voltage determines field current through:

            If = Vf / (Rf + R_adj)

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.
            applied_field_voltage: external DC voltage applied to the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.

        Returns:
            Shaft speed in rpm.

        Raises:
            ValueError: if ``armature_current`` is negative.
        """
        field_current = self.field_current(
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance
        )
        return self.shaft_speed_rpm_from_field_current(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
            field_current=field_current,
        )

    # Nonlinear analysis methods considering a fixed armature reaction

    def field_mmf(self, applied_field_voltage: float, field_adjusting_resistance: float = 0.0) -> float:
        """Returns shunt-field MMF in ampere-turns.

        Uses:

            F_field = N_F * If

        where the field current is computed from:

            If = Vf / (Rf + R_adj)

        Args:
            applied_field_voltage: external DC voltage applied to the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.

        Returns:
            Field MMF in ampere-turns.

        Raises:
            ValueError: if ``field_turns`` is not configured.
        """
        self._validate_field_turns()

        field_current = self.field_current(
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance
        )

        return self.field_turns * field_current

    def equivalent_field_current_with_armature_reaction(
        self,
        applied_field_voltage: float,
        field_adjusting_resistance: float = 0.0,
    ) -> float:
        """Returns equivalent field current after fixed demagnetizing armature reaction.

        Uses:

            F_net = F_field - F_ar
            If* = F_net / N_F

            where If* is the equivalent field current.

        Args:
            applied_field_voltage: external DC voltage applied to the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.

        Returns:
            Equivalent field current in amps.

        Raises:
            ValueError: if ``field_turns`` or ``armature_reaction_mmf`` is not configured.
            ValueError: if the resulting equivalent field current is negative.
        """
        self._validate_field_turns()
        self._validate_armature_reaction_mmf()

        net_mmf = self.field_mmf(
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance
        ) - self.armature_reaction_mmf_value()

        if net_mmf < 0:
            raise ValueError("Equivalent field current would be negative under the specified armature reaction.")

        return net_mmf / self.field_turns

    def induced_emf_from_equivalent_field_current(
        self,
        equivalent_field_current: float,
        desired_speed_rpm: float | None = None,
    ) -> float:
        """Returns induced emf from equivalent field current using the OCC.

        If ``desired_speed_rpm`` is omitted, the machine's configured ``speed_rpm``
        is used.

        Args:
            equivalent_field_current: equivalent field current in amps.
            desired_speed_rpm: shaft speed at which the induced emf is desired, in rpm.

        Returns:
            Induced emf in volts.

        Raises:
            ValueError: if no magnetization curve is available.
        """
        if not self.has_magnetization_curve():
            raise ValueError("Nonlinear armature-reaction analysis requires a magnetization curve.")

        effective_speed_rpm = self.speed_rpm if desired_speed_rpm is None else desired_speed_rpm

        return self.magnetization_curve.emf_from_field_current(
            field_current=equivalent_field_current,
            desired_speed_rpm=effective_speed_rpm,
        )

    def induced_emf_with_armature_reaction(
        self,
        applied_field_voltage: float,
        field_adjusting_resistance: float = 0.0,
        desired_speed_rpm: float | None = None,
    ) -> float:
        """Returns induced emf including fixed demagnetizing armature reaction.

        If ``desired_speed_rpm`` is omitted, the machine's configured ``speed_rpm``
        is used.

        Args:
            applied_field_voltage: external DC voltage applied to the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.
            desired_speed_rpm: shaft speed at which the induced emf is desired, in rpm.

        Returns:
            Induced emf in volts.

        Raises:
            ValueError: if nonlinear OCC requirements are not configured.
        """
        self._validate_nonlinear_occ_requirements()

        equivalent_field_current = self.equivalent_field_current_with_armature_reaction(
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance
        )

        return self.induced_emf_from_equivalent_field_current(
            equivalent_field_current=equivalent_field_current,
            desired_speed_rpm=desired_speed_rpm,
        )

    def terminal_voltage_from_field_voltage_with_armature_reaction(
        self,
        armature_current: float,
        applied_field_voltage: float,
        field_adjusting_resistance: float = 0.0,
        desired_speed_rpm: float | None = None,
    ) -> float:
        """Returns terminal voltage including fixed demagnetizing armature reaction.

        If ``desired_speed_rpm`` is omitted, the machine's configured ``speed_rpm``
        is used.

        Args:
            armature_current: armature current in amps.
            applied_field_voltage: external DC voltage applied to the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.
            desired_speed_rpm: shaft speed at which the induced emf is desired, in rpm.

        Returns:
            Terminal voltage in volts.

        Raises:
            ValueError: if nonlinear OCC requirements are not configured.
            ValueError: if ``armature_current`` is negative.
        """
        induced_emf = self.induced_emf_with_armature_reaction(
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance,
            desired_speed_rpm=desired_speed_rpm,
        )
        return self.terminal_voltage_from_emf(
            armature_current=armature_current,
            induced_emf=induced_emf,
        )

    def equivalent_field_current_from_emf(
        self,
        emf: float,
        desired_speed_rpm: float | None = None,
    ) -> float:
        """Returns the equivalent field current required to produce a desired induced emf.

        This is the inverse OCC helper. If ``desired_speed_rpm`` is omitted, the
        machine's configured ``speed_rpm`` is used.

        Args:
            emf: desired induced emf in volts.
            desired_speed_rpm: shaft speed at which the induced emf is desired, in rpm.

        Returns:
            Equivalent field current in amps.

        Raises:
            ValueError: if no magnetization curve is available.
        """
        if not self.has_magnetization_curve():
            raise ValueError("Nonlinear armature-reaction analysis requires a magnetization curve.")

        effective_speed_rpm = self.speed_rpm if desired_speed_rpm is None else desired_speed_rpm

        return self.magnetization_curve.field_current_from_emf(
            emf=emf,
            desired_speed_rpm=effective_speed_rpm,
        )

    def field_current_required_for_emf_with_armature_reaction(
        self,
        emf: float,
        desired_speed_rpm: float | None = None,
    ) -> float:
        """Returns the actual field current required to produce a desired emf with armature reaction.

        Uses:

            If = If* + F_ar / N_F

            where If* is the equivalent field current (armature reaction) and If the actual field current.

        Args:
            emf: desired induced emf in volts.
            desired_speed_rpm: shaft speed at which the induced emf is desired, in rpm.

        Returns:
            Required actual field current in amps.

        Raises:
            ValueError: if nonlinear OCC requirements are not configured.
        """
        self._validate_nonlinear_occ_requirements()

        equivalent_field_current = self.equivalent_field_current_from_emf(
            emf=emf,
            desired_speed_rpm=desired_speed_rpm,
        )

        return equivalent_field_current + (self.armature_reaction_mmf_value() / self.field_turns)

    def field_adjusting_resistance_required_for_field_current(
        self,
        applied_field_voltage: float,
        field_current: float,
    ) -> float:
        """Returns the external field-adjusting resistance required to obtain a target field current.

        Uses:

            R_adj = (Vf / If) - Rf

        Args:
            applied_field_voltage: external DC voltage applied to the field winding.
            field_current: desired field current in amps.

        Returns:
            Required external field-adjusting resistance in ohms.

        Raises:
            ValueError: if ``field_current`` is not positive.
            ValueError: if the computed resistance is negative.
        """
        if field_current <= 0:
            raise ValueError("Required field current must be positive and non-zero.")

        required_resistance = (applied_field_voltage / field_current) - self.shunt_resistance

        if required_resistance < 0:
            raise ValueError("Required field-adjusting resistance would be negative for the specified field current.")

        return required_resistance

    def field_adjusting_resistance_required_for_emf_with_armature_reaction(
        self,
        emf: float,
        applied_field_voltage: float,
        desired_speed_rpm: float | None = None,
    ) -> float:
        """Returns the external field-adjusting resistance required to produce a desired emf with armature reaction.

        If ``desired_speed_rpm`` is omitted, the machine's configured ``speed_rpm``
        is used.

        Args:
            emf: desired induced emf in volts.
            applied_field_voltage: external DC voltage applied to the field winding.
            desired_speed_rpm: shaft speed at which the induced emf is desired, in rpm.

        Returns:
            Required external field-adjusting resistance in ohms.

        Raises:
            ValueError: if nonlinear OCC requirements are not configured.
        """
        required_field_current = self.field_current_required_for_emf_with_armature_reaction(
            emf=emf,
            desired_speed_rpm=desired_speed_rpm,
        )

        return self.field_adjusting_resistance_required_for_field_current(
            applied_field_voltage=applied_field_voltage,
            field_current=required_field_current
        )

    def field_voltage_required_for_emf_with_armature_reaction(
        self,
        emf: float,
        field_adjusting_resistance: float = 0.0,
        desired_speed_rpm: float | None = None,
    ) -> float:
        """Returns the field-supply voltage required to produce a desired emf with armature reaction.

        If ``desired_speed_rpm`` is omitted, the machine's configured ``speed_rpm``
        is used.

        Args:
            emf: desired induced emf in volts.
            field_adjusting_resistance: external field-adjusting resistance in ohms.
            desired_speed_rpm: shaft speed at which the induced emf is desired, in rpm.

        Returns:
            Field voltage required in volts.
        """
        required_field_current = self.field_current_required_for_emf_with_armature_reaction(
            emf=emf,
            desired_speed_rpm=desired_speed_rpm,
        )
        return required_field_current * self.field_circuit_resistance(field_adjusting_resistance)

    # Power/losses

    def field_input_power(
        self,
        applied_field_voltage: float,
        field_adjusting_resistance: float = 0.0
    ) -> float:
        """Returns external field-supply electrical input power in watts.

        Uses:

            P_field = Vf * If

        where the field current is computed from the total field-circuit resistance:

            If = Vf / (Rf + R_adj)

        Args:
            applied_field_voltage: external DC voltage supplying the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.

        Returns:
            External field-supply input power in watts.
        """
        field_current = self.field_current(
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance,
        )
        return applied_field_voltage * field_current

    def field_copper_losses(
        self,
        applied_field_voltage: float,
        field_adjusting_resistance: float = 0.0
    ) -> float:
        """Returns copper losses in the machine shunt-field winding, in watts.

        The field current is computed from the total field-circuit resistance:

            If = Vf / (Rf + R_adj)

        The winding copper loss returned by this method is:

            P_cu,field = If^2 * Rf

        Args:
            applied_field_voltage: external DC voltage supplying the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.

        Returns:
            Copper loss in the machine shunt-field winding, in watts.

        Note:
            Losses in the external adjusting resistor are not included here.
        """
        field_current = self.field_current(
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance
        )
        return (field_current ** 2) * self.shunt_resistance

    def field_adjusting_resistor_losses(
        self,
        applied_field_voltage: float,
        field_adjusting_resistance: float
    ) -> float:
        """Returns power dissipated in the external field-adjusting resistor.

        Uses:
            P_Radj = If^2 * R_adj

        where the field current is computed from the total field-circuit resistance
        ``Rf + R_adj``.

        Args:
            applied_field_voltage: external DC voltage applied to the field circuit.
            field_adjusting_resistance: external field-adjusting resistance in ohms.

        Returns:
            Power dissipated in the external field-adjusting resistor, in watts.
        """
        if field_adjusting_resistance == 0:
            return 0.0

        field_current = self.field_current(
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance
        )

        return (field_current ** 2) * field_adjusting_resistance

    def copper_losses(
        self,
        armature_current: float,
        applied_field_voltage: float | None = None,
        field_adjusting_resistance: float = 0.0,
        include_field_adjusting_resistor_losses: bool = False
    ) -> float:
        """Returns total copper losses in watts.

        Includes armature-path copper losses and, when ``applied_field_voltage`` is
        provided, copper losses in the machine shunt-field winding.

        If ``include_field_adjusting_resistor_losses`` is ``True``, the losses in the
        external field-adjusting resistor are also included.

        Args:
            armature_current: armature current in amps.
            applied_field_voltage: external DC voltage applied to the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.
            include_field_adjusting_resistor_losses: whether to include losses in the external field-adjusting resistor.

        Returns:
            Total copper losses in watts.

        Raises:
            ValueError: if ``armature_current`` is negative.
        """
        self._validate_non_negative_armature_current(armature_current)

        losses = self.armature_copper_losses(armature_current)

        if applied_field_voltage is not None:
            losses += self.field_copper_losses(
                applied_field_voltage=applied_field_voltage,
                field_adjusting_resistance=field_adjusting_resistance
            )

            if include_field_adjusting_resistor_losses:
                losses += self.field_adjusting_resistor_losses(
                    applied_field_voltage=applied_field_voltage,
                    field_adjusting_resistance=field_adjusting_resistance
                )

        return losses

    def armature_terminal_power(self, terminal_voltage: float, armature_current: float) -> float:
        """Returns armature-side terminal electrical power in watts.

        Uses:

            P_t = Vt * Ia

        Raises:
            ValueError: if ``armature_current`` is negative.
        """
        self._validate_non_negative_armature_current(armature_current)
        return terminal_voltage * armature_current

    def input_power(
        self,
        terminal_voltage: float,
        armature_current: float,
        induced_emf: float,
        applied_field_voltage: float | None = None,
        field_adjusting_resistance: float = 0.0,
        include_field_power: bool = True
    ) -> float:
        """Returns machine input power in watts for the current operating mode.

        For a motor:
            P_in = Vt * Ia

        For a generator:
            P_in = P_conv + P_rot

        If ``include_field_power`` is ``True`` and ``applied_field_voltage`` is
        provided, the external field-supply power is also included.

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.
            induced_emf: operating-point induced emf in volts.
            applied_field_voltage: external DC voltage applied to the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.
            include_field_power: whether to include external field-supply power.

        Returns:
            Input power in watts.

        Raises:
            ValueError: if ``armature_current`` is negative.
        """
        self._validate_non_negative_armature_current(armature_current)

        electromagnetic_power = self.electromagnetic_power(
            armature_current=armature_current,
            induced_emf=induced_emf,
        )
        terminal_power = self.armature_terminal_power(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
        )
        rotational_power = self.rotational_losses()

        if self.operation_mode == "motor":
            input_power = terminal_power
        else:  # generator
            input_power = electromagnetic_power + rotational_power

        if include_field_power and applied_field_voltage is not None:
            input_power += self.field_input_power(
                applied_field_voltage=applied_field_voltage,
                field_adjusting_resistance=field_adjusting_resistance,
            )

        return input_power

    def output_power(
        self,
        terminal_voltage: float,
        armature_current: float,
        induced_emf: float,
        applied_field_voltage: float | None = None,
        field_adjusting_resistance: float = 0.0,
        include_field_power: bool = True,
    ) -> float:
        """Returns machine output power in watts for the current operating mode.

        For a motor:
            P_out = P_conv - P_rot

        For a generator:
            P_out = Vt * Ia

        If ``include_field_power`` is ``True``, generator output remains the terminal
        electrical output, while field-supply power is accounted for on the input side.
        Therefore, this flag only affects the interpretation of the paired
        ``input_power(...)`` method, not the returned generator terminal output.

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.
            induced_emf: operating-point induced emf in volts.
            applied_field_voltage: external DC voltage applied to the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.
            include_field_power: retained for API symmetry with ``input_power(...)``.

        Returns:
            Output power in watts.

        Raises:
            ValueError: if ``armature_current`` is negative.
        """
        self._validate_non_negative_armature_current(armature_current)

        electromagnetic_power = self.electromagnetic_power(
            armature_current=armature_current,
            induced_emf=induced_emf,
        )
        terminal_power = self.armature_terminal_power(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
        )
        rotational_power = self.rotational_losses()

        if self.operation_mode == "motor":
            return electromagnetic_power - rotational_power

        return terminal_power

    # Efficiencies

    def efficiency_excluding_field_power(
        self,
        terminal_voltage: float,
        armature_current: float,
        induced_emf: float
    ) -> float:
        """Returns machine efficiency in percent excluding field-supply power.

        This efficiency includes the losses associated with armature conversion and
        machine rotation, but it excludes the external field-supply power of the
        separately excited field circuit.

        Note:
            Armature-path copper losses and brush losses are already included
            implicitly through ``P_conv = E * Ia``. For a motor, the difference
            between ``Vt * Ia`` and ``E * Ia`` represents those electrical losses.
            For a generator, the difference between ``E * Ia`` and ``Vt * Ia``
            represents those electrical losses.

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.
            induced_emf: operating-point induced emf in volts.

        Returns:
            Efficiency excluding field-supply power, in percent.

        Raises:
            ValueError: if ``armature_current`` is negative.
            ValueError: if the input-side power is zero or negative.
        """
        self._validate_non_negative_armature_current(armature_current)

        input_power = self.input_power(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
            induced_emf=induced_emf,
            include_field_power=False,
        )
        output_power = self.output_power(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
            induced_emf=induced_emf,
            include_field_power=False,
        )

        if input_power <= 0:
            raise ValueError(
                "Cannot compute efficiency excluding field power: input power must be positive and non-zero."
            )

        return (output_power / input_power) * 100.0

    def overall_efficiency(
        self,
        terminal_voltage: float,
        armature_current: float,
        induced_emf: float,
        applied_field_voltage: float,
        field_adjusting_resistance: float = 0.0
    ) -> float:
        """Returns overall machine efficiency in percent, including field-supply power.

        This efficiency includes the external field-supply power of the separately
        excited field circuit.

        Note:
            Armature-path copper losses and brush losses are already included
            implicitly through ``P_conv = E * Ia``. For a motor, the difference
            between ``Vt * Ia`` and ``E * Ia`` represents those electrical losses.
            For a generator, the difference between ``E * Ia`` and ``Vt * Ia``
            represents those electrical losses.

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.
            induced_emf: operating-point induced emf in volts.
            applied_field_voltage: external DC voltage applied to the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.

        Returns:
            Overall efficiency in percent.

        Raises:
            ValueError: if ``armature_current`` is negative.
            ValueError: if the input-side power is zero or negative.
        """
        self._validate_non_negative_armature_current(armature_current)

        input_power = self.input_power(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
            induced_emf=induced_emf,
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance,
            include_field_power=True,
        )
        output_power = self.output_power(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
            induced_emf=induced_emf,
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance,
            include_field_power=True,
        )

        if input_power <= 0:
            raise ValueError(
                "Cannot compute overall efficiency: input power must be positive and non-zero."
            )

        return (output_power / input_power) * 100.0

    def efficiency_excluding_field_power_from_field_voltage(
        self,
        terminal_voltage: float,
        armature_current: float,
        applied_field_voltage: float,
        field_adjusting_resistance: float = 0.0,
        desired_speed_rpm: float | None = None,
    ) -> float:
        """Returns efficiency excluding field-supply power using the preferred excitation model.

        This is a convenience wrapper around ``efficiency_excluding_field_power(...)``.
        It first computes the operating-point induced emf from the applied field voltage,
        including any external field-adjusting resistance, and then evaluates the
        efficiency.

        Preferred order:
            1. magnetization curve, if available.
            2. analytic model ``E = K * flux * speed_rpm`` (fallback).

        If ``desired_speed_rpm`` is omitted, the machine's configured ``speed_rpm``
        is used.

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.
            applied_field_voltage: external DC voltage applied to the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.
            desired_speed_rpm: shaft speed at which the induced emf is desired, in rpm.

        Returns:
            Efficiency excluding field-supply power, in percent.

        Raises:
            ValueError: if ``armature_current`` is negative.
        """
        induced_emf = self.induced_emf_from_field_voltage(
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance,
            desired_speed_rpm=desired_speed_rpm
        )

        return self.efficiency_excluding_field_power(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
            induced_emf=induced_emf,
        )

    def overall_efficiency_from_field_voltage(
        self,
        terminal_voltage: float,
        armature_current: float,
        applied_field_voltage: float,
        field_adjusting_resistance: float = 0.0,
        desired_speed_rpm: float | None = None,
    ) -> float:
        """Returns overall efficiency using the preferred excitation model.

        This is a convenience wrapper around ``overall_efficiency(...)``. It first
        computes the operating-point induced emf from the applied field voltage,
        including any external field-adjusting resistance, and then evaluates the
        overall efficiency.

        Preferred order:
            1. magnetization curve, if available.
            2. analytic model ``E = K * flux * speed_rpm`` (fallback).

        This method includes external field-supply power in the efficiency
        calculation.

        If ``desired_speed_rpm`` is omitted, the machine's configured ``speed_rpm``
        is used.

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.
            applied_field_voltage: external DC voltage applied to the field winding.
            field_adjusting_resistance: external field-adjusting resistance in ohms.
            desired_speed_rpm: shaft speed at which the induced emf is desired, in rpm.

        Returns:
            Overall efficiency in percent.

        Raises:
            ValueError: if ``armature_current`` is negative.
        """
        induced_emf = self.induced_emf_from_field_voltage(
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance,
            desired_speed_rpm=desired_speed_rpm
        )

        return self.overall_efficiency(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
            induced_emf=induced_emf,
            applied_field_voltage=applied_field_voltage,
            field_adjusting_resistance=field_adjusting_resistance
        )
