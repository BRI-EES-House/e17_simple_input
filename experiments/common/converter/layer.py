import dataclasses
from common.house_data.layer import Layer


class LayerConverter:
    def __init__(self, layer: Layer):
        self._layer = layer

    def convert(self, R: float):
        # 参照住戸の境界i に属する層j の熱抵抗・熱容量
        R_dash = self._layer.R
        C_dash = self._layer.C

        # 当該住戸の境界i に属する層j の熱容量を算出
        C = C_dash * R / R_dash if R_dash != 0.0 else 0.0

        # 層j を参照モデル住戸 -> 当該住戸に変換
        return dataclasses.replace(self._layer, thermal_resistance=R, thermal_capacity=C)
