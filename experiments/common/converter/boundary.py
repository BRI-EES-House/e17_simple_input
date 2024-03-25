import dataclasses
import logging
import numpy as np
import common.house_data.boundary as bd
from common.utils.func import get_nu_c, get_nu_h, get_daynum
from .layer import LayerConverter


class ExternalOpaquePartConverter:
    def __init__(self, boundary: bd.ExternalOpaquePart):
        self._bd = boundary

    def convert(self, A: float, q: float):
        # 当該住戸における温度差係数・表面熱抵抗は、参照住戸と同じとする
        H = self._bd.H
        R_si = self._bd.R_si
        R_se = self._bd.R_se

        # 当該住戸における境界i の U値を算出
        # TODO: U値が上限値をとる頻度を調査
        U = 0.0
        if A * H != 0.0:
            U = q / (A * H)

        U_max = 1 / (R_si + R_se)
        if U > U_max:
            logging.info(f'boundary id {self._bd.id:<4}: U clipped ({U} -> {U_max})')
            U = U_max

        # 境界i を参照住戸 -> 当該住戸に変換
        return dataclasses.replace(self._bd, area=A, u_value=U)


class ExternalTransparentPartConverter:
    def __init__(self, boundary: bd.ExternalTransparentPart):
        self._bd = boundary

    def convert(self, region: int, A: float, q: float, m_c: float, m_h: float):
        # FIXME: 日射無しのケースを想定できていない
        # ※現状の参照住戸では全て日よけが定義されているため、しばらく対応不要
        assert self._bd.is_sun_striked_outside
        assert self._bd.direction is not None
        assert self._bd.solar_shading_part is not None

        # 当該住戸における温度差係数・表面熱抵抗・日射熱取得補正係数・方位係数は参照住戸と同じとする
        H = self._bd.H
        R_si = self._bd.R_si
        R_se = self._bd.R_se
        f_c = self._bd.solar_shading_part.calc_f_c(region, self._bd.direction)
        f_h = self._bd.solar_shading_part.calc_f_h(region, self._bd.direction)
        nu_c = get_nu_c(region, self._bd.direction)
        nu_h = get_nu_h(region, self._bd.direction)

        # 当該住戸における境界i の U値を算出
        U = 0.0
        if A * H != 0.0:
            U = q / (A * H)

        U_max = 1 / (R_si + R_se)
        if U > U_max:
            logging.info(f'boundary id {self._bd.id:<4}: U clipped ({U} -> {U_max})')
            U = U_max

        # 当該住戸における暖房期のη値を算出
        eta_h = 0.0
        if A * f_h * nu_h != 0.0:
            eta_h = m_h / (A * f_h * nu_h)

        # 当該住戸における冷房期のη値を算出
        eta_c = 0.0
        if A * f_c * nu_c != 0.0:
            eta_c = m_c / (A * f_c * nu_c)

        # 境界i のη値を決定するため、暖房期・冷房期のη値を暖冷房期間で案分
        daynum_h, daynum_c = get_daynum(region)
        eta = (daynum_h * eta_h  + daynum_c * eta_c)  / (daynum_h + daynum_c)

        # NOTE: 上限値は0.88 かも?要確認
        eta_max = 1.0
        if eta > eta_max:
            logging.info(f'boundary id {self._bd.id:<4}: eta clipped ({eta} -> {eta_max})')
            eta = eta_max

        # 境界i を参照住戸 -> 当該住戸に変換
        return dataclasses.replace(self._bd, area=A, u_value=U, eta_value=eta)


class ExternalGeneralPartConverter:
    def __init__(self, boundary: bd.ExternalGeneralPart):
        self._bd = boundary
        self._layer_converters = [LayerConverter(_) for _ in boundary.layers]

    def convert(self, A_i: float, q_i: float):
        # 当該住戸における温度差係数・表面熱抵抗は、参照住戸と同じとする
        H = self._bd.H
        R_si = self._bd.R_si
        R_se = self._bd.R_se

        # 当該住戸における境界i の熱抵抗のうち、表面熱抵抗を除いた値を算出
        R_lys_i = 0.0
        if q_i != 0.0:
            R_lys_i = A_i * H / q_i - R_si - R_se

        R_min = 0.0
        if R_lys_i < R_min:
            logging.info(f'boundary id {self._bd.id:<4}: R_lys_i clipped ({R_lys_i} -> {R_min})')
            R_lys_i = R_min

        # 参照住戸における各層の熱抵抗を取得
        R_dash_lys_i_j = np.array([_.R for _ in self._bd.layers])
        R_dash_lys_i = np.sum(R_dash_lys_i_j)

        # 当該住戸における各層の熱抵抗を算出
        with np.errstate(divide='ignore', invalid='ignore'):
            R_lys_i_j = R_dash_lys_i_j * R_lys_i / R_dash_lys_i
        R_lys_i_j = np.nan_to_num(R_lys_i_j, nan=0.0, posinf=0.0, neginf=0.0)

        # 境界i に属する層j を、それぞれ参照モデル住戸 -> 当該住戸 に変換
        converted_layers = [converter.convert(R) for converter, R in zip(self._layer_converters, R_lys_i_j)]
        # 境界i を参照モデル住戸 -> 当該住戸に変換
        return dataclasses.replace(self._bd, area=A_i, layers=converted_layers)


class InternalConverter:
    def __init__(self, boundary: bd.Internal):
        self._bd = boundary

    def convert(self, A: float):
        # TODO: 内壁の各層は deepcopy されているのか？要確認
        return dataclasses.replace(self._bd, area=A)


class GroundConverter:
    def __init__(self, boundary: bd.Ground):
        self._bd = boundary

    def convert(self, A: float):
        # TODO: 地盤の各層は deepcopy されているのか？要確認
        return dataclasses.replace(self._bd, area=A)
