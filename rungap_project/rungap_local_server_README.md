# RunGap ローカル開発プロジェクト

理想の走りと実際の走りの「差」を数値で見る、ランニングフォーム比較アプリの
ローカル開発版です。ローカルサーバーが Web 画面と API を配信し、差し替え式
パイプラインで解析します。姿勢推定は「ダミー」と「実モデル（MediaPipe）」を
切り替えられます。

## 構成
```
rungap_pipeline/     姿勢推定パイプライン（共通スケルトン＋アダプタ＋共通後段＋評価モード）
rungap_server/       FastAPI ローカルサーバー（API ＋ web/ の画面配信）
requirements.txt         base 依存（サーバー・パイプライン）
requirements-models.txt  実モデル（MediaPipe）用の追加依存
```

## クイックスタート（ダミーで動かす）
```bash
pip install -r requirements.txt
python3 -m rungap_server.run_local
```
ブラウザで **http://127.0.0.1:8000/** を開く。API ドキュメントは /docs 。

## 実モデル（MediaPipe）で解析する
現行の mediapipe は Tasks API 方式で、姿勢モデルファイルが必要です。
```bash
# 1) 追加依存
pip install -r requirements-models.txt

# 2) 姿勢モデルを一度ダウンロードして pose_landmarker.task として置く
#    （または環境変数 RUNGAP_POSE_MODEL にパスを設定）
#    https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task

# 3) 側方撮影の動画で実行
python3 -m rungap_pipeline.run_video side_view.mp4 --model mediapipe --inseam 80
```
補足：膝関節角度・体幹前傾・腕振り・接地タイミング・ピッチは妥当な値が出ます。
ただし **ストライド長** と **軸の対応** は撮影セットアップに依存するため、実映像での
確認・較正が前提です（＝評価モード／Phase 0 の役割）。RTMPose 等はさらに別の
アダプタとして `rungap_pipeline/estimators/` に追加できます。

## よくあるつまずき（画面の404/405）
画面は必ず **http://127.0.0.1:8000/** を開いてください。VS Code の Live Server（:5500）
から開くと API 呼び出しが :5500 に向かい失敗します（画面側で :8000 を自動で呼ぶよう
にはしてありますが、その場合も FastAPI サーバーの起動が必要）。

## いまの位置づけ
- サーバー：ローカル（インメモリ保存）。運用時は研究室GPUサーバー＋永続DBへ。
- モデル：ダミー＋実モデル（MediaPipe）。RTMPose・メッシュ復元はアダプタ追加で対応。
- 中立性：出力に score/rank/grade を持たず、理想／実測／差／信頼度／局面別のみ。
