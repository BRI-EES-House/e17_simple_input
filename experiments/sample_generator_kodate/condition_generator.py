# ----------------------------------------------------------------
#  計算対象住戸の条件を生成
# ----------------------------------------------------------------

import itertools


def get_house_conditions():
    """計算対象住戸の計算条件を生成する

    Yields:
        計算条件:
            間取り := {戸建2F | 戸建平屋 | 共同3LDK一般 }
            主開口方位 := {南 | 東 | 北 | 西}
            地域 := {岡山 | 岩見沢 | 那覇}
            断熱性能 := {H4 | H11 | H11超}
            断熱位置 := {床下断熱 | 基礎断熱 | 無} ※「無」は共同3LDK一般のみ
    """
    model_plans = ('戸建2F', '戸建平屋', '共同3LDK一般')
    main_directions = ('南', '東', '北', '西')
    regions = ('岡山', '岩見沢', '那覇')
    insulation_levels = ('H4', 'H11', 'H11超')
    structures = ('床断熱', '基礎断熱', '無')
    conditions = itertools.product(model_plans, main_directions, regions, insulation_levels, structures)

    for model_plan, main_direction, region, insulation_level, structure in conditions:
        # 戸建の場合は断熱位置も必要
        if model_plan in ['戸建2F', '戸建平屋'] and structure == '無':
            continue

        # 共同の場合は断熱位置は不要
        if model_plan == '共同3LDK一般' and structure != '無':
            continue

        yield model_plan, main_direction, region, insulation_level, structure


if __name__ == '__main__':
    import sys
    import csv

    # CSV出力準備
    index_writer = csv.writer(sys.stdout)
    index_writer.writerow(['index', '間取り', '主開口方位', '地域', '断熱性能', '断熱位置'])

    # 計算条件を出力
    for i, (model_plan, main_direction, region, insulation_level, structure) in enumerate(get_house_conditions()):
        index_writer.writerow([i, model_plan, main_direction, region, insulation_level, structure])
