
class MagnetizationCurve:

    def __init__(
        self,
        field_current_points: list[float],
        emf_points: list[float],
        reference_speed_rpm: float,
        residual_emf: float = 0.0
    ) -> None:
        # Data validation
        if len(field_current_points) != len(emf_points):
            raise ValueError("The data sets for field_current_points and emf_points must have the same size (length).")
        if len(field_current_points) < 2 or len(emf_points) < 2:
            raise ValueError("There must be at least a set of two (2) data points that define the magnetization curve (open-circuit characteristic).")

        if any(i < 0 for i in field_current_points):
            raise ValueError("There cannot be any negative values for field_current_points.")
        if any(e < 0 for e in emf_points):
            raise ValueError("There cannot be any negative values for emf_points.")

        for idx, current_point in enumerate(field_current_points[:-1]):
            if current_point >= field_current_points[idx + 1]:
                raise ValueError("Field current data points must be strictly increasing.")
        for idx, current_point in enumerate(emf_points[:-1]):
            if current_point > emf_points[idx + 1]:
                raise ValueError("EMF data points must be non-decreasing.")

        if reference_speed_rpm <= 0:
            raise ValueError("Reference speed, in rpm, must be positive and non-zero.")
        if residual_emf < 0:
            raise ValueError("Residual emf, in volts, cannot be negative.")

        self.field_current_points = field_current_points
        self.emf_points = emf_points
        self.reference_speed_rpm = reference_speed_rpm
        self.residual_emf = residual_emf

    def emf_from_field_current(self, field_current: float, speed_rpm: float) -> float:
        ...

    def field_current_from_emf(self, emf: float, speed_rpm: float) -> float:
        ...
