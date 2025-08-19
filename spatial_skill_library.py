# spatial_skill_library.py
"""
空間的な関係性を評価するための関数ライブラリ
"""
from typing import List, Tuple
import numpy as np
from layout import Layout

# --- Helper Functions ---

def calculate_vector(p1: Tuple[float, float, float], p2: Tuple[float, float, float]) -> np.ndarray:
    """2点間のベクトルを計算する。"""
    return np.array(p2) - np.array(p1)

def normalize_vector(v: np.ndarray) -> np.ndarray:
    """ベクトルを正規化する。"""
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else np.zeros_like(v)

def euler_to_forward_vector(orientation: Tuple[float, float, float]) -> np.ndarray:
    """オイラー角を前方ベクトルに変換する。"""
    pitch, yaw, _ = orientation
    x = np.cos(yaw) * np.cos(pitch)
    y = np.sin(yaw) * np.cos(pitch)
    z = np.sin(pitch)
    return np.array([x, y, z])

# --- Scoring Functions ---

def proximity_score(obj1: Layout, obj2: Layout, min_dist: float = 1.0, max_dist: float = 5.0) -> float:
    """2オブジェクトの近接度を評価する。"""
    distance = np.linalg.norm(np.array(obj1.location) - np.array(obj2.location))
    if distance <= min_dist:
        return 1.0
    if distance >= max_dist:
        return 0.0
    return 1 - (distance - min_dist) / (max_dist - min_dist)

def alignment_score(assets: List[Layout], axis: str) -> float:
    """複数アセットの整列度を評価する。"""
    axis_map = {'x': 0, 'y': 1, 'z': 2}
    if not assets or axis not in axis_map:
        return 0.0
    
    coords = [asset.location[axis_map[axis]] for asset in assets]
    variance = np.var(coords)
    return 1 / (1 + variance)

def parallelism_score(assets: List[Layout]) -> float:
    """
    複数アセットの平行度を、位置と向きの両方から評価する。
    論文のFigure 4で示唆された改良を反映。
    """
    if len(assets) < 2:
        return 1.0

    # 1. 位置の平行性評価
    pos_vectors = [calculate_vector(assets[i].location, assets[i+1].location) for i in range(len(assets)-1)]
    if not pos_vectors:
        position_score = 1.0
    else:
        norm_pos_vectors = [normalize_vector(v) for v in pos_vectors]
        dot_products_pos = [np.dot(norm_pos_vectors[i], norm_pos_vectors[i+1]) for i in range(len(norm_pos_vectors)-1)]
        position_score = np.mean([(dot + 1) / 2 for dot in dot_products_pos]) if dot_products_pos else 1.0

    # 2. 向きの類似性評価
    orientations = [euler_to_forward_vector(asset.orientation) for asset in assets]
    norm_orientations = [normalize_vector(o) for o in orientations]
    dot_products_orient = [np.dot(norm_orientations[i], norm_orientations[i+1]) for i in range(len(norm_orientations)-1)]
    orientation_score = np.mean([(dot + 1) / 2 for dot in dot_products_orient]) if dot_products_orient else 1.0

    # 統合スコア
    return (position_score + orientation_score) / 2

def perpendicularity_score(obj1: Layout, obj2: Layout) -> float:
    """2オブジェクトの垂直度を評価する。"""
    vec1 = euler_to_forward_vector(obj1.orientation)
    vec2 = euler_to_forward_vector(obj2.orientation)
    cos_angle = np.dot(normalize_vector(vec1), normalize_vector(vec2))
    return 1 - np.abs(cos_angle)