# RunGap 姿勢推定パイプライン（Step 1 雛形）

設計書「姿勢推定パイプライン・モデルアダプタ設計」の **Step 1** を実装した動く土台です。
共通スケルトン ＋ `PoseEstimator` インターフェース ＋ ダミーアダプタで、
パイプラインを端から端まで通し、1本の入力から結果が出るところまでを確認できます。

## 実行方法
必要: Python 3.10+ / numpy

```bash
cd <このフォルダの親ディレクトリ>
python3 -m rungap_pipeline.run
```

`metric_comparisons`（理想／実測／差／信頼度／局面別）のJSONと、
評価モード（参照値との一致度：Phase 0）のテーブルが表示されます。
数値はすべてダミー（合成モーション）で、配線の実証が目的です。

## 構成
```
skeleton/     共通スケルトン（正規化スキーマ）
estimators/   PoseEstimator 抽象 ＋ レジストリ ＋ ダミーアダプタ
calibration/  cm較正（体型寸法→スケール）
gait/         歩行周期検出（接地区間）・局面
metrics/      6指標の算出（モデル非依存）
confidence/   信頼度の一次付与
schema.py     出力スキーマ（score/rank/grade を持たない＝中立）
evaluation/   評価モード（Phase 0 の一致度検証）
pipeline/     段階のオーケストレーション
run.py        端から端まで通す実演
```

## 次のステップ
- `estimators/` に軽量2Dアダプタ（RTMPose/MMPose→3Dリフト）とメッシュ復元アダプタ（SMPL系）を実装。
- `metrics/compute.py` の簡易算出式を、局面別・左右を含む正式定義へ精緻化。
- `evaluation/` に mocopi・ウォッチの実データ取り込みと時刻同期を実装。
- 信頼度を評価モードの結果で指標×条件ごとに較正（設計書9章）。

> 下流（正規化・検出・較正・指標・3D）はモデル非依存のため、
> 最終的にどのモデルを選んでも再利用でき、無駄になりません。
