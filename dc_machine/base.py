from abc import ABC, abstractmethod
from magnetization import MagnetizationCurve


class DCMachine(ABC):
    '''
    Abstract base class for DC machines.

    Supports both motor and generator operation modes.
    '''

    VALID_MODES = ("motor", "generator")

    def __init__(
        self,
        armature_resistance: float,
        nominal_voltage: float,
        speed_rpm: float,
        operation_mode: str,
        flux: float | None = None,
        k_constant: float | None = None,
        magnetization_curve: MagnetizationCurve = None,
        shunt_resistance: float | None = None,
        series_resistance: float | None = None,
        brush_drop_voltage: float | None = None
    ) -> None:

        if armature_resistance <= 0:
            raise ValueError("Armature resistance, in ohms, must be positive and non-zero.")
        if nominal_voltage <= 0:
            raise ValueError("The supply voltage, in volts, must be positive and non-zero.")
        if speed_rpm <= 0:
            raise ValueError("The machine's speed, in rpm, must be positive and non-zero.")
        if operation_mode not in self.VALID_MODES:
            raise ValueError(f"Must provide one of the operation modes: {self.VALID_MODES}")
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
        self.brush_drop_voltage = brush_drop_voltage

        self.validate_resistance()

    def __str__(self) -> str:
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
        lines.append(f"{indent}{'Brush drop voltage:':<{label_w}} {self._brush_drop_value()} V\n")

        return "\n".join(lines)

    def has_analytic_model(self) -> bool:
        return self.flux is not None and self.k_constant is not None

    def has_magnetization_curve(self) -> bool:
        return self.magnetization_curve is not None

    def has_any_emf_model(self) -> bool:
        return self.magnetization_curve() or self.has_analytic_model()

    def _validate_analytic_model(self) -> None:
        if self.flux is None:
            raise ValueError("Flux must be provided when using the analytic EMF model.")
        if self.k_constant is None:
            raise ValueError("The machine's K constant must be provided when using the analytic EMF model.")
        if self.flux <= 0:
            raise ValueError("The magnetic flux, in weber, must be positive and non-zero.")
        if self.k_constant <= 0:
            raise ValueError("The machine's K constant must be positive and non-zero.")

    def _current_sign(self) -> int:
        """Returns +1 for motor mode (consumes power), -1 for generator mode (delivers power)."""
        return 1 if self.operation_mode == "motor" else -1

    def _brush_drop_value(self) -> float:
        """Returns brush drop voltage in volts, defaulting to 0.0 when disabled."""
        return 0.0 if self.brush_drop_voltage is None else self.brush_drop_voltage

    def induced_emf(self) -> float:
        """Calculates induced emf E using the analytic model E = K * flux * speed_rpm.

        This is the fallback model for machines that do not use a magnetization curve.
        Subclasses may override or supplement this behavior.

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
        """Validates if the machine has the required resistances configured."""
        ...

    @abstractmethod
    def field_current(self, applied_field_voltage: float) -> float:
        """Field current from applied field-winding voltage.
        - Separately excited: applied_field_voltage = Vf.
        - Shunt/Series/compound: applied_field_voltage = Vt (or branch voltage).
        """
        ...

    @abstractmethod
    def armature_current(self, terminal_voltage: float, induced_emf: float) -> float:
        """Armature current with optional brush drop Vb.
        Motor:     Ia = (Vt - E - Vb) / Ra
        Generator: Ia = (E - Vt - Vb) / Ra
        """
        ...

    @abstractmethod
    def terminal_voltage(self, armature_current: float) -> float:
        """Terminal voltage with optional brush drop Vb.

        Motor:     Vt = Vnom - Ia*Ra - Vb
        Generator: Vt = E - Ia*Ra - Vb
        """
        ...

    @abstractmethod
    def induced_torque(self, armature_current: float) -> float:
        """Electromagnetic (induced) torque in N·m.

        Typical form used in this project:
            T = (E * Ia) / omega

        where:
            E: induced emf in volts.
            Ia: armature current in amps.
            omega: mechanical angular speed in rad/s.

        Note:
            This depends on the E/K convention selected in each implementation.
            Keep induced_torque() consistent with induced_emf().
        """
        ...

    @abstractmethod
    def shaft_speed_rpm(self, terminal_voltage: float, armature_current: float) -> float:
        """Solve speed from electrical equation.
        Motor:     E = Vt - Ia*Ra - Vb
        Generator: E = Vt + Ia*Ra + Vb
        with E = K * flux * n_rpm
        """
        ...
