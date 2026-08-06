"""RunGap ローカル開発サーバー（FastAPI）。

データモデル・API 設計をローカル環境向けに実装したもの。
姿勢推定は rungap_pipeline（Step 1・現状ダミー）を HTTP の裏で実行する。
保存はインメモリ（プロセス内）で、ローカル開発用。運用時は研究室GPU
サーバー＋永続DB（PostgreSQL 等）へ移行する。
"""
__version__ = "0.1.0-local"
