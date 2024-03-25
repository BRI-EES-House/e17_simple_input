計算対象住戸を生成するスクリプト群

1) condition_generator.py 計算対象住戸の条件を生成します。
2) input_excel_creator.py 1)で生成した条件を基に負荷計算条件用のExcelファイルを作成します。
3) 2)で生成したExcelファイルを基に負荷計算条件のJSONファイルを生成します。

コマンド実行例
```
$ python3 condition_generator.py > index.csv
$ python3 input_excel_creator.py
$ python3 input_json_creator.py
```
