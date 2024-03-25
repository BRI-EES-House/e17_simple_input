from typing import Union, Literal
from dataclasses import dataclass
from common.utils.enums import Direction


@dataclass
class ISolarShadingPart:
    def calc_f_sh_c(self, region: int, direction: Direction) -> float:
        raise NotImplementedError()

    def calc_f_sh_h(self, region: int, direction: Direction) -> float:
        raise NotImplementedError()

    def calc_f_c(self, region: int, direction: Direction) -> float:
        raise NotImplementedError()

    def calc_f_h(self, region: int, direction: Direction) -> float:
        raise NotImplementedError()


@dataclass
class SolarShadingPartNothing(ISolarShadingPart):
    existence: Literal[False]

    def calc_f_sh_c(self, region: int, direction: Direction) -> float:
        return 1.00

    def calc_f_sh_h(self, region: int, direction: Direction) -> float:
        return 1.00

    def calc_f_c(self, region: int, direction: Direction) -> float:
        return 0.93

    def calc_f_h(self, region: int, direction: Direction) -> float:
        return 0.51


@dataclass
class SolarShadingPartSimple(ISolarShadingPart):
    existence: Literal[True]
    input_method: Literal['simple']
    depth: float
    d_h: float
    d_e: float

    def calc_f_sh_c(self, region: int, direction: Direction) -> float:
        # NOTE: 簡易計算法の場合は日よけ効果係数が未定義だが、便宜上1.00とする
        return 1.00

    def calc_f_sh_h(self, region: int, direction: Direction) -> float:
        # NOTE: 簡易計算法の場合は日よけ効果係数が未定義だが、便宜上1.00とする
        return 1.00

    def calc_f_c(self, region: int, direction: Direction):
        if region in [1, 2, 3, 4, 5, 6, 7]:
            if direction == Direction.S:
                f_c = 0.01 * (24 + 9  * (3*self.d_e + self.d_h)/self.depth)
            else:
                f_c = 0.01 * (16 + 24 * (2*self.d_e + self.d_h)/self.depth)
        else:
            if direction in [Direction.S, Direction.SE, Direction.SW]:
                f_c = 0.01 * (16 + 19 * (2*self.d_e + self.d_h)/self.depth)
            else:
                f_c = 0.01 * (16 + 24 * (2*self.d_e + self.d_h)/self.depth)

        return min(f_c, 0.93)

    def calc_f_h(self, region: int, direction: Direction):
        # 地域8では暖房期が存在しないが、便宜上0.0とする
        if region in [1, 2, 3, 4, 5, 6, 7]:
            if direction in [Direction.S, Direction.SE, Direction.SW]:
                f_h = 0.01 * (5  + 20 * (3*self.d_e + self.d_h)/self.depth)
            else:
                f_h = 0.01 * (10 + 15 * (2*self.d_e + self.d_h)/self.depth)
        else:
            f_h = 0.0

        return min(f_h, 0.72)


@dataclass
class SolarShadingPartDetail(ISolarShadingPart):
    existence: Literal[True]
    input_method: Literal['detail']
    x1: float
    x2: float
    x3: float
    y1: float
    y2: float
    y3: float
    z_x_pls: float
    z_x_mns: float
    z_y_pls: float
    z_y_mns: float

    def calc_f_sh_c(self, region: int, direction: Direction) -> float:
        raise NotImplementedError()

    def calc_f_sh_h(self, region: int, direction: Direction) -> float:
        raise NotImplementedError()

    def calc_f_c(self, region: int, direction: Direction) -> float:
        raise NotImplementedError()

    def calc_f_h(self, region: int, direction: Direction) -> float:
        raise NotImplementedError()


SolarShadingPart = Union[SolarShadingPartNothing,
                         SolarShadingPartSimple,
                         SolarShadingPartDetail]
