from abc import ABC, abstractmethod
from .magnetization import MagnetizationCurve


class DCMachine(ABC):
    """Abstract base class for DC machines.

    Stores common electrical and operating data shared by DC motor/generator
    models and defines the abstract interface implemented by specific
    topologies.
    """

    VALID_MODES = ("motor", "generator")

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
    ) -> None:

        if armature_resistance <= 0:
            raise ValueError("Armature resistance, in ohms, must be positive and non-zero.")
        if nominal_voltage <= 0:
            raise ValueError("The supply voltage, in volts, must be positive and non-zero.")
        if speed_rpm <= 0:
            raise ValueError("The machine's speed, in rpm, must be positive and non-zero.")
        if operation_mode not in self.VALID_MODES:
            raise ValueError(f"Must provide one of the operation modes: {self.VALID_MODES}")
        if compensating_resistance is not None and compensating_resistance <= 0:
            raise ValueError("The compensating resistance, in ohms, must be positive and non-zero.")
        if brush_drop_voltage is not None and brush_drop_voltage < 0:
            raise ValueError("The brush drop voltage must be >= 0.")

        self.armature_resistance = armature_resistance
        self.nominal_voltage = nominal_voltage
        self.speed_rpm = speed_rpm
        self.operation_mode = operation_mode
        self.flux = flux
        self.k_constant = k_constant
        self.magnetization_curve = magnetization_curve
        self.shunt_resistance = shunt_resistance
        self.series_resistance = series_resistance
        self.compensating_resistance = compensating_resistance
        self.brush_drop_voltage = brush_drop_voltage

        self.validate_resistance()

    def __str__(self) -> str:
        """Returns a multi-line human-readable summary of the machine data.

        The summary includes the common electrical and operating parameters
        configured for the machine instance, omitting optional values that are
        not set.
        """
        class_name = type(self).__name__
        indent = "    "
        label_w = 25

        lines = [f"{class_name}:"]
        lines.append(f"{indent}{'Armature resistance:':<{label_w}} {self.armature_resistance} Ω")
        lines.append(f"{indent}{'Supply voltage:':<{label_w}} {self.nominal_voltage} V")
        lines.append(f"{indent}{'Speed:':<{label_w}} {self.speed_rpm} rpm")
        lines.append(f"{indent}{'Operation mode:':<{label_w}} {self.operation_mode}")
        if self.flux is not None:
            lines.append(f"{indent}{'Flux:':<{label_w}} {self.flux} Wb")
        if self.k_constant is not None:
            lines.append(f"{indent}{'K constant:':<{label_w}} {self.k_constant}")
        if self.magnetization_curve is not None:
            lines.append(f"{indent}{'Magnetization curve:':<{label_w}} available")
        if self.shunt_resistance is not None:
            lines.append(f"{indent}{'Shunt resistance:':<{label_w}} {self.shunt_resistance} Ω")
        if self.series_resistance is not None:
            lines.append(f"{indent}{'Series resistance:':<{label_w}} {self.series_resistance} Ω")
        if self.compensating_resistance is not None:
            lines.append(f"{indent}{'Compensating resistance:':<{label_w}} {self.compensating_resistance} Ω")
        lines.append(f"{indent}{'Brush drop voltage:':<{label_w}} {self._brush_drop_value()} V\n")

        return "\n".join(lines)

    def _armature_path_resistance(self) -> float:
        """Returns the equivalent resistance seen by the armature current.

        This is the total resistance in the armature current path. If a compensating
        or auxiliary winding is modeled, its resistance is added in series with the
        armature resistance:

            R_a_path = R_a + R_i

        where:
            R_a: armature resistance
            R_i: compensating resistance, when present
        """
        if self.compensating_resistance is not None:
            return self.armature_resistance + self.compensating_resistance
        else:
            return self.armature_resistance

    def _validate_analytic_model(self) -> None:
        """Validates the analytic EMF model inputs.

        Raises:
            ValueError: if ``flux`` or ``k_constant`` is missing.
            ValueError: if ``flux`` or ``k_constant`` is not positive.
        """
        if self.flux is None:
            raise ValueError("Flux must be provided when using the analytic EMF model.")
        if self.k_constant is None:
            raise ValueError("The machine's K constant must be provided when using the analytic EMF model.")
        if self.flux <= 0:
            raise ValueError("The magnetic flux, in weber, must be positive and non-zero.")
        if self.k_constant <= 0:
            raise ValueError("The machine's K constant must be positive and non-zero.")

    def _current_sign(self) -> int:
        """Returns the sign convention used for current equations.

        Returns:
            +1 for motor mode
            -1 for generator mode
        """
        return 1 if self.operation_mode == "motor" else -1

    def _brush_drop_value(self) -> float:
        """Returns the configured brush-drop voltage in volts.

        If brush drop is not configured, returns ``0.0``.
        """
        return 0.0 if self.brush_drop_voltage is None else self.brush_drop_voltage

    def has_analytic_model(self) -> bool:
        """Returns whether the analytic EMF model is fully configured.

        The analytic model requires both ``flux`` and ``k_constant`` to be
        present. This helper only checks presence; positivity is validated when
        the analytic model is actually used.
        """
        return self.flux is not None and self.k_constant is not None

    def has_magnetization_curve(self) -> bool:
        """Returns whether a magnetization-curve / OCC model is available."""
        return self.magnetization_curve is not None

    def has_any_emf_model(self) -> bool:
        """Returns whether any EMF model is available for the machine.

        A machine is considered able to produce EMF calculations if it has
        either a magnetization curve or a fully specified analytic model.
        """
        return self.has_magnetization_curve() or self.has_analytic_model()

    def induced_emf(self) -> float:
        """Calculates induced emf E using the analytic model E = K * flux * speed_rpm.

        This is the analytic fallback model when a magnetization curve / OCC-based
        model is not being used. Subclasses may override or supplement this behavior.

        Current convention:
        - speed_rpm is stored in rpm.
        - K is defined so E = K * flux * speed_rpm.

        Important:
        If you switch to SI form E = K_e * flux * omega_rad_s, update this method
        and all K values consistently.

        Returns:
            The induced emf in volts.
        """
        self._validate_analytic_model()
        return self.k_constant * self.flux * self.speed_rpm

    @abstractmethod
    def validate_resistance(self) -> None:
        """Validates that the machine has the required winding resistances configured."""
        ...

    @abstractmethod
    def field_current(self, applied_field_voltage: float) -> float:
        """Returns field current from the applied field-winding voltage.

        Interpretation of ``applied_field_voltage`` depends on the machine type:
            - Separately excited: external field supply voltage ``Vf``
            - Shunt/series/compound: terminal or branch field voltage, as applicable
        """
        ...

    @abstractmethod
    def armature_current(self, terminal_voltage: float, induced_emf: float) -> float:
        """Returns armature current with optional brush drop ``Vb``.

        Typical forms used in this project:
            Motor:     Ia = (Vt - E - Vb) / Ra
            Generator: Ia = (E - Vt - Vb) / Ra

        Note:
            The exact source of ``E`` depends on the subclass implementation and may
            come from an analytic model or from operating-point helper methods.
        """
        ...

    @abstractmethod
    def terminal_voltage(self, armature_current: float) -> float:
        """Returns terminal voltage using the subclass's configured machine model.

        Typical forms used in this project:
            Motor:     Vt = Vnom - Ia*Ra - Vb
            Generator: Vt = E - Ia*Ra - Vb

        Note:
            The exact source of Vnom or E depends on the subclass implementation.
            Subclasses may use an analytic EMF model here and may also expose
            additional helper methods when operating-point excitation data is
            required, such as with magnetization-curve / OCC workflows.
        """
        ...

    @abstractmethod
    def induced_torque(self, armature_current: float) -> float:
        """Electromagnetic (induced) torque in N·m.

        Default contract for this project:
            T = (E * Ia) / omega

        where:
            E: induced emf in volts.
            Ia: armature current in amps.
            omega: mechanical angular speed in rad/s.

        Note:
            This abstract method does not prescribe how ``E`` is obtained.
            Subclasses may implement it using an analytic EMF model or provide
            additional helper methods when extra excitation data is required.
        """
        ...

    @abstractmethod
    def shaft_speed_rpm(self, terminal_voltage: float, armature_current: float) -> float:
        """Solve speed from the electrical equation.

        Motor:     E = Vt - Ia*Ra - Vb
        Generator: E = Vt + Ia*Ra + Vb

        If an analytic EMF model is used, a typical form is:
            E = K * flux * n_rpm

        Note:
            This base signature is sufficient only when the subclass can solve
            speed directly from its configured machine model. Subclasses may
            provide additional helper methods when excitation data is also
            required, such as with magnetization-curve/OCC operation.
        """
        ...
