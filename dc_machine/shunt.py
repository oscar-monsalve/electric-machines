from .base import DCMachine
from .magnetization import MagnetizationCurve
from .utils import rpm_to_rad_s


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
    def _validate_non_negative_terminal_voltage(terminal_voltage: float) -> None:
        """Validates terminal voltage for the simplified shunt-machine model."""
        if terminal_voltage < 0:
            raise ValueError("Terminal voltage must be >= 0.")

    @staticmethod
    def _validate_non_negative_line_current(line_current: float) -> None:
        """Validates line current for the simplified shunt-machine model."""
        if line_current < 0:
            raise ValueError("Line current must be >= 0.")

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
        self._validate_non_negative_terminal_voltage(applied_field_voltage)

        total_field_resistance = self.field_circuit_resistance(
            field_adjusting_resistance=field_adjusting_resistance
        )

        return applied_field_voltage / total_field_resistance

    def line_current_from_armature_current(
        self,
        terminal_voltage: float,
        armature_current: float,
        field_adjusting_resistance: float = 0.0
    ) -> float:
        """Returns line current from armature current.

        In a shunt machine, terminal current splits between the armature branch
        and the shunt-field branch.

        Motor operation:

            IL = IA + If

        Generator operation:

            IL = IA - If

        where:

            If = Vt / (Rf + R_adj)

        Args:
            terminal_voltage: machine terminal voltage in volts.
            armature_current: armature current in amps.
            field_adjusting_resistance: external field-adjusting resistance in
                ohms. Defaults to ``0.0``.

        Returns:
            Line current in amps.

        Raises:
            ValueError: if ``terminal_voltage`` is negative.
            ValueError: if ``armature_current`` is negative.
            ValueError: if ``field_adjusting_resistance`` is negative.
            ValueError: if generator operation would produce negative line current.
        """
        self._validate_non_negative_terminal_voltage(terminal_voltage)
        self._validate_non_negative_armature_current(armature_current)

        field_current = self.field_current(
            applied_field_voltage=terminal_voltage,
            field_adjusting_resistance=field_adjusting_resistance
        )

        if self.operation_mode == "motor":
            return armature_current + field_current

        line_current = armature_current - field_current
        if line_current < 0:
            raise ValueError(
                "Generator line current would be negative because armature current is less than field current."
            )

        return line_current

    def armature_current_from_line_current(
        self,
        terminal_voltage: float,
        line_current: float,
        field_adjusting_resistance: float = 0.0
    ) -> float:
        """Returns armature current from line current.

        In a shunt machine, terminal current splits between the armature branch
        and the shunt-field branch.

        Motor operation:

            IA = IL - If

        Generator operation:

            IA = IL + If

        where:

            If = Vt / (Rf + R_adj)

        Args:
            terminal_voltage: machine terminal voltage in volts.
            line_current: external line current in amps.
            field_adjusting_resistance: external field-adjusting resistance in
                ohms. Defaults to ``0.0``.

        Returns:
            Armature current in amps.


        Raises:
            ValueError: if ``terminal_voltage`` is negative.
            ValueError: if ``line_current`` is negative.
            ValueError: if ``field_adjusting_resistance`` is negative.
            ValueError: if motor operation would produce negative armature
                current.
        """
        self._validate_non_negative_terminal_voltage(terminal_voltage)
        self._validate_non_negative_line_current(line_current)

        field_current = self.field_current(
            applied_field_voltage=terminal_voltage,
            field_adjusting_resistance=field_adjusting_resistance,
        )

        if self.operation_mode == "generator":
            return line_current + field_current

        armature_current = line_current - field_current
        if armature_current < 0:
            raise ValueError(
                "Motor armature current would be negative because line current is less than field current."
            )

        return armature_current

    def armature_current(self, terminal_voltage: float, induced_emf: float) -> float:
        """Returns armature current from terminal voltage and induced EMF.

        This method solves only the armature-branch current. It does not include
        shunt-field current. Use ``line_current_from_armature_current(...)`` or
        ``armature_current_from_line_current(...)`` when converting between
        armature current and external line current.

        Armature voltage equations:

            Motor:     IA = (Vt - E - Vb) / R_a_path
            Generator: IA = (E - Vt - Vb) / R_a_path

        where:

            R_a_path = Ra + Ri

        when a compensating resistance is configured, and:

            Vb = brush_drop_voltage

        when brush drop is configured.

        Args:
            terminal_voltage: machine terminal voltage in volts.
            induced_emf: internal generated EMF or motor back-EMF, in volts.

        Returns:
            Armature current in amps. The returned value may be negative if the
            supplied terminal conditions are inconsistent with the selected
            operating mode.

        Raises:
            ValueError: if ``terminal_voltage`` is negative.
        """
        self._validate_non_negative_terminal_voltage(terminal_voltage)

        armature_path_resistance = self._armature_path_resistance()
        brush_drop_voltage = self._brush_drop_value()

        return (
            (self._current_sign() * (terminal_voltage - induced_emf) - brush_drop_voltage) / armature_path_resistance
        )

    def induced_emf_from_terminal_conditions(
        self,
        terminal_voltage: float,
        armature_current: float,
    ) -> float:
        """Returns induced EMF from terminal voltage and armature current.

        This helper uses armature current, not line current. For shunt machines,
        convert line current to armature current first when the problem gives
        external line current.

        Electrical equations:

            Motor:     E = Vt - IA * R_a_path - Vb
            Generator: E = Vt + IA * R_a_path + Vb

        Args:
            terminal_voltage: machine terminal voltage in volts.
            armature_current: armature current in amps.

        Returns:
            Internal generated EMF or motor back-EMF, in volts.

        Raises:
            ValueError: if ``terminal_voltage`` is negative.
            ValueError: if ``armature_current`` is negative.
        """
        self._validate_non_negative_terminal_voltage(terminal_voltage)
        self._validate_non_negative_armature_current(armature_current)

        armature_path_resistance = self._armature_path_resistance()
        brush_drop_voltage = self._brush_drop_value()

        if self.operation_mode == "motor":
            return (
                terminal_voltage - (armature_current * armature_path_resistance) - brush_drop_voltage
            )
        else:  # generator
            return (
                terminal_voltage + (armature_current * armature_path_resistance) + brush_drop_voltage
            )

    def terminal_voltage_from_emf(
        self,
        armature_current: float,
        induced_emf: float,
    ) -> float:
        """Returns terminal voltage from armature current and induced EMF.

        This helper uses armature current, not line current.

        Electrical equations:

            Motor:     Vt = E + IA * R_a_path + Vb
            Generator: Vt = E - IA * R_a_path - Vb

        Args:
            armature_current: armature current in amps.
            induced_emf: internal generated EMF or motor back-EMF, in volts.

        Returns:
            Machine terminal voltage in volts.

        Raises:
            ValueError: if ``armature_current`` is negative.
        """

        self._validate_non_negative_armature_current(armature_current)

        armature_path_resistance = self._armature_path_resistance()
        brush_drop_voltage = self._brush_drop_value()

        if self.operation_mode == "motor":
            return (
                induced_emf + (armature_current * armature_path_resistance) + brush_drop_voltage
            )
        else:  # generator
            return (
                induced_emf - (armature_current * armature_path_resistance) - brush_drop_voltage
            )

    def terminal_voltage(self, armature_current: float) -> float:
        """Returns terminal voltage using the analytic EMF model only.

        This method uses armature current, not line current. If the problem gives
        external line current, convert it first with
        ``armature_current_from_line_current(...)``.

        The induced EMF is computed from the analytic model:

            E = K * flux * speed_rpm

        Electrical equations:

            Motor:     Vt = E + IA * R_a_path + Vb
            Generator: Vt = E - IA * R_a_path - Vb

        Args:
            armature_current: armature current in amps.

        Returns:
            Machine terminal voltage in volts.

        Raises:
            ValueError: if ``armature_current`` is negative.
            ValueError: if the analytic EMF model is not configured.
        """
        self._validate_non_negative_armature_current(armature_current)

        return self.terminal_voltage_from_emf(
            armature_current=armature_current,
            induced_emf=self.induced_emf(),
        )

    def induced_torque(self, armature_current: float) -> float:
        """Returns induced torque using the analytic EMF model only.

        This method uses armature current, not line current. If the problem gives
        external line current, convert it first with
        ``armature_current_from_line_current(...)``.

        The induced EMF is computed from the analytic model:

            E = K * flux * speed_rpm

        Then electromagnetic torque is:

            T = E * IA / omega

        where:

            omega = shaft speed in rad/s

        Args:
            armature_current: armature current in amps.

        Returns:
            Induced electromagnetic torque in N*m.

        Raises:
            ValueError: if ``armature_current`` is negative.
            ValueError: if the analytic EMF model is not configured.
        """
        self._validate_non_negative_armature_current(armature_current)

        omega = rpm_to_rad_s(self.speed_rpm)
        if omega == 0:
            raise ValueError("speed_rpm cannot be zero when computing torque.")

        return (self.induced_emf() * armature_current) / omega

    def shaft_speed_rpm(self, terminal_voltage: float, armature_current: float) -> float:
        """Solves shaft speed using the analytic EMF model only.

        This method uses armature current, not line current. If the problem gives
        external line current, convert it first with
        ``armature_current_from_line_current(...)``.

        Electrical equations:

            Motor:     E = Vt - IA * R_a_path - Vb
            Generator: E = Vt + IA * R_a_path + Vb

        Analytic speed model:

            E = K * flux * n_rpm

        Therefore:

            n_rpm = E / (K * flux)

        Args:
            terminal_voltage: machine terminal voltage in volts.
            armature_current: armature current in amps.

        Returns:
            Shaft speed in rpm.

        Raises:
            ValueError: if ``terminal_voltage`` is negative.
            ValueError: if ``armature_current`` is negative.
            ValueError: if the analytic EMF model is not configured.
        """
        self._validate_analytic_model()

        k_phi = self.k_constant * self.flux

        induced_emf = self.induced_emf_from_terminal_conditions(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current
        )

        return induced_emf / k_phi

    # Open-circuit characteristic (OCC) methods

    def induced_emf_from_terminal_voltage(
        self,
        terminal_voltage: float,
        field_adjusting_resistance: float = 0.0,
        desired_speed_rpm: float | None = None
    ) -> float:
        """Returns induced EMF using the OCC and shunt terminal voltage.

        For a shunt machine, terminal voltage determines shunt-field current:

            If = Vt / (Rf + R_adj)

        The magnetization curve then gives induced EMF at the requested speed:

            E = OCC(If) scaled to desired_speed_rpm

        If ``desired_speed_rpm`` is omitted, the machine's configured
        ``speed_rpm`` is used.

        Args:
            terminal_voltage: machine terminal voltage in volts.
            field_adjusting_resistance: external field-adjusting resistance in
                ohms. Defaults to ``0.0``.
            desired_speed_rpm: shaft speed at which the induced EMF is desired,
                in rpm.

        Returns:
            Induced EMF in volts.

        Raises:
            ValueError: if no magnetization curve is configured.
            ValueError: if ``terminal_voltage`` is negative.
            ValueError: if ``field_adjusting_resistance`` is negative.
            ValueError: if ``desired_speed_rpm`` is not positive.
        """
        if not self.has_magnetization_curve():
            raise ValueError("induced_emf_from_terminal_voltage requires a magnetization curve.")

        self._validate_non_negative_terminal_voltage(terminal_voltage)

        effective_speed_rpm = self._effective_speed_rpm(desired_speed_rpm)

    def _effective_speed_rpm(self, desired_speed_rpm: float | None) -> float:
        """Returns the configured speed or a validated explicit speed override."""
        if desired_speed_rpm is None:
            return self.speed_rpm

        self._validate_desired_speed_rpm(desired_speed_rpm)
        return desired_speed_rpm

    @staticmethod
    def _validate_desired_speed_rpm(desired_speed_rpm: float):
        if desired_speed_rpm <= 0:
            raise ValueError("desired_speed_rpm must be >= 0.")
