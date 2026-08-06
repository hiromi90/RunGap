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
python3 -m rungap_server.run_local
```
ブラウザで **http://127.0.0.1:8000/** を開く（理想を選び「解析を実行」→進捗→結果→評価モード）。
API ドキュメントは http://127.0.0.1:8000/docs 。

その他：
```bash
python3 -m rungap_pipeline.run       # パイプライン単体の実演
python3 -m rungap_server.selftest    # サーバーの自己検証（起動不要）
```

## よくあるつまずき
- **404 / 405 や「Unexpected token '<'」が出る**：画面を別のサーバー（例：VS Code の
  Live Server = ポート 5500）から開いていると、API 呼び出しが :5500 に向かい失敗します。
  → **必ず http://127.0.0.1:8000/ を開いてください**（FastAPI サーバー自身が画面を配信します）。
  なお画面側は、:8000 以外から開かれた場合は自動で http://127.0.0.1:8000 のAPIを呼ぶように
  してありますが、その場合も `python3 -m rungap_server.run_local` でサーバーの起動が必要です。

## いまの位置づけ
- サーバー：ローカル（インメモリ保存、127.0.0.1）。運用時は研究室GPUサーバー＋永続DBへ。
- モデル：現状ダミー。`rungap_pipeline/estimators/` に軽量2D・メッシュ復元を差し込む。
- 中立性：出力に score/rank/grade を持たず、理想／実測／差／信頼度／局面別のみ。
