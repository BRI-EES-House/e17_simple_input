import os
import functools
import pandas as pd

# ----------------------------------------------------------------
#  計算対象住戸の生成
# 
#  * input_xlsx/{index}.xlsx ファイルの生成 (個別の条件をExcelファイルで生成)
# ----------------------------------------------------------------

def create_input_xlsx(
    input_xlsx_filepath: str,
    model_plan: str,
    main_direction: str,
    region: str,
    insulation_level: str,
    structure: str,
) -> None:
    """テンプレートから入力Excelを生成する関数

    Args:
        input_xlsx_filepath (str): 入力Excelのパス
        model_plan (str): 間取り(戸建2F, 戸建平屋, 共同3LDK一般)
        main_direction (str): 主開口方位(南, 東, 北, 西)
        region (str): 地域区分(岡山, 岩見沢, 那覇)
        insulation_level (str): 断熱性能(H4, H11, H11超)
        structure (str): 断熱位置(床下断熱 | 基礎断熱 | 無)  ※「無」は共同3LDK一般のみ
    """
    # 入力Excel のテンプレートファイルを読み込み
    template_xlsx = _get_template_xlsx(model_plan, structure)

    # 入力シート内の各種変数名を変換する辞書を取得
    varname_mapper = _get_varname_mapper(model_plan, main_direction, region, insulation_level)

    #TODO: 基礎断熱への対応

    # 入力シート内の各種変数名を変換
    with pd.ExcelWriter(input_xlsx_filepath) as writer:
        for (sheet_name, df) in template_xlsx.items():
            df.replace(varname_mapper).to_excel(writer, sheet_name=sheet_name, index=False)
            

@functools.lru_cache
def _get_template_xlsx(
    model_plan: str,
    structure: str,
) -> dict[str, pd.DataFrame]:
    template_xlsx_path = {
        ('戸建2F',       '床断熱'): 'template_戸建2F_20231106.xlsx',
        ('戸建平屋',     '床断熱'): 'template_戸建平屋_20231106.xlsx',
        ('戸建2F',       '基礎断熱'): 'template_戸建2F_基礎断熱_20231106.xlsx',
        ('戸建平屋',     '基礎断熱'): 'template_戸建平屋_基礎断熱_20231106.xlsx',
        ('共同3LDK一般', '無'):       'template_3LDK一般.xlsx',
    }[(model_plan, structure)]

    if not os.path.isabs(template_xlsx_path):
        template_xlsx_path = os.path.join(os.path.dirname(__file__), template_xlsx_path)

    return pd.read_excel(template_xlsx_path, sheet_name=None)


def _get_varname_mapper(
    model_plan: str,
    main_direction: str,
    region: str,
    insulation_level: str
) -> dict:
    direction_mapper = _get_direction_mapper(main_direction)
    insulation_mapper = _get_insulation_mapper(model_plan, region, insulation_level)

    # 共同住宅では階・住戸位置に応じてtemplateの変数名を置き換える必要がある。
    # sample_generator_kodate は戸建の検証がメインとなるため、共同では最上階・右側妻住戸のみを生成対象とした。
    floor_mapper = _get_floor_mapper(model_plan, region, floor='最上階')
    place_mapper = _get_place_mapper(model_plan, region, place='右側妻住戸')

    return direction_mapper | insulation_mapper | floor_mapper | place_mapper


def _get_direction_mapper(main_direction: str) -> dict:
    varnames = ('#D_0', '#D_90', '#D_180', '#D_270')
    
    to_values = {
        '南': ('s', 'e', 'n', 'w'),
        '東': ('e', 'n', 'w', 's'),
        '北': ('n', 'w', 's', 'e'),
        '西': ('w', 's', 'e', 'n'),
    }[main_direction]
    
    return dict(zip(varnames, to_values))


def _get_insulation_mapper(model_plan, region: str, insulation_level: str) -> dict:
    varnames = ('#R_ceiling', '#R_wall', '#R_floor', '#C_ceiling', '#C_wall', '#C_floor', '#U_window', '#eta_window', '#U_door')

    # 現行負荷データの計算条件に準拠
    # NOTE: 断熱材厚みに応じて熱容量を設定したところ、heat_load_calcで応答係数を求める際にエラーが発生することが分かった。
    # 断熱材の熱容量はコンクリと比較して値が小さいことを加味して、検証の際は断熱材の熱容量を0.00として計算することとした。
    if model_plan in ['戸建2F', '戸建平屋']:
        to_values = {
            ('岡山',   'H4'):    (1.12, 0.72, 0.36, 0.00, 0.00, 0.00, 6.51, 0.70, 6.51),
            ('岡山',   'H11'):   (3.42, 1.42, 1.44, 0.00, 0.00, 0.00, 4.65, 0.63, 4.65),
            ('岡山',   'H11超'): (5.48, 2.32, 2.30, 0.00, 0.00, 0.00, 2.91, 0.32, 2.91),
            ('岩見沢', 'H4'):    (4.14, 1.78, 1.96, 0.00, 0.00, 0.00, 2.33, 0.46, 2.33),
            ('岩見沢', 'H11'):   (5.66, 2.40, 2.76, 0.00, 0.00, 0.00, 2.33, 0.46, 2.33),
            ('岩見沢', 'H11超'): (5.36, 3.20, 3.30, 0.00, 0.00, 0.00, 1.90, 0.42, 1.90),
            ('那覇',   'H4'):    (0.02, 0.04, 0.00, 0.00, 0.00, 0.00, 6.51, 0.70, 6.51),
            ('那覇',   'H11'):   (6.64, 3.04, 0.00, 0.00, 0.00, 0.00, 6.51, 0.70, 6.51),
            ('那覇',   'H11超'): (6.64, 3.04, 0.00, 0.00, 0.00, 0.00, 6.51, 0.15, 6.51),
        }[(region, insulation_level)]

    # 既存研究の計算条件に準拠
    # https://www.kenken.go.jp/japanese/contents/publications/data/154/5.pdf#page=4
    elif model_plan == '共同3LDK一般':
        to_values = {
            ('岡山',   'H4'):    (1.10, 0.70, 0.50, 1.25, 0.79, 0.57, 6.51, 0.70, 4.65),
            ('岡山',   'H11'):   (2.50, 1.10, 1.50, 2.83, 1.25, 1.70, 4.65, 0.63, 4.65),
            ('岡山',   'H11超'): (2.70, 1.80, 1.80, 3.05, 2.04, 2.04, 2.33, 0.51, 2.33),
            ('岩見沢', 'H4'):    (2.90, 1.70, 2.10, 3.28, 1.92, 2.37, 2.33, 0.51, 2.33),
            ('岩見沢', 'H11'):   (3.60, 2.30, 2.20, 4.07, 2.60, 2.49, 2.33, 0.51, 2.33),
            ('岩見沢', 'H11超'): (6.25, 4.47, 2.86, 7.06, 5.04, 3.23, 1.60, 0.47, 1.60),
            ('那覇',   'H4'):    (1.10, 0.00, 0.00, 1.25, 0.00, 0.00, 6.51, 0.70, 4.65),
            ('那覇',   'H11'):   (2.50, 0.30, 0.00, 2.83, 0.34, 0.00, 6.51, 0.70, 4.65),
            ('那覇',   'H11超'): (2.50, 0.30, 0.00, 2.83, 0.34, 0.00, 6.51, 0.30, 4.65),
        }[(region, insulation_level)]

    return dict(zip(varnames, to_values))


# 共同住宅における階(最上階, 中間階, 最下階)の違いに応じて変数名を置き換える関数
def _get_floor_mapper(model_plan: str, region: str, floor: str) -> dict:
    # 戸建の場合は変数名の置き換え不要
    if model_plan != '共同3LDK一般':
        return {}

    if region in ['岡山', '那覇']:
        H_parting = 0.15
    elif region == '岩見沢':
        H_parting = 0.05
    else:
        raise ValueError(region)

    varnames = ('#H_ceiling', '#LayersType_ceiling', '#H_floor', '#LayersType_floor')

    to_values = {
        '最上階': (1.00,      'ceiling',         H_parting, 'parting_floor'),
        '中間階': (H_parting, 'parting_ceiling', H_parting, 'parting_floor'),
        '最下階': (H_parting, 'parting_ceiling', 0.70,      'floor'),
    }[floor]

    return dict(zip(varnames, to_values))


# 共同住宅における住戸位置(右側妻住戸, 中住戸, 左側妻住戸)の違いに応じて変数名を置き換える関数
def _get_place_mapper(model_plan: str, region: str, place: str) -> dict:
    # 戸建の場合は変数名の置き換え不要
    if model_plan != '共同3LDK一般':
        return {}

    if region in ['岡山', '那覇']:
        H_parting = 0.15
    elif region == '岩見沢':
        H_parting = 0.05
    else:
        raise ValueError(region)

    varnames = ('#H_90', '#LayersType_90', '#H_270', '#LayersType_270')

    to_values = {
        '右側妻住戸': (1.00,      'wall',         H_parting, 'parting_wall'),
        '中住戸':     (H_parting, 'parting_wall', H_parting, 'parting_wall'),
        '左側妻住戸': (H_parting, 'parting_wall', 1.00,       'wall'),        
    }[place]

    return dict(zip(varnames, to_values))


if __name__ == '__main__':
    import csv
    import shutil

    dirpath = os.path.dirname(__file__)
    input_csv_path = os.path.join(dirpath, 'index.csv')
    input_xlsx_dirpath = os.path.join(dirpath, 'input_xlsx')

    # input_xlsxディレクトリが残っている場合は削除する(古い入力Excelの混在を防ぐため)
    if os.path.exists(input_xlsx_dirpath):
        print(f'Remove an old directory: {input_xlsx_dirpath}')
        shutil.rmtree(input_xlsx_dirpath)

    # input_xlsxディレクトリを再度作成(生成した入力Excelをこのディレクトリに入れていく)
    print(f"Make a new directory: {input_xlsx_dirpath}")
    os.makedirs(input_xlsx_dirpath)

    with open(input_csv_path, mode='r', encoding='utf-8', newline='') as index_file:
        csvreader = csv.DictReader(index_file)
        for row in csvreader:
            # 入力Excel を生成
            input_xlsx_filename = f"{row['index']}.xlsx"
            input_xlsx_filepath = os.path.join(input_xlsx_dirpath, input_xlsx_filename)
            print(f"{input_xlsx_filepath}")
            create_input_xlsx(
                input_xlsx_filepath=input_xlsx_filepath,
                model_plan=row['間取り'],
                main_direction=row['主開口方位'],
                region=row['地域'],
                insulation_level=row['断熱性能'],
                structure=row['断熱位置'],
            )
