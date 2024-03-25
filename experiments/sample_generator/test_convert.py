import os
import csv
import logging
from common.web_input import WebInput, create_web_input_from_house_data
from common.house_data import HouseData
from common.converter import HouseDataConverter
from common.utils.func import load_json, dump_json

import numpy as np
np.seterr(all='raise')


def get_conditions():
    index_csvpath = os.path.join(os.path.dirname(__file__), 'index.csv')
    with open(index_csvpath, mode='r', encoding='utf-8', newline='') as index_csvfile:
        index_csvreader = csv.DictReader(index_csvfile)
        return [(_['index'], _['地域']) for _ in index_csvreader]


def test_converter(
    test_index: str,
    region_name: str,
) -> None:
    """コンバータを実行する

    Args:
        test_index (str): 管理用インデックス番号
        region_name (str): 地域名 := {'岩見沢' | '岡山' | '那覇'}
    """

    # ディレクトリの準備
    base_dirpath = os.path.join(os.path.dirname(__file__), 'input_json')
    testcase_dirpath = os.path.join(base_dirpath, test_index)

    # ログ出力先の設定
    log_filepath = os.path.join(testcase_dirpath, 'test_converter.log')
    logging.basicConfig(filename=log_filepath, level=logging.INFO, filemode='w', force=True,
                        format='[{levelname:.4}] {message}', style='{')

    # 地域名から地域区分の番号へ変換
    region = {
        '岩見沢': 2,
        '岡山': 6,
        '那覇': 8,
    }[region_name]

    # 参照住戸のファイルを読み込み
    ref_house_filename = f'3LDK一般_南_最上階_左側妻住戸_{region_name}_H11.json'
    ref_house_filepath = os.path.join(os.path.dirname(__file__), 'ref_house', ref_house_filename)
    ref_house_data = load_json(ref_house_filepath, data_class=HouseData)

    # 計算対象住戸のファイルを読み込み
    house_data_path = os.path.join(testcase_dirpath, 'house_data.json')
    house_data = load_json(house_data_path, data_class=HouseData)

    # 計算対象住戸の簡易入力条件を取得 <情報を絞り込む>
    web_input = create_web_input_from_house_data(region, house_data)

    # 簡易入力条件に従って負荷計算条件を推定 <情報の復元を試みる>
    house_data_cvt = HouseDataConverter(ref_house_data).convert(web_input)

    # 簡易入力条件を保存
    web_input_expected_path = os.path.join(testcase_dirpath, 'web_input_expected.json')
    dump_json(web_input_expected_path, web_input)

    # 変換後のファイルを保存
    house_data_cvt_expected_path = os.path.join(testcase_dirpath, 'house_data_cvt_expected.json')
    dump_json(house_data_cvt_expected_path, house_data_cvt)


# =============================================================================

if __name__ == '__main__':
    for index, region in get_conditions():
        print(index)
        test_converter(index, region)
