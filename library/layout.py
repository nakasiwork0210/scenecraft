"""
3Dシーン内のアセットのレイアウト情報を定義するモジュール
"""
from dataclasses import dataclass
from typing import Tuple
from copy import deepcopy

@dataclass
class Layout:
    """
    3Dシーン内の単一アセットのレイアウト情報を保持するデータクラス。
    論文の Section 2.2 で言及されているレイアウト行列 L(a_i) に相当します。
    """
    location: Tuple[float, float, float]  # 位置 (x, y, z)
    orientation: Tuple[float, float, float] # 向き (pitch, yaw, roll)
    scale: Tuple[float, float, float]     # スケール (sx, sy, sz)
    
    def copy(self):
        return deepcopy(self)