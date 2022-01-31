# Ishiki-dash
Jリーグの新人選手の出場記録をインタラクティブに可視化するダッシュボード、J.LEAGUE Rookie Stats Viewerの開発用レポジトリです。

## 環境構築
Python3.7以上の環境で以下を実行してください。
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ダッシュボード起動
http://0.0.0.0:8050/ にダッシュボードを起動します。
```
python app.py
```

## データ更新
前処理済みのファイルが./data以下に保存されています。データを更新したい時のみ以下を実行してください。

### ダウンロード
新たな年度のデータを取得したい時などに以下を実行します。
```
python -m mydash.scripts.fetch_rookie --out ./data/rookie_raw.csv
python -m mydash.scripts.fetch_stat --out ./data/rookie_raw.csv
```

## データ修正
以下のファイルを使って手動でデータを更新できます。
* stats_drop.csv
    * 新人選手と同姓同名のプレーヤーがいたときに、そのレコードを無視するようにします。
    * この方法では、同姓同名の新人選手が複数いたときはカバーできないことに注意してください。

### 前処理
データ修正用ファイルを更新したときや正規化処理を更新した時などに以下を実行します。
```
python -m mydash.scripts.process_rookie --out ./data/rookie.csv
python -m mydash.scripts.process_stats --out ./data/stats.csv
```