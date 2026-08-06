# RunGap ローカル開発サーバー（FastAPI）

データモデル・API 設計をローカル環境向けに実装したもの。姿勢推定は
`rungap_pipeline`（Step 1・現状ダミー）を HTTP の裏で実行する。
保存はインメモリ（プロセス内）で、再起動すると消える。運用時は研究室
GPU サーバー ＋ 永続DB（PostgreSQL 等）へ移行する。

## セットアップ
```bash
pip install -r requirements.txt
```

## ローカル起動
```bash
python3 -m rungap_server.run_local        # http://127.0.0.1:8000
# または
uvicorn rungap_server.app:app --reload
```
`http://127.0.0.1:8000/docs` で対話的なAPIドキュメント（Swagger UI）が開く。

## 動作確認（サーバー起動なし）
```bash
python3 -m rungap_server.selftest
```

## 主なエンドポイント
- `POST /api/v1/users/me/body-profiles` … 体型プロファイル作成（F1）
- `POST /api/v1/ideal-motions` … 理想モーション登録（F2）
- `POST /api/v1/analyses` … 解析を投入（F3・F4）→ 202 と job_id を返す
- `GET  /api/v1/jobs/{job_id}` … 進捗ポーリング
- `GET  /api/v1/analyses/{id}` … 結果（metric_comparisons）
- `POST /api/v1/analyses/{id}/evaluate` … 評価モード（Phase 0 の一致度）

数値はすべてダミー（合成モーション）で、配線とローカル動作の実証が目的。
中立性：出力に score/rank/grade を持たず、理想／実測／差／信頼度／局面別のみ。
