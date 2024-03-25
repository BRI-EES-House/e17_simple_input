import csv
import json
import os, sys
from common.web_input import create_web_input_from_house_data
from common.house_data import HouseData
from common.utils.func import load_json
from experiments.simple_input_r5 import estimate, to_json


def create_new_house_data(
    index: str,
    region_name: str,
    model_plan: str,
    structure: str,
    input_xlsx_dirpath: str,
    input_json_dirpath: str
) -> None:
    """新しい簡易入力法(R5年)で・入力Excel・入力JSONを生成する関数

    Args:
        index (str): インデックス(0, 1, 2, ...)
        region_name (str): 地域名(岩見沢 | 岡山 | 那覇)
        model_plan (str): 間取り(戸建2F | 戸建平屋 | 共同3LDK一般)
        structure (str): 断熱位置(床下断熱 | 基礎断熱 | 無)
        input_xlsx_dirpath (str): 入力Excelを保存するディレクトリ
        input_json_dirpath (str): 入力JSONを保存するディレクトリ
    """
    region = {
        '岩見沢':   2,
        '岡山':     6,
        '那覇':     8,
    }[region_name]

    tatekata = {
        '戸建2F': '戸建住宅',
        '戸建平屋': '戸建住宅',
        '共同3LDK一般': '共同住宅',
    }[model_plan]

    # コントロールデータの簡易計算条件(≒住宅Webプログラムの画面入力)を算出
    house_data_path = os.path.join(input_json_dirpath, 'house_data_{}.json'.format(index))
    house_data = load_json(house_data_path, data_class=HouseData)
    web_input = create_web_input_from_house_data(region, house_data)

    # R5年度に検討した簡易入力法(simple_input_r5.py)を用いて、対照群の入力Excelを生成
    new_input_xlsx_path = os.path.join(input_xlsx_dirpath, f'new_input_{str(index)}.xlsx')
    estimate(region=web_input.region,
             total_floor_area=web_input.A_A,
             main_floor_area=web_input.A_MR,
             other_floor_area=web_input.A_OR,
             A_env=web_input.A_env,
             ua=web_input.U_A,
             eta_ac=web_input.eta_A_C,
             eta_ah=web_input.eta_A_H,
             tatekata=tatekata,
             structure=structure,
             #structure="床断熱",
             xlsx_path=new_input_xlsx_path)

    # 対照群の入力JSONを生成
    new_house_data = to_json(new_input_xlsx_path)
    new_house_data_path = os.path.join(input_json_dirpath, 'new_house_data_{}.json'.format(index))
    with open(new_house_data_path, mode='w') as new_house_data_file:
        json.dump(new_house_data, new_house_data_file, indent=4)
    new_house_data_loaded = load_json(new_house_data_path, data_class=HouseData)
    reconstructed_web_input = create_web_input_from_house_data(region, new_house_data_loaded)

    DD_h, DD_c = get_master_days()[web_input.region-1]
    eta_A_org =get_eta_avg(web_input.eta_A_C, web_input.eta_A_H, DD_c, DD_h)
    eta_A_reconstructed =get_eta_avg(reconstructed_web_input.eta_A_C, reconstructed_web_input.eta_A_H, DD_c, DD_h)

    print("")
    print("復元された条件")
    print("-------------------------------------------------")
    print("延床面積: {} [㎡]".format(reconstructed_web_input.A_A))
    print(" 主たる居室: {} [㎡]".format(reconstructed_web_input.A_MR))
    print(" その他居室: {} [㎡]".format(reconstructed_web_input.A_OR))
    print("外皮総面積: {} [㎡]".format(reconstructed_web_input.A_env))
    print("外皮平均熱貫流率: {} [W/K]".format(reconstructed_web_input.U_A))
    print("暖房期平均日射熱取得率: {}".format(reconstructed_web_input.eta_A_H))
    print("冷房期平均日射熱取得率: {}".format(reconstructed_web_input.eta_A_C))
    print("")

    if abs(reconstructed_web_input.U_A - web_input.U_A) > 1.0e-3:
        sys.stderr.write("{},{},{},{},{},{}\n".format(index, region_name, model_plan, structure, web_input.U_A, reconstructed_web_input.U_A))

    if abs(eta_A_reconstructed - eta_A_org) > 1.0e-3:
        sys.stderr.write("{},{},{},{},{},{}\n".format(index, region_name, model_plan, structure, eta_A_org, eta_A_reconstructed))

def get_master_days():
    """暖房度日、冷房度日"""
    return [
        [257, 53],
        [252, 48],
        [244, 53],
        [242, 53],
        [218, 57],
        [169, 117],
        [122, 152],
        [0, 265],
    ]

def get_eta_avg(eta_ac, eta_ah, DD_c, DD_h):
    return (eta_ac * DD_c + eta_ah * DD_h) / (DD_c + DD_h)

if __name__ == '__main__':
    dirpath = os.path.dirname(__file__)
    input_csv_path = os.path.join(dirpath, 'index.csv')
    input_xlsx_dirpath = os.path.join(dirpath, 'input_xlsx')
    input_json_dirpath = os.path.join(dirpath, 'input_json')

    index_csvpath = os.path.join('sample_generator_kodate', 'index.csv')
    with open(index_csvpath, mode='r', encoding='utf-8', newline='') as index_csvfile:
        index_csvreader = csv.DictReader(index_csvfile)
        test_params = [_.values() for _ in index_csvreader]

    for index, model_plan, _, region_name, _, structure in test_params:
        create_new_house_data(index, region_name, model_plan, structure, input_xlsx_dirpath, input_json_dirpath)
