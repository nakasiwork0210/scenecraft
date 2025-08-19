def parallelism_score(assets: List[Layout]) -> float:
    #... (引数と返り値の説明)
    if len(assets) < 2:
        return 1.0

    # --- 位置の平行性評価 (従来の部分) ---
    vectors = [calculate_vector(assets[i].location, assets[i+1].location) for i in range(len(assets)-1)]
    normalized_vectors = [normalize_vector(v) for v in vectors]
    dot_products_position = [np.dot(normalized_vectors[i], normalized_vectors[i+1]) for i in range(len(normalized_vectors)-1)]
    position_score = np.mean([(dot+1)/2 for dot in dot_products_position])

    # --- 向きの類似性評価 (新たに追加された部分) ---
    orientation_similarities = [orientation_similarity(assets[i].orientation, assets[i+1].orientation) for i in range(len(assets)-1)]
    orientation_score = np.mean([(similarity+1)/2 for similarity in orientation_similarities])

    # --- 最終スコアの統合 ---
    # 位置スコアと向きスコアを平均して最終的な平行性スコアとする
    final_score = (position_score + orientation_score) / 2
    return final_score