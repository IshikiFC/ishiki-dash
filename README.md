
## 環境構築
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## データ取得
```
python -m mydash.scripts.fetch_stats
python -m mydash.scripts.fetch_rookie
python -m mydash.scripts.process_stats
```

## ダッシュボード起動
```
python app.py
```