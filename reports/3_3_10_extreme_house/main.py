import os
import dacite
from enum import Enum
from common.house_data import HouseData
from common.web_input import create_web_input_from_house_data
from sample_generator.input_json_creator import convert_to_input_json
from simple_input_rewrite import estimate, get_master_days


def get_result_row(base_path: str, model_plan: str, wind_ratio: str, insulation_level: str, region: int) -> dict:
    """result.csvの行を生成する関数

    result.csv には各計算条件(間取り・開口部比率・断熱仕様)におけるUA・ηACの計算結果と、
    simple_input_rewrite.py を用いて推定した部位情報から算出した推定結果のUA・ηACが記録される。

    Args:
        base_path (str): 本スクリプトが格納されているディレクトリへのパス
        model_plan (str): 間取り(平屋／メゾネット)
        wind_ratio (str): 開口部比率(開口部比率20%／開口部比率70%)
        insulation_level (str): 断熱仕様(無断熱／等級7相当)
        region (int): ηAC, ηAHを計算する際の地域区分

    Returns:
        dict: result.csvに記録する以下の項目を格納する辞書
            * 間取り
            * 開口部比率
            * 断熱仕様
            * UA
            * 推定UA
            * ηAC
            * 推定ηAC
    """
    # in: 手動で作成した入力Excelを格納（※手動で作成）
    # out: 簡易入力(UA値など)から推定した部位情報を記録した入力Excelを格納
    xlsx_dirpath_in = os.path.join(base_path, 'in')
    xlsx_dirpath_out = os.path.join(base_path, 'out')

    xlsx_filename = f'input_excel_{model_plan}_{wind_ratio}_{insulation_level}.xlsx'
    xlsx_path_in = os.path.join(xlsx_dirpath_in, xlsx_filename)
    xlsx_path_out = os.path.join(xlsx_dirpath_out, xlsx_filename)

    # 簡易入力(UA値など)を算出
    json_dict_in = convert_to_input_json(xlsx_path_in)
    house_data_in = dacite.from_dict(data_class=HouseData, data=json_dict_in, config=dacite.Config(cast=[Enum]))
    web_input_in = create_web_input_from_house_data(region=region, house_data=house_data_in)

    # 簡易入力(UA値など)から部位情報を推定し、入力Excelに記録
    estimate(region=region,
             total_floor_area=web_input_in.A_A,
             main_floor_area=web_input_in.A_MR,
             other_floor_area=web_input_in.A_OR,
             A_env=web_input_in.A_env,
             U_A=web_input_in.U_A,
             eta_AC=web_input_in.eta_A_C,
             eta_AH=web_input_in.eta_A_H,
             xlsx_path=xlsx_path_out)

    # 推定した部位情報から、簡易入力(UAなど)を再計算
    json_dict_out = convert_to_input_json(xlsx_path_out)
    house_data_out = dacite.from_dict(data_class=HouseData, data=json_dict_out, config=dacite.Config(cast=[Enum]))
    web_input_out = create_web_input_from_house_data(region=region, house_data=house_data_out)

    # ηAC・ηAH を暖冷房期間で案分した値を算出
    daysnum_H, daysnum_C = get_master_days()[region - 1]
    eta_A_in = (web_input_in.eta_A_C * daysnum_C + web_input_in.eta_A_H * daysnum_H) / (daysnum_C + daysnum_H)
    eta_A_out = (web_input_out.eta_A_C * daysnum_C + web_input_out.eta_A_H * daysnum_H) / (daysnum_C + daysnum_H)

    return {
        '間取り': model_plan,
        '開口部比率': wind_ratio,
        '断熱仕様': insulation_level,
        'UA': web_input_in.U_A,
        '推定UA': web_input_out.U_A,
        'ηA': eta_A_in,
        '推定ηA': eta_A_out
    }


if __name__ == '__main__':
    import csv
    import itertools

    base_path = os.path.dirname(__file__)
    result_csv_path = os.path.join(base_path, 'result.csv')
    with open(result_csv_path, mode='w', encoding='utf-8', newline='') as result_csv:
        csv_writer = csv.DictWriter(result_csv, fieldnames=['間取り',
                                                            '開口部比率',
                                                            '断熱仕様',
                                                            'UA',
                                                            '推定UA',
                                                            'ηA',
                                                            '推定ηA'])
        csv_writer.writeheader()

        model_plans = ('平屋', 'メゾネット')
        wind_ratios = ('開口部20%', '開口部70%')
        insulation_levels = ('無断熱', '等級7相当')
        for (model_plan, wind_ratio, insulation_level) in itertools.product(model_plans, wind_ratios, insulation_levels):
            # NOTE: ηAC, ηAHを計算する際の地域区分は6としている
            result_row = get_result_row(base_path, model_plan, wind_ratio, insulation_level, region=6)
            csv_writer.writerow(result_row)
