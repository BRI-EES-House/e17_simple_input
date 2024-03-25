from dataclasses import dataclass
from typing import List, Optional, Literal, Union
import numpy as np

from common.house_data.layer import Layer
from common.house_data.solar_shading_part import SolarShadingPart
from common.utils.enums import Direction
from common.utils.func import get_nu_c, get_nu_h


@dataclass
class IBoundary:
    id: int
    name: str
    sub_name: str
    connected_room_id: int
    area: float
    is_solar_absorbed_inside: bool
    is_floor: bool
    h_c: float

    @property
    def RoomID(self) -> int:
        return self.connected_room_id

    @property
    def A(self) -> float:
        """面積 [m2]"""
        return self.area

    @property
    def IsFloor(self) -> bool:
        return self.is_floor


@dataclass
class ExternalOpaquePart(IBoundary):
    """不透明部位"""
    boundary_type: Literal['external_opaque_part']
    is_sun_striked_outside: bool
    direction: Optional[Direction]
    temp_dif_coef: float
    outside_emissivity: float
    outside_heat_transfer_resistance: float
    u_value: float
    inside_heat_transfer_resistance: float
    outside_solar_absorption: float
    solar_shading_part: Optional[SolarShadingPart]

    @property
    def R_se(self) -> float:
        return self.outside_heat_transfer_resistance

    @property
    def R_si(self) -> float:
        return self.inside_heat_transfer_resistance

    @property
    def U(self):
        return self.u_value

    @property
    def H(self):
        return self.temp_dif_coef

    @property
    def q(self) -> float:
        return self.A * self.U * self.H

    def calc_m_c(self, region: int) -> float:
        if not self.is_sun_striked_outside:
            return 0.0

        assert self.direction is not None
        assert self.solar_shading_part is not None

        nu_c = get_nu_c(region, self.direction)
        f_sh_c = self.solar_shading_part.calc_f_sh_c(region, self.direction)
        return self.A * 0.034 * self.U * f_sh_c * nu_c

    def calc_m_h(self, region: int) -> float:
        if not self.is_sun_striked_outside:
            return 0.0

        assert self.direction is not None
        assert self.solar_shading_part is not None

        nu_h = get_nu_h(region, self.direction)
        f_sh_h = self.solar_shading_part.calc_f_sh_h(region, self.direction)
        return self.A * 0.034 * self.U * f_sh_h * nu_h


@dataclass
class ExternalGeneralPart(IBoundary):
    """一般部位"""
    boundary_type: Literal['external_general_part']
    is_sun_striked_outside: bool
    direction: Optional[Direction]
    temp_dif_coef: float
    outside_emissivity: float
    outside_heat_transfer_resistance: float
    outside_solar_absorption: float
    layers: List[Layer]
    solar_shading_part: Optional[SolarShadingPart]

    @property
    def R_se(self) -> float:
        return self.outside_heat_transfer_resistance

    @property
    def R_si(self) -> float:
        # FIXME: 方位が未定義の場合の処理
        # ※現状の参照住戸では日射の有無に関わらず方位が設定されているため、しばらく対応不要
        assert self.direction is not None

        if self.direction == Direction.TOP:
            return 0.09
        elif self.direction == Direction.BOTTOM:
            return 0.15
        else:
            return 0.11

    @property
    def U(self):
        R_j = np.array([_.R for _ in self.layers])
        return 1 / (self.R_se + self.R_si + R_j.sum())

    @property
    def H(self):
        return self.temp_dif_coef

    @property
    def q(self) -> float:
        return self.A * self.U * self.H

    def calc_m_c(self, region: int) -> float:
        if not self.is_sun_striked_outside:
            return 0.0

        assert self.direction is not None
        assert self.solar_shading_part is not None

        nu_c = get_nu_c(region, self.direction)
        f_sh_c = self.solar_shading_part.calc_f_sh_c(region, self.direction)
        return self.A * 0.034 * self.U * f_sh_c * nu_c

    def calc_m_h(self, region: int) -> float:
        if not self.is_sun_striked_outside:
            return 0.0

        assert self.direction is not None
        assert self.solar_shading_part is not None

        nu_h = get_nu_h(region, self.direction)
        f_sh_h = self.solar_shading_part.calc_f_sh_h(region, self.direction)
        return self.A * 0.034 * self.U * f_sh_h * nu_h


@dataclass
class ExternalTransparentPart(IBoundary):
    """透明部位"""
    boundary_type: Literal['external_transparent_part']
    is_sun_striked_outside: bool
    direction: Optional[Direction]
    temp_dif_coef: float
    outside_emissivity: float
    outside_heat_transfer_resistance: float
    eta_value: float
    u_value: float
    inside_heat_transfer_resistance: float
    glass_area_ratio: float
    incident_angle_characteristics: Literal['single', 'multiple']
    solar_shading_part: Optional[SolarShadingPart]

    @property
    def R_se(self) -> float:
        return self.outside_heat_transfer_resistance

    @property
    def R_si(self) -> float:
        return self.inside_heat_transfer_resistance

    @property
    def U(self):
        return self.u_value

    @property
    def H(self):
        return self.temp_dif_coef

    @property
    def q(self) -> float:
        return self.A * self.U * self.H

    def calc_m_c(self, region: int) -> float:
        if not self.is_sun_striked_outside:
            return 0.0

        assert self.direction is not None
        assert self.solar_shading_part is not None

        nu_c = get_nu_c(region, self.direction)
        f_c = self.solar_shading_part.calc_f_c(region, self.direction)
        return self.A * self.eta_value * f_c * nu_c

    def calc_m_h(self, region: int) -> float:
        if not self.is_sun_striked_outside:
            return 0.0

        assert self.direction is not None
        assert self.solar_shading_part is not None

        nu_h = get_nu_h(region, self.direction)
        f_h = self.solar_shading_part.calc_f_h(region, self.direction)
        return self.A * self.eta_value * f_h * nu_h


@dataclass
class Ground(IBoundary):
    boundary_type: Literal['ground']
    layers: List[Layer]


@dataclass
class Internal(IBoundary):
    boundary_type: Literal['internal']
    rear_surface_boundary_id: int
    layers: List[Layer]


Boundary = Union[ExternalOpaquePart, ExternalGeneralPart, ExternalTransparentPart, Ground, Internal]
