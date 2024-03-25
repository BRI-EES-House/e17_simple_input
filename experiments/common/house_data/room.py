from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Union


@dataclass
class Room:
    id: int
    name: str
    sub_name: str
    floor_area: float
    volume: float
    ventilation: Ventilation
    furniture: Furniture
    schedule: Schedule


@dataclass
class Ventilation:
    natural: float


Furniture = Union['FurnitureDefault', 'FurnitureSpecify']


@dataclass
class FurnitureDefault:
    input_method: Literal['default']


@dataclass
class FurnitureSpecify:
    input_method: Literal['specify']
    heat_capacity: float
    heat_cond: float
    moisture_capacity: float
    moisture_cond: float


@dataclass
class Schedule:
    name: str
