from dataclasses import dataclass
from typing import Literal


@dataclass
class MechanicalVentilation:
    id: int
    root_type: Literal['type1', 'type2', 'type3']
    volume: float
    root: list[int]


def create_mechanical_ventilations(
    V_MR: float,
    V_OR: float,
    V_NR: float,
) -> list[MechanicalVentilation]:
    ventilation_rate = 0.5
    v_vent_MR = ventilation_rate * (V_MR + V_NR * V_MR / (V_MR + V_OR))
    v_vent_OR = ventilation_rate * (V_OR + V_NR * V_OR / (V_MR + V_OR))

    mechanical_ventilation_MR = MechanicalVentilation(id=0, root_type='type3', volume=v_vent_MR, root=[0, 2])
    mechanical_ventilation_OR = MechanicalVentilation(id=1, root_type='type3', volume=v_vent_OR, root=[1, 2])

    return [mechanical_ventilation_MR, mechanical_ventilation_OR]
