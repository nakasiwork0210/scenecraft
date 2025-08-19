def proximity_score(object1: Layout, object2: Layout, min_distance: float = 1.0, max_distance: float = 5.0) -> float:
    """
    2つのオブジェクトがどれだけ近いかを示す近接スコアを計算する。
    距離がmin_distance以下ならスコアは1.0、max_distance以上なら0.0となる。
    その間の距離では線形に補間される。
    """
    distance = np.linalg.norm(np.array(object1.location) - np.array(object2.location))
    if distance <= min_distance:
        return 1.0
    elif distance >= max_distance:
        return 0.0
    else:
        return 1 - (distance - min_distance) / (max_distance - min_distance)


def alignment_score(assets: List[Layout], axis: str) -> float:
    """
    指定された軸に沿ったアセットリストの整列スコアを計算する。
    座標の分散が小さいほど、整列度が高いと評価される。
    """
    axis_map = {'x': 0, 'y': 1, 'z': 2}
    if not assets or axis not in axis_map:
        return 0.0

    axis_index = axis_map[axis]
    coordinates = [asset.location[axis_index] for asset in assets]
    variance = np.var(coordinates)

    # 分散をスコアに変換（分散が0に近いほど1に近づく）
    score = 1 / (1 + variance)
    return score

def euler_to_forward_vector(orientation: Tuple[float, float, float]) -> np.ndarray:
    # オイラー角を前方ベクトルに変換するヘルパー関数 (ここでは簡略化)
    # 実際には回転行列を計算する必要がある
    pitch, yaw, roll = orientation
    x = np.cos(yaw) * np.cos(pitch)
    y = np.sin(yaw) * np.cos(pitch)
    z = np.sin(pitch)
    return np.array([x, y, z])

def perpendicularity_score(object1: Layout, object2: Layout) -> float:
    """
    2つのオブジェクトの前方ベクトルに基づいて、それらがどれだけ垂直であるかを評価する。
    """
    vec1 = euler_to_forward_vector(object1.orientation)
    vec2 = euler_to_forward_vector(object2.orientation)

    # 2つのベクトルの内積の絶対値が0に近いほど垂直
    cos_angle = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    score = 1 - np.abs(cos_angle)
    return score


