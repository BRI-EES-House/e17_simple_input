from dataclasses import dataclass
from common.house_data import HouseData, ExternalGeneralPart, ExternalOpaquePart, ExternalTransparentPart, Ground


@dataclass
class WebInput:
    """簡易計算条件"""

    # 地域区分
    region: int

    # 延床面積 [m2]
    A_A: float

    # 主たる居室の面積 [m2]
    A_MR: float

    # その他の居室の面積 [m2]
    A_OR: float

    # 総外皮面積 [m2]
    A_env: float

    # 外皮平均熱貫流率UA [W/m2K]
    U_A: float

    # 暖房期日射熱取得率 [-]
    eta_A_H: float

    # 冷房期日射熱取得率 [-]
    eta_A_C: float


def create_web_input_from_house_data(
    region: int,
    house_data: HouseData,
) -> WebInput:
    """ HouseDataからWebInputを計算

    Args:
        region (int): 地域区分
        house_data (HouseData): HouseDataのインスタンス

    Returns:
        WebInput: 簡易計算条件
    """
    rooms = house_data.rooms
    boundaries = house_data.boundaries

    # 床面積
    A_MR, A_OR, A_NR = [_.floor_area for _ in rooms[:3]]
    A_A = A_MR + A_OR + A_NR

    # 外皮面積 (一般部位、不透明部位、透明部位、地盤の面積)
    external_part_types = [ExternalGeneralPart, ExternalOpaquePart, ExternalTransparentPart, Ground]
    envs = [_ for _ in boundaries if type(_) in external_part_types]
    A_env = sum(_.A for _ in envs)

    # 外皮平均熱貫流率
    q = sum(_.q for _ in envs if type(_) is not Ground)
    U_A = q / A_env

    # 暖房期・冷房期平均熱貫流率
    m_h = sum(_.calc_m_h(region) for _ in envs if type(_) is not Ground)
    m_c = sum(_.calc_m_c(region) for _ in envs if type(_) is not Ground)
    eta_A_H = m_h / A_env * 100
    eta_A_C = m_c / A_env * 100

    return WebInput(region=region,
                    A_A=A_A,
                    A_MR=A_MR,
                    A_OR=A_OR,
                    A_env=A_env,
                    U_A=U_A,
                    eta_A_H=eta_A_H,
                    eta_A_C=eta_A_C)
