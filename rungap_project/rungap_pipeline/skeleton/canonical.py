"""共通スケルトン（正規化スキーマ）。全モデルの出力をこの並び・定義へ写像する。
座標系は側方カメラ基準：x=進行方向, y=鉛直, z=奥行き。単位はメートル。"""

JOINT_NAMES = [
    "head", "neck", "chest", "pelvis",
    "l_shoulder", "l_elbow", "l_wrist",
    "r_shoulder", "r_elbow", "r_wrist",
    "l_hip", "l_knee", "l_ankle", "l_toe", "l_heel",
    "r_hip", "r_knee", "r_ankle", "r_toe", "r_heel",
]
NAME_TO_IDX = {n: i for i, n in enumerate(JOINT_NAMES)}
NUM_JOINTS = len(JOINT_NAMES)


def idx(name: str) -> int:
    return NAME_TO_IDX[name]
