計算対象住戸を生成するスクリプト群

1) condition_generator.py 計算対象住戸の条件を生成します。
2) input_excel_creator.py 1)で生成した条件を基に負荷計算条件用の入力Excel(コントロール群)を作成します。
3) 2)で生成した入力Excel(コントロール群)を基に負荷計算条件の入力JSON(コントロール群)を生成します。
4) 3)で生成した入力JSON(コントロール群)を基に対照群の入力Excel・入力JSONを生成します。

コマンド実行例
```
$ python3 -m sample_generator_kodate.condition_generator > sample_generator_kodate/index.csv
$ python3 -m sample_generator_kodate.input_excel_creator
$ python3 -m sample_generator_kodate.input_json_creator
$ python3 -m sample_generator_kodate.new_input_json_creator
```
