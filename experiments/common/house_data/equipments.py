from __future__ import annotations
from dataclasses import dataclass
from typing import Literal


@dataclass
class Equipments:
    heating_equipments: list[Equipment]
    cooling_equipments: list[Equipment]


@dataclass
class Equipment:
    # NOTE: 現状はracのみ対応
    id: int
    name: str
    equipment_type: Literal['rac']
    property: RacProperty


@dataclass
class RacProperty:
    space_id: int
    q_min: float
    q_max: float
    v_min: float
    v_max: float
    bf: float


def create_equipments(A_MR, A_OR) -> Equipments:
    eqp_c_MR, eqp_h_MR = _create_equipment_from_A_r(id=0, space_id=0, A_r=A_MR)
    eqp_c_OR, eqp_h_OR = _create_equipment_from_A_r(id=1, space_id=1, A_r=A_OR)

    return Equipments(heating_equipments=[eqp_h_MR, eqp_h_OR],
                      cooling_equipments=[eqp_c_MR, eqp_c_OR])


def _create_equipment_from_A_r(id, space_id, A_r) -> tuple[Equipment, Equipment]:
    q_rtd_c = 190.5 * A_r + 45.6
    q_rtd_h = 1.2090 * q_rtd_c - 85.1

    q_max_c = max(0.8462 * q_rtd_c + 1205.9, q_rtd_c)
    q_max_h = max(1.7597 * q_max_c - 413.7, q_rtd_h)

    q_min_c = 500
    q_min_h = 500

    v_max_c = 11.076 * (q_rtd_c / 1000.0) ** 0.3432
    v_max_h = 11.076 * (q_rtd_h / 1000.0) ** 0.3432

    v_min_c = v_max_c * 0.55
    v_min_h = v_max_h * 0.55

    bf_c = 0.2
    bf_h = 0.2

    prop_c = RacProperty(space_id=space_id,
                         q_min=q_min_c,
                         q_max=q_max_c,
                         v_min=v_min_c,
                         v_max=v_max_c,
                         bf=bf_c)
    prop_h = RacProperty(space_id=space_id,
                         q_min=q_min_h,
                         q_max=q_max_h,
                         v_min=v_min_h,
                         v_max=v_max_h,
                         bf=bf_h)

    eqp_c = Equipment(id=id,
                      name=f'cooling_equipment no.{id}',
                      equipment_type='rac',
                      property=prop_c)
    eqp_h = Equipment(id=id,
                      name=f'heating_equipment no.{id}',
                      equipment_type='rac',
                      property=prop_h)

    return eqp_c, eqp_h
