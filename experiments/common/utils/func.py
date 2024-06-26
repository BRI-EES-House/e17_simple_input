import dataclasses
from enum import Enum
import json
from typing import Tuple, Type, TypeVar

import dacite
from common.utils.enums import Direction


def get_nu_c(
    region: int,
    direction: Direction,
) -> float:
    return {
        Direction.TOP:    {1: 1.000, 2: 1.000, 3: 1.000, 4: 1.000, 5: 1.000, 6: 1.000, 7: 1.000, 8: 1.000},
        Direction.N:      {1: 0.329, 2: 0.341, 3: 0.335, 4: 0.322, 5: 0.373, 6: 0.341, 7: 0.307, 8: 0.325},
        Direction.NE:     {1: 0.430, 2: 0.412, 3: 0.390, 4: 0.426, 5: 0.437, 6: 0.431, 7: 0.415, 8: 0.414},
        Direction.E:      {1: 0.545, 2: 0.503, 3: 0.468, 4: 0.518, 5: 0.500, 6: 0.512, 7: 0.509, 8: 0.515},
        Direction.SE:     {1: 0.560, 2: 0.527, 3: 0.487, 4: 0.508, 5: 0.500, 6: 0.498, 7: 0.490, 8: 0.528},
        Direction.S:      {1: 0.502, 2: 0.507, 3: 0.476, 4: 0.437, 5: 0.472, 6: 0.434, 7: 0.412, 8: 0.480},
        Direction.SW:     {1: 0.526, 2: 0.548, 3: 0.550, 4: 0.481, 5: 0.520, 6: 0.491, 7: 0.479, 8: 0.517},
        Direction.W:      {1: 0.508, 2: 0.529, 3: 0.553, 4: 0.481, 5: 0.518, 6: 0.504, 7: 0.495, 8: 0.505},
        Direction.NW:     {1: 0.411, 2: 0.428, 3: 0.447, 4: 0.401, 5: 0.442, 6: 0.427, 7: 0.406, 8: 0.411},
        Direction.BOTTOM: {1: 0.000, 2: 0.000, 3: 0.000, 4: 0.000, 5: 0.000, 6: 0.000, 7: 0.000, 8: 0.000},
    }[direction][region]


def get_nu_h(
    region: int,
    direction: Direction,
) -> float:
    # NOTE: 8地域の場合は暖房期が存在しないため、便宜上0.000 とする
    return {
        Direction.TOP:    {1: 1.000, 2: 1.000, 3: 1.000, 4: 1.000, 5: 1.000, 6: 1.000, 7: 1.000, 8: 0.000},
        Direction.N:      {1: 0.260, 2: 0.263, 3: 0.284, 4: 0.256, 5: 0.238, 6: 0.261, 7: 0.227, 8: 0.000},
        Direction.NE:     {1: 0.333, 2: 0.341, 3: 0.348, 4: 0.330, 5: 0.310, 6: 0.325, 7: 0.281, 8: 0.000},
        Direction.E:      {1: 0.564, 2: 0.554, 3: 0.540, 4: 0.531, 5: 0.568, 6: 0.579, 7: 0.543, 8: 0.000},
        Direction.SE:     {1: 0.823, 2: 0.766, 3: 0.751, 4: 0.724, 5: 0.846, 6: 0.833, 7: 0.843, 8: 0.000},
        Direction.S:      {1: 0.935, 2: 0.856, 3: 0.851, 4: 0.815, 5: 0.983, 6: 0.936, 7: 1.023, 8: 0.000},
        Direction.SW:     {1: 0.790, 2: 0.753, 3: 0.750, 4: 0.723, 5: 0.815, 6: 0.763, 7: 0.848, 8: 0.000},
        Direction.W:      {1: 0.535, 2: 0.544, 3: 0.542, 4: 0.527, 5: 0.538, 6: 0.523, 7: 0.548, 8: 0.000},
        Direction.NW:     {1: 0.325, 2: 0.341, 3: 0.351, 4: 0.326, 5: 0.297, 6: 0.317, 7: 0.284, 8: 0.000},
        Direction.BOTTOM: {1: 0.000, 2: 0.000, 3: 0.000, 4: 0.000, 5: 0.000, 6: 0.000, 7: 0.000, 8: 0.000},
    }[direction][region]


def get_daynum(
    region: int,
) -> Tuple[int, int]:
    # 参照: 住宅仕様書11.6.5 暖冷房期間
    daynum_H, daynum_C = {
        1: (257, 53),  2: (252, 48),
        3: (244, 53),  4: (242, 53),
        5: (218, 57),  6: (169, 117),
        7: (122, 152), 8: (0,   265),
    }[region]

    return daynum_H, daynum_C


T = TypeVar('T')


def load_json(
    json_path: str,
    data_class: Type[T],
    encoding: str = 'utf-8',
) -> T:
    assert dataclasses.is_dataclass(data_class)

    with open(json_path, mode='r', encoding=encoding) as json_file:
        json_dict = json.load(json_file)

    return dacite.from_dict(data_class=data_class, data=json_dict, config=dacite.Config(cast=[Enum]))


def dump_json(
    json_path: str,
    data_class_obj: object,
    encoding: str = 'utf-8',
    indent: int = 4,
) -> None:
    assert dataclasses.is_dataclass(data_class_obj)

    # JSON出力時に、null が出力されないようにフィルタリング
    json_dict = dataclasses.asdict(data_class_obj, dict_factory=lambda d: {k: v for (k, v) in d if v is not None})

    with open(json_path, mode='w', encoding=encoding) as json_file:
        json.dump(json_dict, json_file, indent=indent)
