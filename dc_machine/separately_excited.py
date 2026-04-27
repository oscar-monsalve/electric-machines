from .base import DCMachine
from .magnetization import MagnetizationCurve
from .utils import rpm_to_rad_s


class SeparatelyExcitedMotorGenerator(DCMachine):
    """Separately excited DC motor/generator with externally supplied field current.

    This machine requires ``shunt_resistance`` to model the field winding supplied
    by an external DC source. The armature circuit may also include optional brush
    drop and optional compensating resistance.

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

    EMF model used in this class:
        - Preferred: magnetization curve ``E = f(If)`` scaled by speed.
        - Fallback: ``E = K * flux * speed_rpm``.
        - Torque: ``T = (E * Ia) / omega``, with ``omega = rpm_to_rad_s(speed_rpm)``.

    Assumptions kept for now:
        - no armature reaction
        - constant flux under the configured excitation model
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
        )

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

    def field_current(self, applied_field_voltage: float) -> float:
        """Calculates the field current for the separately excited machine using the equation: If = Vf / Rf.

        Args:
            applied_field_voltage: External DC voltage supplying the shunt winding.

        Returns:
            Field circuit current in amps.
        """
        return applied_field_voltage / self.shunt_resistance

    def induced_emf_from_field_voltage(self, applied_field_voltage: float) -> float:
        """Returns induced emf using the preferred excitation model.

        Preferred order:
        1. magnetization curve, if available.
        2. analytic model E = K * flux * speed_rpm (fallback).

        Args:
            applied_field_voltage: external DC voltage applied to the field winding, in volts.

        Returns:
            The induced emf in volts.

        Raises:
            ValueError: if no emf model is available.
        """
        field_current = self.field_current(applied_field_voltage)

        if self.has_magnetization_curve():
            return self.magnetization_curve.emf_from_field_current(
                field_current=field_current,
                desired_speed_rpm=self.speed_rpm
            )
        if self.has_analytic_model():
            return self.induced_emf()

        raise ValueError("Cannot compute induced emf: provide either magnetization_curve or both flux and k_constant.")

    def field_voltage_from_emf(self, emf: float) -> float:
        """Returns the field voltage required to produce the desired induced emf.

        This method requires a magnetization curve.

        Args:
            emf: desired induced emf in volts.

        Returns:
            The required field voltage in volts.

        Raises:
            ValueError: if no magnetization curve is available.
        """
        if not self.has_magnetization_curve():
            raise ValueError("field_voltage_from_emf requires a magnetization curve.")

        field_current = self.magnetization_curve.field_current_from_emf(
            emf=emf,
            desired_speed_rpm=self.speed_rpm
        )

        return field_current * self.shunt_resistance

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

        Note:
            The textbook form uses ``Ra``. In implementation, the armature-path
            resistance is ``Ra + Ri`` when a compensating resistance is configured.
        """
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

        Note:
            The textbook form uses ``Ra``. In implementation, the armature-path
            resistance is ``Ra + Ri`` when a compensating resistance is configured.
        """
        armature_path_resistance = self._armature_path_resistance()
        brush_drop_voltage = self._brush_drop_value()

        if self.operation_mode == "motor":
            return induced_emf + (armature_current * armature_path_resistance) + brush_drop_voltage
        else:  # generator
            return induced_emf - (armature_current * armature_path_resistance) - brush_drop_voltage

    def terminal_voltage_from_field_voltage(
        self,
        armature_current: float,
        applied_field_voltage: float
    ) -> float:
        """Returns terminal voltage using the preferred excitation model.

        Preferred order:
        1. magnetization curve, if available.
        2. analytic model E = K * flux * speed_rpm (fallback).

        Args:
            armature_current: armature current in amps.
            applied_field_voltage: external DC voltage applied to the field winding.

        Returns:
            Terminal voltage in volts.
        """
        induced_emf = self.induced_emf_from_field_voltage(applied_field_voltage)
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
        """
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

        Note:
            The textbook form uses ``Ra``. In implementation, the armature-path
            resistance is ``Ra + Ri`` when a compensating resistance is configured.
        """
        k_phi = self.k_constant * self.flux
        if k_phi == 0:
            raise ValueError("k_constant * flux must be non-zero.")

        armature_path_resistance = self._armature_path_resistance()
        brush_drop_voltage = self._brush_drop_value()
        if self.operation_mode == "motor":
            emf = terminal_voltage - (armature_current * armature_path_resistance) - brush_drop_voltage
        else:
            emf = terminal_voltage + (armature_current * armature_path_resistance) + brush_drop_voltage

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
        """
        omega = rpm_to_rad_s(self.speed_rpm)

        if omega == 0:
            raise ValueError("speed_rpm cannot be zero when computing torque.")

        return (induced_emf * armature_current) / omega

    def induced_torque_from_field_voltage(self, armature_current: float, applied_field_voltage: float) -> float:
        """Returns induced torque using the preferred excitation model.

        Preferred order:
        1. magnetization curve, if available.
        2. analytic model E = K * flux * speed_rpm (fallback).

        Args:
            armature_current: armature current in amps.
            applied_field_voltage: external DC voltage applied to the field winding.

        Returns:
            The induced torque in N·m.
        """
        induced_emf = self.induced_emf_from_field_voltage(applied_field_voltage)
        return self.induced_torque_from_emf(
            armature_current=armature_current,
            induced_emf=induced_emf
        )

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

        Note:
            The textbook form uses ``Ra``. In implementation, the armature-path
            resistance is ``Ra + Ri`` when a compensating resistance is configured.
        """
        if not self.has_magnetization_curve():
            raise ValueError("shaft_speed_rpm_from_field_current requires a magnetization curve.")

        armature_path_resistance = self._armature_path_resistance()
        brush_drop_voltage = self._brush_drop_value()
        if self.operation_mode == "motor":
            required_emf = terminal_voltage - (armature_current * armature_path_resistance) - brush_drop_voltage
        else:
            required_emf = terminal_voltage + (armature_current * armature_path_resistance) + brush_drop_voltage

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
    ) -> float:
        """Solves shaft speed from terminal conditions and applied field voltage.

        This helper is intended for separately excited OCC operation, where the
        field voltage determines field current through:
            If = Vf / Rf

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.
            applied_field_voltage: external DC voltage applied to the field winding.

        Returns:
            Shaft speed in rpm.
        """
        field_current = self.field_current(applied_field_voltage)
        return self.shaft_speed_rpm_from_field_current(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
            field_current=field_current,
        )

    # Power/losses

    def field_input_power(self, applied_field_voltage: float) -> float:
        """Returns external field-supply electrical input power in watts.

        Uses:

            P_field = Vf * If

        where ``If = Vf / Rf`` for the separately excited field circuit.
        """
        return applied_field_voltage * self.field_current(applied_field_voltage)

    def field_copper_losses(self, applied_field_voltage: float) -> float:
        """Returns field copper losses in watts for the separately excited field circuit.

        Uses:

            If = Vf / Rf
            P_cu,field = If^2 * Rf
        """
        field_current = self.field_current(applied_field_voltage)
        return (field_current ** 2) * self.shunt_resistance

    def copper_losses(
        self,
        armature_current: float,
        applied_field_voltage: float | None = None
    ) -> float:
        """Returns total copper losses in watts.

        Includes armature-path copper losses and, when ``applied_field_voltage`` is
        provided, field copper losses for the separately excited field circuit.
        """
        losses = self.armature_copper_losses(armature_current)
        if applied_field_voltage is not None:
            losses += self.field_copper_losses(applied_field_voltage)
        return losses

    def armature_terminal_power(self, terminal_voltage: float, armature_current: float) -> float:
        """Returns armature-side terminal electrical power in watts.

        Uses:

            P_t = Vt * Ia
        """
        return terminal_voltage * armature_current

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

        Shared relations:
            P_conv = E * Ia
            P_rot = P_mech + P_core + P_misc

        Motor:
            P_in = Vt * Ia
            P_out = P_conv - P_rot

        Generator:
            P_in = P_conv + P_rot
            P_out = Vt * Ia

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.
            induced_emf: operating-point induced emf in volts.

        Returns:
            Efficiency excluding field-supply power, in percent.

        Raises:
            ValueError: if the input-side power is zero or negative.
        """
        electromagnetic_power = self.electromagnetic_power(
            armature_current=armature_current,
            induced_emf=induced_emf
        )
        terminal_power = self.armature_terminal_power(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current
        )
        rotational_power = self.rotational_losses()

        if self.operation_mode == "motor":
            input_power = terminal_power
            output_power = electromagnetic_power - rotational_power
        else:  # generator
            input_power = electromagnetic_power + rotational_power
            output_power = terminal_power

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
        applied_field_voltage: float
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

        Shared relations:
            P_conv = E * Ia
            P_rot = P_mech + P_core + P_misc
            P_field = Vf * If

        Motor:
            P_in = Vt * Ia + P_field
            P_out = P_conv - P_rot

        Generator:
            P_in = P_conv + P_rot + P_field
            P_out = Vt * Ia

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.
            induced_emf: operating-point induced emf in volts.
            applied_field_voltage: external DC voltage applied to the field winding.

        Returns:
            Overall efficiency in percent.

        Raises:
            ValueError: if the input-side power is zero or negative.
        """

        electromagnetic_power = self.electromagnetic_power(
            armature_current=armature_current,
            induced_emf=induced_emf,
        )
        terminal_power = self.armature_terminal_power(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
        )
        rotational_power = self.rotational_losses()
        field_power = self.field_input_power(applied_field_voltage)

        if self.operation_mode == "motor":
            input_power = terminal_power + field_power
            output_power = electromagnetic_power - rotational_power
        else:
            input_power = electromagnetic_power + rotational_power + field_power
            output_power = terminal_power

        if input_power <= 0:
            raise ValueError("Cannot compute overall efficiency: input power must be positive and non-zero.")

        return (output_power / input_power) * 100.0

    def efficiency_excluding_field_power_from_field_voltage(
        self,
        terminal_voltage: float,
        armature_current: float,
        applied_field_voltage: float,
    ) -> float:
        """Returns efficiency excluding field-supply power using the preferred excitation model.

        This wrapper uses the same efficiency definition as
        ``efficiency_excluding_field_power(...)``, so armature-path copper losses and
        brush losses are accounted for implicitly through ``P_conv = E * Ia``.

        Preferred order:
            1. magnetization curve, if available.
            2. analytic model ``E = K * flux * speed_rpm`` (fallback).

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.
            applied_field_voltage: external DC voltage applied to the field winding.

        Returns:
            Efficiency excluding field-supply power, in percent.
        """
        induced_emf = self.induced_emf_from_field_voltage(applied_field_voltage)
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
    ) -> float:
        """Returns overall efficiency using the preferred excitation model.

        This wrapper uses the same overall-efficiency definition as
        ``overall_efficiency(...)``, so armature-path copper losses and brush losses
        are accounted for implicitly through ``P_conv = E * Ia``.

        Preferred order:
            1. magnetization curve, if available.
            2. analytic model ``E = K * flux * speed_rpm`` (fallback).

        This method includes external field-supply power in the efficiency
        calculation.

        Args:
            terminal_voltage: terminal voltage in volts.
            armature_current: armature current in amps.
            applied_field_voltage: external DC voltage applied to the field winding.

        Returns:
            Overall efficiency in percent.
        """
        induced_emf = self.induced_emf_from_field_voltage(applied_field_voltage)
        return self.overall_efficiency(
            terminal_voltage=terminal_voltage,
            armature_current=armature_current,
            induced_emf=induced_emf,
            applied_field_voltage=applied_field_voltage,
        )
