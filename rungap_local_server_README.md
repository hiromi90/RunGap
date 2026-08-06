# RunGap ローカル開発プロジェクト

理想の走りと実際の走りの「差」を数値で見る、ランニングフォーム比較アプリの
ローカル開発版です。ローカルサーバーが Web 画面と API を配信し、差し替え式
パイプラインの Step 1（現状ダミーモデル）で解析します。

## 構成
```
rungap_pipeline/     姿勢推定パイプライン（共通スケルトン＋アダプタ＋共通後段＋評価モード）
rungap_server/       FastAPI ローカルサーバー（API ＋ web/ の画面配信）
rungap_server/web/   ブラウザ画面（実APIで解析→進捗→結果→評価）
requirements.txt     依存関係
```

## クイックスタート
```bash
pip install -r requirements.txt

# ローカルサーバー起動
python3 -m rungap_server.run_local
```
ブラウザで次を開く：
- 画面：http://127.0.0.1:8000/  （理想を選び「解析を実行」→ 進捗→結果→評価モード）
- API ドキュメント：http://127.0.0.1:8000/docs

その他：
```bash
python3 -m rungap_pipeline.run       # パイプライン単体の実演
python3 -m rungap_server.selftest    # サーバーの自己検証（起動不要）
```

## いまの位置づけ
- サーバー：ローカル（インメモリ保存、127.0.0.1）。運用時は研究室GPUサーバー＋永続DBへ。
- モデル：現状ダミー。`rungap_pipeline/estimators/` に軽量2D・メッシュ復元を差し込む。
- 中立性：出力に score/rank/grade を持たず、理想／実測／差／信頼度／局面別のみ。
