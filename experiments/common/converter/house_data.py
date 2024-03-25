import dataclasses
from common.house_data.house_data import HouseData
from common.house_data.mechanical_ventilation import create_mechanical_ventilations
from common.house_data.equipments import create_equipments
from common.converter.rooms import convert_room
from common.converter.boundaries import BoundariesConverter
from common.web_input import WebInput


class HouseDataConverter:
    def __init__(self, house_data: HouseData):
        self._house_data = house_data
        self._boundaries_converter = BoundariesConverter(house_data.boundaries)

    def convert(self, web_input: WebInput):
        # 室
        A_MR = web_input.A_MR
        A_OR = web_input.A_MR
        A_NR = web_input.A_A - A_MR - A_OR
        A_u = [A_MR, A_OR, A_NR]
        new_rooms = [convert_room(room, A) for room, A in zip(self._house_data.rooms, A_u)]

        # 境界
        new_boundaries = self._boundaries_converter.convert(web_input)

        # 全般換気設備
        V_MR, V_OR, V_NR = [_.volume for _ in new_rooms]
        new_mec_vents = create_mechanical_ventilations(V_MR, V_OR, V_NR)

        # 暖冷房機器
        new_equipments = create_equipments(A_MR, A_OR)

        return dataclasses.replace(self._house_data,
                                   rooms=new_rooms,
                                   boundaries=new_boundaries,
                                   mechanical_ventilations=new_mec_vents,
                                   equipments=new_equipments)
