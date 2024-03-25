# 負荷計算まで一貫で試算

## 方針

* Google Cloud Batch を使って並列計算を行う。
* 計算条件は index.csv で与えるものとする。
* 計算に必要なコードはDockerイメージにまとめる。
* 計算結果はGoogle Cloud Storageに保存する。

## ファイル構成

* calc_hc_job.json ... バッチ実行時の構成情報
* Dockerfile ... Dockerイメージの作成
* requirements.txt ... Python依存モジュールのインストール用
* task.sh ... Cloud Batchで実行されるシェルスクリプト
* aggregator.py ... 負荷計算結果が大きいので興味があるところだけに集約するスクリプト

## 計算条件のファイル(index.csv, 入力JSON)をGCSにアップロード

`sample_generator_kodate`で作成した計算条件のファイル(index.csv, 入力JSON)を、GCS(Google Cloud Storage)にアップロードします。
GCSへのアップロードにあたり、GCS内にある古い各種ファイルを削除しておきます。

```
gcloud config set project <your-project>
gsutil -m rm gs://<your-gcs-bucket>/**
gsutil cp ../../sample_generator_kodate/index.csv gs://<your-gcs-bucket>
gsutil -m cp ../../sample_generator_kodate/input_json/*.json gs://<your-gcs-bucket>
```

## Dockerイメージ作成

head_load_calc をローカルに取得してから、Dockerビルドします。

```
git clone --depth 1 git@github.com:BRI-EES-House/heat_load_calc.git
docker build -t <your-container-image-name> .
docker push <your-container-image-name>
```

## バッチの実行

以下のコマンドによりバッチ処理を実行します。
(e17xxxxxxx の所は何でも良いが、`gcloud batch jobs list` で重複無きことを確認する。)

```
gcloud batch jobs submit projects/<your-project>/locations/<location>/jobs/<job-name> --config=calc_hc_job.json
```


バッチ処理の実行後、各種計算結果を格納したJSONファイル(`result_summary_{num}.json`)がGCSの同バケットにアップロードされます。
