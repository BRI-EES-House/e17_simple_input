# ----------------------------------------------------------------
#  計算対象住戸の条件を生成
# ----------------------------------------------------------------

import itertools

def get_house_conditions():
    """計算対象住戸の計算条件を生成する

    Yields:
        計算条件:
            間取り := {3LDK一般 | 3LDKリビング横長 | 3LDKタワー型}
            主開口方位 := {南 | 東 | 北 | 西}
            階 := {最上階 | 中間階 | 最下階}
            住戸位置 := {右側妻住戸 | 中住戸 | 左側妻住戸 | 無} ※`無` は3LDKタワー型のみ
            地域 := {岡山 | 岩見沢 | 那覇}
            断熱性能 := {H4 | H11 | H11超}
    """
    model_plans       = ('3LDK一般', '3LDKリビング横長', '3LDKタワー型')
    main_directions   = ('南', '東', '北', '西')
    floors            = ('最上階', '中間階', '最下階')
    places            = ('右側妻住戸', '中住戸', '左側妻住戸', '無')
    regions           = ('岡山', '岩見沢', '那覇')
    insulation_levels = ('H4', 'H11', 'H11超')
    conds_gen = itertools.product(model_plans, main_directions, floors, places, regions, insulation_levels)

    for model_plan, main_direction, floor, place, region, insulation_level in conds_gen:
        # 3LDK一般、3LDKリビング横長の場合は住戸位置も必要
        if model_plan in ['3LDK一般', '3LDKリビング横長'] and place == '無':
            continue

        # 3LDKタワー型の場合、住戸位置は不要
        if model_plan == '3LDKタワー型' and place != '無':
            continue

        yield (model_plan, main_direction, floor, place, region, insulation_level)


if __name__ == '__main__':
    import sys
    import csv
    import itertools

    # CSV出力準備
    index_writer = csv.writer(sys.stdout)
    index_writer.writerow(['index', '間取り', '主開口方位', '階', '住戸位置', '地域', '断熱性能'])

    # 計算条件を出力
    for i, (model_plan, main_direction, floor, place, region, insulation_level) in enumerate(get_house_conditions()):
        index_writer.writerow([i, model_plan, main_direction, floor, place, region, insulation_level])
