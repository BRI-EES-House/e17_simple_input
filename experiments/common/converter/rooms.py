import dataclasses
from common.house_data.room import Room, Ventilation


def convert_room(
    room: Room,
    floor_area: float,
) -> Room:
    floor_area_ratio = room.floor_area / floor_area if floor_area != 0.0 else 0.0
    volume = room.volume * floor_area_ratio
    ventilation_natural = room.ventilation.natural * floor_area_ratio

    return dataclasses.replace(room,
                               floor_area=floor_area,
                               volume=volume,
                               ventilation=Ventilation(natural=ventilation_natural))
