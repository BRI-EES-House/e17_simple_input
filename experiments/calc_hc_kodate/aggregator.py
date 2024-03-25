import json
import pandas as pd


def aggregate(result_detail_path: str, result_summary_path: str):
    result_detail_df = pd.read_csv(result_detail_path)
    l_s_c_h_sum_MJ, l_s_c_c_sum_MJ = _calc_l_x_x_sum_MJ(result_detail_df, columns_suffix='l_s_c')
    l_s_r_h_sum_MJ, l_s_r_c_sum_MJ = _calc_l_x_x_sum_MJ(result_detail_df, columns_suffix='l_s_r')
    l_l_c_h_sum_MJ, l_l_c_c_sum_MJ = _calc_l_x_x_sum_MJ(result_detail_df, columns_suffix='l_l_c')

    with open(result_summary_path, mode='w', encoding='utf-8') as fp:
        json.dump({
            'l_s_c_h_sum_MJ': l_s_c_h_sum_MJ,
            'l_s_c_c_sum_MJ': l_s_c_c_sum_MJ,
            'l_s_r_h_sum_MJ': l_s_r_h_sum_MJ,
            'l_s_r_c_sum_MJ': l_s_r_c_sum_MJ,
            'l_l_c_h_sum_MJ': l_l_c_h_sum_MJ,
            'l_l_c_c_sum_MJ': l_l_c_c_sum_MJ,
        }, fp)


def _calc_l_x_x_sum_MJ(
    result_detail_df: pd.DataFrame,
    columns_suffix: str
) -> tuple[float, float]:
    columns: list[str] = result_detail_df.columns
    l_x_x_columns = [_ for _ in columns if _.endswith(columns_suffix)]
    l_x_x_df = result_detail_df[l_x_x_columns]

    l_x_x_h = l_x_x_df[l_x_x_df > 0.0].sum(axis=1)
    l_x_x_c = l_x_x_df[l_x_x_df < 0.0].sum(axis=1)

    min_per_step = 15
    sec_per_min = 60
    l_x_x_h_MJ = l_x_x_h * min_per_step * sec_per_min * 10**(-6)
    l_x_x_c_MJ = l_x_x_c * min_per_step * sec_per_min * 10**(-6)

    return l_x_x_h_MJ.sum(), l_x_x_c_MJ.sum()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('result_detail_path', type=str)
    parser.add_argument('result_summary_path', type=str)

    args = parser.parse_args()
    aggregate(args.result_detail_path, args.result_summary_path)
