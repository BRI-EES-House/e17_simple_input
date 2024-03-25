from dataclasses import dataclass


@dataclass
class Layer:
    name: str
    thermal_resistance: float
    thermal_capacity: float

    @property
    def R(self) -> float:
        return self.thermal_resistance

    @property
    def C(self) -> float:
        return self.thermal_capacity
