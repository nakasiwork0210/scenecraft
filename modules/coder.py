# modules/coder.py
"""
Step 4: スクリプト生成 (Code Generation)
論文の Section 2.3 と Equation (4) に対応。
"""
from typing import List, Dict

def generate_script_with_solver(scene_graph: Dict, asset_list: List[str]) -> str:
    """
    シーングラフから、最適化ソルバーを含む実行可能なBlender Pythonスクリプトを生成する。
    """
    print("\n--- [Step 4] 💻 スクリプト生成 ---")
    
    script_parts = [
        "import bpy, random, numpy as np",
        "from typing import List, Dict",
        "# 実際の環境では、以下のライブラリはBlenderアドオンとして読み込まれることを想定",
        "from library.spatial_skill_library import SKILLS, Layout",
        "\n# --- 1. アセットの読み込みと初期化 ---",
        "# 実際のコードでは、ここでアセットファイルをロードし、Blenderオブジェクトを生成します。",
        f"asset_names = {asset_list}",
        "assets_layout = {name: Layout(location=(random.uniform(-10, 10), random.uniform(-10, 10), 0), orientation=(0,0,0), scale=(1,1,1)) for name in asset_names}",
        "# Blender上にダミーのCubeオブジェクトを生成してシーンを表現",
        "blender_objects = {}",
        "for name in asset_names:",
        "    bpy.ops.mesh.primitive_cube_add(size=1, location=assets_layout[name].location)",
        "    blender_objects[name] = bpy.context.active_object",
        "    blender_objects[name].name = name",
        "",
        "\n# --- 2. 制約評価関数 ---",
        "def evaluate_layout(current_assets: Dict[str, Layout]) -> float:",
        "    total_score = 0.0"
    ]

    # scene_graphから評価ロジックを動的に構築
    relations = scene_graph.get("relations", [])
    if relations:
        for relation in relations:
            rel_type = relation.get("type", "").lower()
            # SKILLSに存在しない関係性はスキップ
            if rel_type not in SKILLS:
                continue
                
            involved = relation['involved_assets']
            args = relation.get("args", {})
            
            assets_to_pass = [f"current_assets['{name}']" for name in involved]
            args_str = ", ".join([f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in args.items()])

            script_parts.append(f"    # {rel_type} 関係の評価")
            # スキルの引数構成に応じて呼び出し方を変更
            if len(assets_to_pass) > 1 and rel_type not in ["alignment", "parallelism", "symmetry"]:
                # 2アセット間の関係 (例: proximity)
                func_call = f"SKILLS['{rel_type}']({assets_to_pass[0]}, {assets_to_pass[1]}, {args_str})"
            else:
                # 複数アセット間の関係 (例: alignment)
                func_call = f"SKILLS['{rel_type}']([{', '.join(assets_to_pass)}], {args_str})"

            script_parts.append(f"    total_score += {func_call}")

    script_parts.extend([
        "    return total_score",
        "\n# --- 3. 最適化ソルバー (論文で言及されている制約ベースの探索) ---",
        "def constraint_based_search(initial_assets: Dict[str, Layout], max_iter=100) -> Dict[str, Layout]:",
        "    best_layout = {k: v for k, v in initial_assets.items()}",
        "    best_score = evaluate_layout(best_layout)",
        "    for _ in range(max_iter):",
        "        current_layout = {k: v for k, v in best_layout.items()}",
        "        asset_to_move = random.choice(list(current_layout.keys()))",
        "        # 位置と向きを少しだけランダムに動かす摂動処理",
        "        loc = list(current_layout[asset_to_move].location)",
        "        ori = list(current_layout[asset_to_move].orientation)",
        "        loc[random.randint(0,2)] += random.uniform(-0.5, 0.5)",
        "        ori[random.randint(0,2)] = (ori[random.randint(0,2)] + random.uniform(-5, 5)) % 360",
        "        current_layout[asset_to_move].location = tuple(loc)",
        "        current_layout[asset_to_move].orientation = tuple(ori)",
        "        current_score = evaluate_layout(current_layout)",
        "        if current_score > best_score:",
        "            best_score = current_score",
        "            best_layout = current_layout",
        "    print(f'  [Solver] 最適化後のスコア: {best_score:.4f}')",
        "    return best_layout",
        "\n# --- 4. メイン処理 ---",
        "final_layout = constraint_based_search(assets_layout)",
        "print('  [Solver] ✔️ 最適化されたレイアウトが決定しました。')",
        "\n# --- 5. Blenderシーンへの最終レイアウト適用 ---",
        "print('  [Blender] ✔️ 最終レイアウトをBlenderシーンに適用します。')",
        "for name, layout in final_layout.items():",
        "    if name in blender_objects:",
        "        obj = blender_objects[name]",
        "        obj.location = layout.location",
        "        # オイラー角の単位をラジアンに変換して適用",
        "        obj.rotation_euler = [np.radians(angle) for angle in layout.orientation]",
        "        obj.scale = layout.scale",
        "print('  [Blender] ✔️ シーンの更新が完了しました。')",
    ])
    
    print("✔️ 最適化ソルバーとシーン適用ロジックを含む完全なスクリプトが生成されました。")
    return "\n".join(script_parts)