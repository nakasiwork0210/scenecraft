from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class Layout:
    """
    3Dシーン内の単一アセットのレイアウト情報を保持するデータクラス。
    """
    # アセットの3D空間における中心位置 (x, y, z)
    location: Tuple[float, float, float]
    
    # アセットのバウンディングボックスの最小座標 (min_x, min_y, min_z)
    min: Tuple[float, float, float]
    
    # アセットのバウンディングボックスの最大座標 (max_x, max_y, max_z)
    max: Tuple[float, float, float]
    
    # アセットの向きをオイラー角で表現 (pitch, yaw, roll)
    orientation: Tuple[float, float, float]