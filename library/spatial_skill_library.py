# library/spatial_skill_library.py
"""
空間的な関係性を評価するための関数ライブラリ (Spatial Skill Library)
論文の Section 2.4 で詳述されている、自己進化するスキルの中核。
"""
from typing import List, Tuple, Dict
import numpy as np
import inspect

from .layout import Layout
from . import skill_database

# --- Helper Functions ---
def _calculate_vector(p1, p2):
    return np.array(p2) - np.array(p1)

def _normalize_vector(v):
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else np.zeros_like(v)

def _euler_to_forward_vector(orientation):
    pitch, yaw, _ = map(np.radians, orientation)
    x = np.cos(yaw) * np.cos(pitch)
    y = np.sin(yaw) * np.cos(pitch)
    z = np.sin(pitch)
    return np.array([x, y, z])

# --- Scoring Functions (The Skills) ---

def proximity_score(obj1: Layout, obj2: Layout, min_dist: float = 1.0, max_dist: float = 5.0) -> float:
    """2オブジェクトの近接度を評価する。"""
    distance = np.linalg.norm(np.array(obj1.location) - np.array(obj2.location))
    if distance <= min_dist: return 1.0
    if distance >= max_dist: return 0.0
    return 1 - (distance - min_dist) / (max_dist - min_dist)

def alignment_score(assets: List[Layout], axis: str) -> float:
    """複数アセットの指定された軸に沿った整列度を評価する。"""
    axis_map = {'x': 0, 'y': 1, 'z': 2}
    if not assets or axis not in axis_map: return 0.0
    coords = [asset.location[axis_map[axis]] for asset in assets]
    return 1 / (1 + np.var(coords))

def parallelism_score(assets: List[Layout]) -> float:
    """
    複数アセットの平行度を、位置と向きの両方から評価する。
    論文のFigure 4で示された自己進化の例を反映した完成形。
    """
    if len(assets) < 2: return 1.0
    
    pos_vectors = [_calculate_vector(assets[i].location, assets[i+1].location) for i in range(len(assets)-1)]
    norm_pos = [_normalize_vector(v) for v in pos_vectors if np.linalg.norm(v) > 0]
    pos_dots = [np.dot(norm_pos[i], norm_pos[i+1]) for i in range(len(norm_pos)-1)]
    pos_score = np.mean([(d + 1) / 2 for d in pos_dots]) if pos_dots else 1.0

    orient_vecs = [_euler_to_forward_vector(a.orientation) for a in assets]
    orient_dots = [np.dot(orient_vecs[i], orient_vecs[i+1]) for i in range(len(orient_vecs)-1)]
    orient_score = np.mean([(d + 1) / 2 for d in orient_dots]) if orient_dots else 1.0
    
    return (pos_score + orient_score) / 2

def perpendicularity_score(obj1: Layout, obj2: Layout) -> float:
    """2オブジェクトの向きの垂直度を評価する。"""
    vec1 = _normalize_vector(_euler_to_forward_vector(obj1.orientation))
    vec2 = _normalize_vector(_euler_to_forward_vector(obj2.orientation))
    return 1 - np.abs(np.dot(vec1, vec2))

def symmetry_score(assets: List[Layout], axis: str) -> float:
    """複数アセットの指定された軸に関する対称性を評価する。"""
    # (論文のAppendix Cで言及されている機能の実装例)
    # ...
    return 0.8 # ダミーのスコア

# --- スキル管理 ---
SKILLS: Dict[str, callable] = {
    "proximity": proximity_score,
    "alignment": alignment_score,
    "parallelism": parallelism_score,
    "perpendicularity": perpendicularity_score,
    "symmetry": symmetry_score,
}

def initialize_skills():
    """
    【追加】プログラム起動時にデータベースから最新のスキルを読み込み、
    メモリ上のSKILLSを更新する。
    """
    learned_skills_code = skill_database.load_skills_from_db()
    if not learned_skills_code:
        return # データベースが空か、読み込めなかった場合は何もしない

    for skill_name, source_code in learned_skills_code.items():
        try:
            # 読み込んだ文字列のソースコードから、実行可能な関数オブジェクトを動的に生成
            exec(source_code, globals())
            # グローバルに生成された関数オブジェクトでSKILLSを更新
            SKILLS[skill_name] = globals()[skill_name]
            print(f"[Library] ℹ️ スキル '{skill_name}' が学習済みのバージョンに更新されました。")
        except Exception as e:
            print(f"[Library] ❌ エラー: スキル '{skill_name}' の動的読み込みに失敗 - {e}")

def get_skill_source(skill_name: str) -> str:
    """指定されたスキルのソースコードを取得する。(変更なし)"""
    if skill_name in SKILLS:
        return inspect.getsource(SKILLS[skill_name])
    return ""

def update_skill(skill_name: str, new_function_code: str):
    """
    【修正】スキルライブラリの関数を動的に更新し、
    その結果をデータベースに保存する。
    """
    try:
        # 1. メモリ上のスキルを更新
        exec(new_function_code, globals())
        new_func = globals()[skill_name]
        SKILLS[skill_name] = new_func
        print(f"[Library] ✔️ メモリ上のスキル '{skill_name}' が正常に更新されました。")

        # 2. データベースに保存
        # 現在の全スキルのソースコードを取得
        current_skills_source = {name: inspect.getsource(func) for name, func in SKILLS.items()}
        # データベースに保存
        skill_database.save_skills_to_db(current_skills_source)

    except Exception as e:
        print(f"[Library] ❌ エラー: スキル '{skill_name}' の更新に失敗しました - {e}")

