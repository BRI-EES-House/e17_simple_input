import logging
import numpy as np
from common.web_input import WebInput
import common.house_data.boundary as bd
from . import boundary as bd_cvt


class BoundariesConverter:
    MAX_ROOM = 3

    def __init__(self, bds: list[bd.Boundary]):
        self._bds = bds
        self._gens = [_ for _ in bds if isinstance(_, bd.ExternalGeneralPart)]
        self._opqs = [_ for _ in bds if isinstance(_, bd.ExternalOpaquePart)]
        self._tras = [_ for _ in bds if isinstance(_, bd.ExternalTransparentPart)]
        self._itrs = [_ for _ in bds if isinstance(_, bd.Internal)]
        self._gnds = [_ for _ in bds if isinstance(_, bd.Ground)]
        self._gen_cvts = [bd_cvt.ExternalGeneralPartConverter(_)     for _ in self._gens]
        self._opq_cvts = [bd_cvt.ExternalOpaquePartConverter(_)      for _ in self._opqs]
        self._tra_cvts = [bd_cvt.ExternalTransparentPartConverter(_) for _ in self._tras]
        self._itr_cvts = [bd_cvt.InternalConverter(_)                for _ in self._itrs]
        self._gnd_cvts = [bd_cvt.GroundConverter(_)                  for _ in self._gnds]

    @property
    def A_dash_gen_i(self):
        return np.array([_.A for _ in self._gens])

    @property
    def A_dash_opq_i(self):
        return np.array([_.A for _ in self._opqs])

    @property
    def A_dash_tra_i(self):
        return np.array([_.A for _ in self._tras])

    @property
    def A_dash_itr_i(self):
        return np.array([_.A for _ in self._itrs])

    @property
    def A_dash_gnd_i(self):
        return np.array([_.A for _ in self._gnds])

    @property
    def IsFloor_gen_i(self):
        return np.array([_.IsFloor for _ in self._gens], dtype=np.bool_)

    @property
    def IsFloor_opq_i(self):
        return np.array([_.IsFloor for _ in self._opqs], dtype=np.bool_)

    @property
    def IsFloor_tra_i(self):
        return np.array([_.IsFloor for _ in self._tras], dtype=np.bool_)

    @property
    def IsFloor_itr_i(self):
        return np.array([_.IsFloor for _ in self._itrs], dtype=np.bool_)

    @property
    def IsFloor_gnd_i(self):
        return np.array([_.IsFloor for _ in self._gnds], dtype=np.bool_)

    @property
    def RoomID_gen_i(self):
        return np.array([_.RoomID for _ in self._gens], dtype=np.int32)

    @property
    def RoomID_opq_i(self):
        return np.array([_.RoomID for _ in self._opqs], dtype=np.int32)

    @property
    def RoomID_tra_i(self):
        return np.array([_.RoomID for _ in self._tras], dtype=np.int32)

    @property
    def RoomID_itr_i(self):
        return np.array([_.RoomID for _ in self._itrs], dtype=np.int32)

    @property
    def RoomID_gnd_i(self):
        return np.array([_.RoomID for _ in self._gnds], dtype=np.int32)

    def calc_A_dash_u(self):
        A_flr_gen_u = np.bincount(self.RoomID_gen_i, weights=self.A_dash_gen_i*self.IsFloor_gen_i, minlength=BoundariesConverter.MAX_ROOM)
        A_flr_opq_u = np.bincount(self.RoomID_opq_i, weights=self.A_dash_opq_i*self.IsFloor_opq_i, minlength=BoundariesConverter.MAX_ROOM)
        A_flr_tra_u = np.bincount(self.RoomID_tra_i, weights=self.A_dash_tra_i*self.IsFloor_tra_i, minlength=BoundariesConverter.MAX_ROOM)
        A_flr_itr_u = np.bincount(self.RoomID_itr_i, weights=self.A_dash_itr_i*self.IsFloor_itr_i, minlength=BoundariesConverter.MAX_ROOM)
        A_flr_gnd_u = np.bincount(self.RoomID_gnd_i, weights=self.A_dash_gnd_i*self.IsFloor_gnd_i, minlength=BoundariesConverter.MAX_ROOM)
        return A_flr_gen_u + A_flr_opq_u + A_flr_tra_u + A_flr_itr_u + A_flr_gnd_u

    def calc_A_dash_itr_u(self):
        return np.bincount(self.RoomID_itr_i, weights=self.A_dash_itr_i*self.IsFloor_itr_i, minlength=BoundariesConverter.MAX_ROOM)

    def calc_A_dash_gnd_u(self):
        return np.bincount(self.RoomID_gnd_i, weights=self.A_dash_gnd_i*self.IsFloor_gnd_i, minlength=BoundariesConverter.MAX_ROOM)

    def calc_A_env_u(self):
        A_gen_u = np.bincount(self.RoomID_gen_i, weights=self.A_dash_gen_i, minlength=BoundariesConverter.MAX_ROOM)
        A_opq_u = np.bincount(self.RoomID_opq_i, weights=self.A_dash_opq_i, minlength=BoundariesConverter.MAX_ROOM)
        A_tra_u = np.bincount(self.RoomID_tra_i, weights=self.A_dash_tra_i, minlength=BoundariesConverter.MAX_ROOM)
        return A_gen_u + A_opq_u + A_tra_u

    def calc_A_env_flr_u(self):
        A_flr_gen_u = np.bincount(self.RoomID_gen_i, weights=self.A_dash_gen_i*self.IsFloor_gen_i, minlength=BoundariesConverter.MAX_ROOM)
        A_flr_opq_u = np.bincount(self.RoomID_opq_i, weights=self.A_dash_opq_i*self.IsFloor_opq_i, minlength=BoundariesConverter.MAX_ROOM)
        A_flr_tra_u = np.bincount(self.RoomID_tra_i, weights=self.A_dash_tra_i*self.IsFloor_tra_i, minlength=BoundariesConverter.MAX_ROOM)
        return A_flr_gen_u + A_flr_opq_u + A_flr_tra_u

    def calc_q_u(self):
        q_dash_gen_i = self.calc_q_gen_i()
        q_dash_opq_i = self.calc_q_opq_i()
        q_dash_tra_i = self.calc_q_tra_i()
        q_gen_u = np.bincount(self.RoomID_gen_i, weights=q_dash_gen_i, minlength=BoundariesConverter.MAX_ROOM)
        q_opq_u = np.bincount(self.RoomID_opq_i, weights=q_dash_opq_i, minlength=BoundariesConverter.MAX_ROOM)
        q_tra_u = np.bincount(self.RoomID_tra_i, weights=q_dash_tra_i, minlength=BoundariesConverter.MAX_ROOM)
        return q_gen_u + q_opq_u + q_tra_u

    def calc_m_gen_c_u(self, region: int):
        m_gen_i = self.calc_m_gen_c_i(region)
        m_gen_u = np.bincount(self.RoomID_gen_i, weights=m_gen_i, minlength=BoundariesConverter.MAX_ROOM)
        return m_gen_u

    def calc_m_opq_c_u(self, region: int):
        m_opq_i = self.calc_m_opq_c_i(region)
        m_opq_u = np.bincount(self.RoomID_opq_i, weights=m_opq_i, minlength=BoundariesConverter.MAX_ROOM)
        return m_opq_u

    def calc_m_tra_c_u(self, region: int):
        m_tra_i = self.calc_m_tra_c_i(region)
        m_tra_u = np.bincount(self.RoomID_tra_i, weights=m_tra_i, minlength=BoundariesConverter.MAX_ROOM)
        return m_tra_u

    def calc_m_gen_h_u(self, region: int):
        m_gen_i = self.calc_m_gen_h_i(region)
        m_gen_u = np.bincount(self.RoomID_gen_i, weights=m_gen_i, minlength=BoundariesConverter.MAX_ROOM)
        return m_gen_u

    def calc_m_opq_h_u(self, region: int):
        m_opq_i = self.calc_m_opq_h_i(region)
        m_opq_u = np.bincount(self.RoomID_opq_i, weights=m_opq_i, minlength=BoundariesConverter.MAX_ROOM)
        return m_opq_u

    def calc_m_tra_h_u(self, region: int):
        m_tra_i = self.calc_m_tra_h_i(region)
        m_tra_u = np.bincount(self.RoomID_tra_i, weights=m_tra_i, minlength=BoundariesConverter.MAX_ROOM)
        return m_tra_u

    def calc_q_gen_i(self):
        return np.array([_.q for _ in self._gens])

    def calc_q_opq_i(self):
        return np.array([_.q for _ in self._opqs])

    def calc_q_tra_i(self):
        return np.array([_.q for _ in self._tras])

    def calc_m_gen_c_i(self, region: int):
        return np.array([_.calc_m_c(region) for _ in self._gens])

    def calc_m_opq_c_i(self, region: int):
        return np.array([_.calc_m_c(region) for _ in self._opqs])

    def calc_m_tra_c_i(self, region: int):
        return np.array([_.calc_m_c(region) for _ in self._tras])

    def calc_m_gen_h_i(self, region: int):
        return np.array([_.calc_m_h(region) for _ in self._gens])

    def calc_m_opq_h_i(self, region: int):
        return np.array([_.calc_m_h(region) for _ in self._opqs])

    def calc_m_tra_h_i(self, region: int):
        return np.array([_.calc_m_h(region) for _ in self._tras])

    def convert(self, web_input: WebInput):
        # =====================================================================
        # 変換に必要な各種パラメータを算出
        # =====================================================================

        A_MR = web_input.A_MR
        A_OR = web_input.A_OR
        A_NR = web_input.A_A - A_MR - A_OR
        A_u = [A_MR, A_OR, A_NR]
        A_env = web_input.A_env
        q = A_env * web_input.U_A
        m_h = A_env * web_input.eta_A_H / 100
        m_c = A_env * web_input.eta_A_C / 100

        q_dash_gen_i = self.calc_q_gen_i()
        q_dash_opq_i = self.calc_q_opq_i()
        q_dash_tra_i = self.calc_q_tra_i()
        m_dash_tra_h_i = self.calc_m_tra_h_i(web_input.region)
        m_dash_tra_c_i = self.calc_m_tra_c_i(web_input.region)

        A_dash_u = self.calc_A_dash_u()
        A_dash_env_u = self.calc_A_env_u()
        A_dash_env_flr_u = self.calc_A_env_flr_u()
        A_dash_itr_flr_u = self.calc_A_dash_itr_u()
        A_dash_gnd_flr_u = self.calc_A_dash_gnd_u()
        q_dash_u = self.calc_q_u()
        m_dash_gen_h_u = self.calc_m_gen_h_u(web_input.region)
        m_dash_opq_h_u = self.calc_m_opq_h_u(web_input.region)
        m_dash_tra_h_u = self.calc_m_tra_h_u(web_input.region)
        m_dash_gen_c_u = self.calc_m_gen_c_u(web_input.region)
        m_dash_opq_c_u = self.calc_m_opq_c_u(web_input.region)
        m_dash_tra_c_u = self.calc_m_tra_c_u(web_input.region)

        # =====================================================================
        # 外皮面積・q値・m値を各室用途に案分
        # =====================================================================

        # 外皮面積を案分
        with np.errstate(divide='ignore', invalid='ignore'):
            A_hat_env_u = np.nan_to_num(A_dash_env_u * A_u / A_dash_u, nan=0.0, posinf=0.0, neginf=0.0)
            A_env_u = np.nan_to_num(A_env * A_hat_env_u / np.sum(A_hat_env_u), nan=0.0, posinf=0.0, neginf=0.0)

        # q値を案分
        with np.errstate(divide='ignore', invalid='ignore'):
            q_hat_u = np.nan_to_num(q_dash_u * A_env_u / A_dash_env_u, nan=0.0, posinf=0.0, neginf=0.0)
            q_u = q * np.nan_to_num(q_hat_u / np.sum(q_hat_u), nan=0.0, posinf=0.0, neginf=0.0)

        # m値合計のうち、透明部位の分を算出
        with np.errstate(divide='ignore', invalid='ignore'):
            m_gen_c_u = np.nan_to_num(m_dash_gen_c_u * q_u / q_dash_u, nan=0.0, posinf=0.0, neginf=0.0)
            m_opq_c_u = np.nan_to_num(m_dash_opq_c_u * q_u / q_dash_u, nan=0.0, posinf=0.0, neginf=0.0)
            m_gen_h_u = np.nan_to_num(m_dash_gen_h_u * q_u / q_dash_u, nan=0.0, posinf=0.0, neginf=0.0)
            m_opq_h_u = np.nan_to_num(m_dash_opq_h_u * q_u / q_dash_u, nan=0.0, posinf=0.0, neginf=0.0)
        m_tra_c = m_c - np.sum(m_gen_c_u) - np.sum(m_opq_c_u)
        m_tra_h = m_h - np.sum(m_gen_h_u) - np.sum(m_opq_h_u)

        m_tra_c_min = m_tra_h_min = 0.0
        if m_tra_c < m_tra_c_min:
            logging.info(f'm_tra_c clipped ({m_tra_c} -> {m_tra_c_min})')
            m_tra_c = m_tra_c_min
        if m_tra_h < m_tra_h_min:
            logging.info(f'm_tra_h clipped ({m_tra_h} -> {m_tra_h_min})')
            m_tra_h = m_tra_h_min

        # m値合計(透明部位分)を案分
        with np.errstate(divide='ignore', invalid='ignore'):
            m_hat_tra_c_u = np.nan_to_num(m_dash_tra_c_u * A_env_u / A_dash_env_u, nan=0.0, posinf=0.0, neginf=0.0)
            m_hat_tra_h_u = np.nan_to_num(m_dash_tra_h_u * A_env_u / A_dash_env_u, nan=0.0, posinf=0.0, neginf=0.0)
            m_tra_c_u = np.nan_to_num(m_tra_c * m_hat_tra_c_u / np.sum(m_hat_tra_c_u), nan=0.0, posinf=0.0, neginf=0.0)
            m_tra_h_u = np.nan_to_num(m_tra_h * m_hat_tra_h_u / np.sum(m_hat_tra_h_u), nan=0.0, posinf=0.0, neginf=0.0)

        # =====================================================================
        # 外皮面積・q値・m値を、各室用途から各外皮に案分
        # =====================================================================

        # 外皮・一般部位
        with np.errstate(divide='ignore', invalid='ignore'):
            A_gen_i = self.A_dash_gen_i * A_env_u[self.RoomID_gen_i] / A_dash_env_u[self.RoomID_gen_i]
            q_gen_i = q_dash_gen_i * q_u[self.RoomID_gen_i] / q_dash_u[self.RoomID_gen_i]
        A_gen_i = np.nan_to_num(A_gen_i)
        q_gen_i = np.nan_to_num(q_gen_i)
        new_gens = [converter.convert(A, q) for (converter, A, q) in zip(self._gen_cvts, A_gen_i, q_gen_i)]

        # 外皮・不透明部位
        with np.errstate(divide='ignore', invalid='ignore'):
            A_opq_i = self.A_dash_opq_i * A_env_u[self.RoomID_opq_i] / A_dash_env_u[self.RoomID_opq_i]
            q_opq_i = q_dash_opq_i * q_u[self.RoomID_opq_i] / q_dash_u[self.RoomID_opq_i]
        A_opq_i = np.nan_to_num(A_opq_i)
        q_opq_i = np.nan_to_num(q_opq_i)
        new_opqs = [converter.convert(A, q) for (converter, A, q) in zip(self._opq_cvts, A_opq_i, q_opq_i)]

        # 外皮・透明部位
        with np.errstate(divide='ignore', invalid='ignore'):
            A_tra_i = self.A_dash_tra_i * A_env_u[self.RoomID_tra_i] / A_dash_env_u[self.RoomID_tra_i]
            q_tra_i = q_dash_tra_i * q_u[self.RoomID_tra_i] / q_dash_u[self.RoomID_tra_i]
            m_tra_c_i = m_dash_tra_c_i * m_tra_c_u[self.RoomID_tra_i] / m_dash_tra_c_u[self.RoomID_tra_i]
            m_tra_h_i = m_dash_tra_h_i * m_tra_h_u[self.RoomID_tra_i] / m_dash_tra_h_u[self.RoomID_tra_i]
        A_tra_i = np.nan_to_num(A_tra_i, nan=0.0, posinf=0.0, neginf=0.0)
        q_tra_i = np.nan_to_num(q_tra_i, nan=0.0, posinf=0.0, neginf=0.0)
        m_tra_c_i = np.nan_to_num(m_tra_c_i, nan=0.0, posinf=0.0, neginf=0.0)
        m_tra_h_i = np.nan_to_num(m_tra_h_i, nan=0.0, posinf=0.0, neginf=0.0)
        new_tras = [converter.convert(web_input.region, A, q, m_c, m_h) for (converter, A, q, m_c, m_h)
                    in zip(self._tra_cvts, A_tra_i, q_tra_i, m_tra_c_i, m_tra_h_i)]

        # =====================================================================
        # 外皮以外の床面積を、各内壁・地盤に案分
        # =====================================================================

        # 当該住戸の室用途u における床面積合計のうち、外皮でない部分を算出
        with np.errstate(divide='ignore', invalid='ignore'):
            A_env_flr_u = np.nan_to_num(A_dash_env_flr_u * A_env_u / A_dash_env_u, nan=0.0, posinf=0.0, neginf=0.0)
        A_nenv_flr_u = A_u - A_env_flr_u

        A_nenv_flr_u_min = 0.0
        if np.any(A_nenv_flr_u < A_nenv_flr_u_min):
            logging.info(f'A_nenv_flr_u clipped ({A_env_flr_u} -> {A_nenv_flr_u_min})')
            A_nenv_flr_u = np.clip(A_nenv_flr_u, a_min=A_nenv_flr_u_min, a_max=None)

        # 当該住戸の室用途u における内壁・地盤の床面積合計を算出
        with np.errstate(divide='ignore', invalid='ignore'):
            A_itr_flr_u = np.nan_to_num(A_nenv_flr_u * A_dash_itr_flr_u / (A_dash_itr_flr_u + A_dash_gnd_flr_u), nan=0.0, posinf=0.0, neginf=0.0)
            A_gnd_flr_u = np.nan_to_num(A_nenv_flr_u * A_dash_gnd_flr_u / (A_dash_itr_flr_u + A_dash_gnd_flr_u), nan=0.0, posinf=0.0, neginf=0.0)

        # 当該住戸の境界i が属する室用途u における内壁・地盤の床面積合計を算出(それぞれ shape=i)
        A_dash_itr_flr_u_i = A_dash_itr_flr_u[self.RoomID_itr_i]
        A_dash_gnd_flr_u_i = A_dash_gnd_flr_u[self.RoomID_gnd_i]
        A_itr_flr_u_i = A_itr_flr_u[self.RoomID_itr_i]
        A_gnd_flr_u_i = A_gnd_flr_u[self.RoomID_gnd_i]

        # 当該住戸の内壁i／地盤i の面積を算出
        # TODO: 屋根の内壁面積を、裏面の床面積で上書きする必要がある。
        A_itr_i = self.A_dash_itr_i
        A_gnd_i = self.A_dash_gnd_i
        with np.errstate(divide='ignore', invalid='ignore'):
            A_itr_i[self.IsFloor_itr_i] *= np.nan_to_num(A_itr_flr_u_i[self.IsFloor_itr_i] / A_dash_itr_flr_u_i[self.IsFloor_itr_i],
                                                         nan=0.0, posinf=0.0, neginf=0.0)
            A_gnd_i[self.IsFloor_gnd_i] *= np.nan_to_num(A_gnd_flr_u_i[self.IsFloor_gnd_i] / A_dash_gnd_flr_u_i[self.IsFloor_gnd_i],
                                                         nan=0.0, posinf=0.0, neginf=0.0)

        new_itrs = [converter.convert(A) for (converter, A) in zip(self._itr_cvts, A_itr_i)]
        new_gnds = [converter.convert(A) for (converter, A) in zip(self._gnd_cvts, A_gnd_i)]

        # =====================================================================
        # 変換後の各境界を出力
        # =====================================================================

        # TODO: 内壁・地盤の面積計算をどうやって実装するか要検討
        new_boundaries: list[bd.Boundary] = []
        new_boundaries.extend(new_gens)
        new_boundaries.extend(new_opqs)
        new_boundaries.extend(new_tras)
        new_boundaries.extend(new_itrs)
        new_boundaries.extend(new_gnds)

        return sorted(new_boundaries, key=lambda _: _.id)
