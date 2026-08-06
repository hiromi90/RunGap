# RunGap ローカル開発プロジェクト

理想の走りと実際の走りの「差」を数値で見る、ランニングフォーム比較アプリの
バックエンド実装（ローカル開発版）です。現段階はローカルサーバー前提で、
姿勢推定は差し替え式パイプラインの Step 1（ダミーモデル）を用います。

## 構成
```
rungap_pipeline/   姿勢推定パイプライン（共通スケルトン＋アダプタ＋共通後段＋評価モード）
rungap_server/     FastAPI ローカル開発サーバー（体型・理想・解析・進捗・結果・評価）
requirements.txt   依存関係
```

## クイックスタート
```bash
pip install -r requirements.txt

# パイプライン単体の実演
python3 -m rungap_pipeline.run

# ローカルサーバー起動 → http://127.0.0.1:8000/docs（Swagger UI）
python3 -m rungap_server.run_local

# サーバーの自己検証（起動不要）
python3 -m rungap_server.selftest
```

## いまの位置づけ
- サーバー：ローカル（インメモリ保存、127.0.0.1）。運用時は研究室GPUサーバー＋永続DBへ。
- モデル：現状ダミー。`rungap_pipeline/estimators/` に軽量2D・メッシュ復元を差し込む。
- 中立性：出力に score/rank/grade を持たず、理想／実測／差／信頼度／局面別のみ。
