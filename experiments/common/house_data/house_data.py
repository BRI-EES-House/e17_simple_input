from dataclasses import dataclass
from common.house_data.boundary import Boundary
from common.house_data.room import Room
from common.house_data.mechanical_ventilation import MechanicalVentilation
from common.house_data.equipments import Equipments


@dataclass
class HouseData:
    common: dict
    building: dict

    # 居室
    rooms: list[Room]

    # 境界
    boundaries: list[Boundary]

    # 機械換気
    mechanical_ventilations: list[MechanicalVentilation]

    # 設備
    equipments: Equipments
