# modules/coder.py
"""
Step 4: スクリプト生成 (Code Generation)
論文の Section 2.3 と Equation (4) に対応。
"""
from typing import List, Dict
import os

def generate_script_with_solver(scene_graph: Dict, assets_with_paths: Dict[str, str]) -> str:
    """
    シーングラフから、最適化ソルバーと実際のレンダリング処理を含む
    実行可能なBlender Pythonスクリプトを生成する。
    """
    print("\n--- [Step 4] 💻 プロダクト品質のスクリプトを生成 ---")

    asset_list_str = list(assets_with_paths.keys())
    
    # アセットのファイルパスをBlenderスクリプト内で使えるように辞書形式の文字列に変換
    # Windowsのパス区切り文字 `\` がエスケープされないよう 'r' プレフィックスを付与
    asset_paths_dict_str = ", ".join([f"'{name}': r'{path}'" for name, path in assets_with_paths.items() if path])

    # --- Script Part 1: 初期設定とアセット読み込み ---
    script_parts = [
        "import bpy, random, numpy as np, os, sys",
        "from typing import List, Dict",
        "",
        "# 外部モジュールをBlenderのPython環境からインポート可能にする",
        "sys.path.append(os.path.abspath('.'))",
        "from library.layout import Layout",
        "from library.spatial_skill_library import SKILLS",
        "",
        "# --- 1. アセットの読み込みと初期化 ---",
        f"asset_paths = {{{asset_paths_dict_str}}}",
        f"asset_names = {asset_list_str}",
        "blender_objects = {}",
        "",
        "# 開始時に既存の全オブジェクトを削除してシーンをクリア",
        "bpy.ops.object.select_all(action='SELECT')",
        "bpy.ops.object.delete()",
        "",
        "print('  [Blender] 3Dアセットをインポート中...')",
        "for name, path in asset_paths.items():",
        "    if path and os.path.exists(path):",
        "        try:",
        "            ext = os.path.splitext(path)[1].lower()",
        "            if ext == '.obj':",
        "                bpy.ops.import_scene.obj(filepath=path)",
        "            elif ext == '.fbx':",
        "                bpy.ops.import_scene.fbx(filepath=path)",
        "            elif ext in ['.glb', '.gltf']:",
        "                 bpy.ops.import_scene.gltf(filepath=path)",
        "            # 選択されたオブジェクト（インポートされたオブジェクト）を取得",
        "            imported_obj = bpy.context.selected_objects[0]",
        "            blender_objects[name] = imported_obj",
        "            blender_objects[name].name = name",
        "            print(f'    ✅ {name} をインポートしました。')",
        "        except Exception as e:",
        "            print(f'    ❌ {name} のインポートに失敗しました: {e}')",
        "    else:",
        "        print(f'    [Warning] アセットのパスが見つかりません: {name} at {path}')",
        "",
        "# 初期レイアウトをランダムに設定",
        "assets_layout = {name: Layout(location=(random.uniform(-10, 10), random.uniform(-10, 10), 0), orientation=(0,0,0), scale=(1,1,1)) for name in asset_names}",
        "",
        "\n# --- 2. 制約評価関数 ---",
        "def evaluate_layout(current_assets: Dict[str, Layout]) -> float:",
        "    total_score = 0.0"
    ]

    # --- Script Part 2: 制約評価ロジックの動的構築 ---
    relations = scene_graph.get("relations", [])
    if relations:
        for relation in relations:
            rel_type = relation.get("type", "").lower()
            if rel_type not in SKILLS:
                continue
                
            involved = relation['involved_assets']
            args = relation.get("args", {})
            
            assets_to_pass = [f"current_assets['{name}']" for name in involved]
            args_str = ", ".join([f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in args.items()])

            script_parts.append(f"    # {rel_type} 関係の評価")
            if len(assets_to_pass) > 1 and rel_type not in ["alignment", "parallelism", "symmetry"]:
                func_call = f"SKILLS['{rel_type}']({assets_to_pass[0]}, {assets_to_pass[1]}, {args_str})"
            else:
                func_call = f"SKILLS['{rel_type}']([{', '.join(assets_to_pass)}], {args_str})"
            script_parts.append(f"    total_score += {func_call}")

    # --- Script Part 3: 最適化ソルバー ---
    script_parts.extend([
        "    return total_score",
        "\n# --- 3. 最適化ソルバー (制約ベースの探索) ---",
        "def constraint_based_search(initial_assets: Dict[str, Layout], max_iter=100) -> Dict[str, Layout]:",
        "    best_layout = {k: v.copy() for k, v in initial_assets.items()}",
        "    best_score = evaluate_layout(best_layout)",
        "    print(f'  [Solver] 初期スコア: {best_score:.4f}')",
        "    for _ in range(max_iter):",
        "        current_layout = {k: v.copy() for k, v in best_layout.items()}",
        "        asset_to_move = random.choice(list(current_layout.keys()))",
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
    ])
    
    # --- Script Part 4: メイン処理とレンダリング設定 ---
    script_parts.extend([
        "\n# --- 4. メイン処理 ---",
        "final_layout = constraint_based_search(assets_layout)",
        "print('  [Solver] ✔️ 最適化されたレイアウトが決定しました。')",
        "\n# --- 5. Blenderシーンへの最終レイアウト適用 ---",
        "print('  [Blender] ✔️ 最終レイアウトをBlenderシーンに適用します。')",
        "for name, layout in final_layout.items():",
        "    if name in blender_objects:",
        "        obj = blender_objects[name]",
        "        obj.location = layout.location",
        "        obj.rotation_euler = [np.radians(angle) for angle in layout.orientation]",
        "        obj.scale = layout.scale",
        
        "\n# --- 6. レンダリングのためのシーン設定 ---",
        "print('  [Blender] カメラとライトを設定します。')",
        "# 地面を追加",
        "bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))",
        "ground = bpy.context.active_object",
        "ground.name = 'Ground'",
        
        "# カメラを配置",
        "bpy.ops.object.camera_add(location=(15, -20, 15))",
        "camera = bpy.context.active_object",
        "bpy.context.scene.camera = camera",
        
        "# カメラがシーンの中心を向くように設定",
        "look_at_target = bpy.data.objects.get(asset_names[0]) if asset_names else ground",
        "direction = look_at_target.location - camera.location",
        "rot_quat = direction.to_track_quat('-Z', 'Y')",
        "camera.rotation_euler = rot_quat.to_euler()",
        
        "# ライト(太陽)を追加",
        "bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))",
        "light = bpy.context.active_object",
        "light.data.energy = 3",
        "light.data.angle = np.radians(15)", # 少し柔らかい影にする
        "",
        "\n# --- 7. レンダリング実行 ---",
        "print('  [Blender] レンダリングを開始します。')",
        "bpy.context.scene.render.engine = 'CYCLES'", # 高品質なCyclesレンダラーを使用
        "bpy.context.scene.cycles.samples = 128", # サンプル数を設定
        "bpy.context.scene.render.image_settings.file_format = 'PNG'",
        "bpy.context.scene.render.resolution_x = 1024",
        "bpy.context.scene.render.resolution_y = 768",
        "# 出力パスはblender_env.pyからコマンドライン引数経由で設定される",
        "bpy.ops.render.render(write_still=True)",
        "print(f'  [Blender] ✔️ レンダリングが完了しました。')",
    ])
    
    print("✔️ 最適化とレンダリングロジックを含む完全なスクリプトが生成されました。")
    return "\n".join(script_parts)