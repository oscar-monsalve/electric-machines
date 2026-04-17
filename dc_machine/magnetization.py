from numpy import interp


class MagnetizationCurve:

    def __init__(
        self,
        field_current_points: list[float],
        emf_points: list[float],
        reference_speed_rpm: float,
    ) -> None:
        # Data validation
        if len(field_current_points) != len(emf_points):
            raise ValueError("The data sets for field_current_points and emf_points must have the same size (length).")
        if len(field_current_points) < 2 or len(emf_points) < 2:
            raise ValueError("The data set defining the magnetization curve must have at least two (2) data points.")

        if any(i < 0 for i in field_current_points):
            raise ValueError("There cannot be any negative values for field_current_points.")
        if any(e < 0 for e in emf_points):
            raise ValueError("There cannot be any negative values for emf_points.")

        for idx, field_current_point in enumerate(field_current_points[:-1]):
            if field_current_point >= field_current_points[idx + 1]:
                raise ValueError("Field current data points must be strictly increasing.")
        for idx, emf_point in enumerate(emf_points[:-1]):
            if emf_point > emf_points[idx + 1]:
                raise ValueError("EMF data points must be non-decreasing.")

        if reference_speed_rpm <= 0:
            raise ValueError("Reference speed, in rpm, must be positive and non-zero.")

        self.field_current_points = field_current_points
        self.emf_points = emf_points
        self.reference_speed_rpm = reference_speed_rpm

    def emf_from_field_current(self, field_current: float, desired_speed_rpm: float) -> float:
        """Returns the internal generated emf interpolated from the magnetization curve
        and scaled to the desired shaft speed.

        Interpolation is clamped at the ends of the curve:
        - below the first field-current point, the first emf value is used
        - above the last field-current point, the last emf value is used

        Args:
            field_current: field/excitation current in amps.
            desired_speed_rpm: shaft speed at which the emf is desired, in rpm.

        Returns:
            The internal generated emf in volts at the desired speed.

        Raises:
            ValueError: if field_current is negative or if desired_speed_rpm is not positive.
        """

        if field_current < 0:
            raise ValueError("Field current, in amps, cannot be negative.")
        if desired_speed_rpm <= 0:
            raise ValueError("The machine's speed, in rpm, must be positive and non-zero.")

        reference_emf = interp(
            field_current,
            self.field_current_points,
            self.emf_points,
            left=self.emf_points[0],
            right=self.emf_points[-1]
        )

        return reference_emf * (desired_speed_rpm / self.reference_speed_rpm)

    def field_current_from_emf(self, emf: float, desired_speed_rpm: float) -> float:
        """Returns the field/excitation current required to produce a desired internal
        generated emf at a given shaft speed.

        The requested emf is first converted to its equivalent value at the
        reference speed, and then the magnetization curve is inverse-interpolated.

        Interpolation is clamped at the ends of the curve:
        - below the first emf point, the first field-current value is used
        - above the last emf point, the last field-current value is used

        Args:
            emf: desired internal generated emf in volts.
            desired_speed_rpm: shaft speed at which the emf is desired, in rpm.

        Returns:
            The required field/excitation current in amps.

        Raises:
            ValueError: if emf is negative or if desired_speed_rpm is not positive.
        """
        if emf < 0:
            raise ValueError("EMF, in volts, cannot be negative.")
        if desired_speed_rpm <= 0:
            raise ValueError("The machine's speed, in rpm, must be positive and non-zero.")

        reference_emf = emf * (self.reference_speed_rpm / desired_speed_rpm)
        reference_field_current = interp(
            reference_emf,
            self.emf_points,
            self.field_current_points,
            left=self.field_current_points[0],
            right=self.field_current_points[-1]
        )

        return reference_field_current
