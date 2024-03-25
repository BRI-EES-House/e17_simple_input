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
    floor: str,
    place: str,
    region: str,
    insulation_level: str,
) -> None:
    """テンプレートから入力Excelを生成する関数

    Args:
        input_xlsx_filepath (str): 入力Excelのパス
        model_plan (str): 間取り(3LDK一般, 3LDKリビング横長, 3LDKタワー型)
        main_direction (str): 主開口方位(南, 東, 北, 西)
        floor (str): 階(最上階, 中間階, 最下階)
        place (str): 住戸位置(右側妻住戸, 中住戸, 左側妻住戸) ※3LDKタワー型の場合は'無'
        region (str): 地域区分(岡山, 岩見沢, 那覇)
        insulation_level (str): 断熱性能(H4, H11, H11超)
    """
    # 入力Excel のテンプレートファイルを読み込み
    template_xlsx = _get_template_xlsx(model_plan)

    # 入力シート内の各種変数名を変換する辞書を取得
    varname_mapper = _get_varname_mapper(main_direction, floor, place, region, insulation_level)

    # 入力シート内の各種変数名を変換
    with pd.ExcelWriter(input_xlsx_filepath) as writer:
        for (sheet_name, df) in template_xlsx.items():
            df.replace(varname_mapper).to_excel(writer, sheet_name=sheet_name, index=False)
            

@functools.lru_cache
def _get_template_xlsx(
    model_plan: str,
) -> dict[str, pd.DataFrame]:
    template_xlsx_path = {
        '3LDK一般':         'template_3LDK一般.xlsx',
        '3LDKリビング横長': 'template_3LDKリビング横長.xlsx',
        '3LDKタワー型':     'template_3LDKタワー型.xlsx'
    }[model_plan]
    
    if not os.path.isabs(template_xlsx_path):
        template_xlsx_path = os.path.join(os.path.dirname(__file__), template_xlsx_path)

    return pd.read_excel(template_xlsx_path, sheet_name=None)


def _get_varname_mapper(
    main_direction: str,
    floor: str,
    place: str,
    region: str,
    insulation_level: str
) -> dict:
    direction_mapper  = _get_direction_mapper(main_direction)
    floor_mapper      = _get_floor_mapper(region, floor)
    place_mapper      = _get_place_mapper(region, place)
    insulation_mapper = _get_insulation_mapper(region, insulation_level)
    
    return direction_mapper | floor_mapper | place_mapper | insulation_mapper


def _get_direction_mapper(main_direction: str) -> dict:
    varnames = ('#D_0', '#D_90', '#D_180', '#D_270')
    
    to_values = {
        '南': ('s', 'e', 'n', 'w'),
        '東': ('e', 'n', 'w', 's'),
        '北': ('n', 'w', 's', 'e'),
        '西': ('w', 's', 'e', 'n'),
    }[main_direction]
    
    return dict(zip(varnames, to_values))
    
    
def _get_floor_mapper(region: str, floor: str) -> dict:
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


def _get_place_mapper(region: str, place: str) -> dict:
    # 3LDKタワー型の場合、変数名の置き換えはしない
    if place == '無':
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


def _get_insulation_mapper(region: str, insulation_level: str) -> dict:
    varnames = ('#R_ceiling', '#R_wall', '#R_floor', '#C_ceiling', '#C_wall', '#C_floor', '#U_window', '#eta_window', '#U_door')

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


if __name__ == '__main__':
    import os
    import csv

    dirpath = os.path.dirname(__file__)
    input_xlsx_dirpath = os.path.join(dirpath, 'input_xlsx')
    if not os.path.exists(input_xlsx_dirpath):
        print(f"Make a directory: {input_xlsx_dirpath}")
        os.makedirs(input_xlsx_dirpath)

    with open('index.csv', mode='r', encoding='utf-8', newline='') as index_file:
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
                floor=row['階'],
                place=row['住戸位置'],
                region=row['地域'],
                insulation_level=row['断熱性能']
            )
