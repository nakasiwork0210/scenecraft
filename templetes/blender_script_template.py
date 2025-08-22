# templates/blender_script_template.py
import bpy, random, numpy as np, os, sys
from typing import List, Dict

# --- 外部モジュールのインポート設定 ---
sys.path.append(os.path.abspath('.'))
from library.layout import Layout
from library.spatial_skill_library import SKILLS
from utils import config # 設定ファイルをインポート

# --- プレースホルダー (この部分がcoder.pyによって動的に埋め込まれる) ---
ASSET_PATHS = {asset_paths}
ASSET_NAMES = {asset_names}

# --- 1. アセットの読み込みと初期化 ---
blender_objects = {{}}

# 開始時に既存の全オブジェクトを削除してシーンをクリア
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

print('  [Blender] 3Dアセットをインポートし、スケールを正規化中...')
for name, info in ASSET_INFO.items():
    path = info.get("file_path")
    target_height = info.get("height", 1.0)
    
    if path and os.path.exists(path):
        # ... (アセットのインポート処理) ...
        imported_obj = bpy.context.selected_objects[0]
        
        # --- 【追加】スケールの正規化と適用 ---
        # 現在のオブジェクトの高さを取得 (dimensions.z)
        current_height = imported_obj.dimensions.z
        if current_height > 0:
            # 高さを1に正規化するためのスケール係数を計算
            scale_factor = target_height / current_height
            imported_obj.scale = (scale_factor, scale_factor, scale_factor)
            bpy.context.view_layer.update() # スケール変更を確定
            print(f'    ✅ {{name}} をインポートし、高さを {{target_height}}m に調整しました。')

        blender_objects[name] = imported_obj
        # ...
        
assets_layout = {{name: Layout(location=(random.uniform(-10, 10), random.uniform(-10, 10), 0), orientation=(0,0,0), scale=(1,1,1)) for name in ASSET_NAMES}}

# --- 2. 制約評価関数 ---
def evaluate_layout(current_assets: Dict[str, Layout]) -> float:
    total_score = 0.0
{evaluation_logic}
    return total_score

# --- 3. 最適化ソルバー (制約ベースの探索) ---
def constraint_based_search(initial_assets: Dict[str, Layout], max_iter=100) -> Dict[str, Layout]:
    best_layout = {{k: v.copy() for k, v in initial_assets.items()}}
    best_score = evaluate_layout(best_layout)
    print(f'  [Solver] 初期スコア: {{best_score:.4f}}')
    for _ in range(max_iter):
        current_layout = {{k: v.copy() for k, v in best_layout.items()}}
        asset_to_move = random.choice(list(current_layout.keys()))
        loc = list(current_layout[asset_to_move].location)
        ori = list(current_layout[asset_to_move].orientation)
        loc[random.randint(0,2)] += random.uniform(-0.5, 0.5)
        ori[random.randint(0,2)] = (ori[random.randint(0,2)] + random.uniform(-5, 5)) % 360
        current_layout[asset_to_move].location = tuple(loc)
        current_layout[asset_to_move].orientation = tuple(ori)
        current_score = evaluate_layout(current_layout)
        if current_score > best_score:
            best_score = current_score
            best_layout = current_layout
    print(f'  [Solver] 最適化後のスコア: {{best_score:.4f}}')
    return best_layout

# --- 4. メイン処理 ---
final_layout = constraint_based_search(assets_layout)
print('  [Solver] ✔️ 最適化されたレイアウトが決定しました。')

# --- 5. Blenderシーンへの最終レイアウト適用 ---
print('  [Blender] ✔️ 最終レイアウトをBlenderシーンに適用します。')
for name, layout in final_layout.items():
    if name in blender_objects:
        obj = blender_objects[name]
        obj.location = layout.location
        obj.rotation_euler = [np.radians(angle) for angle in layout.orientation]
        obj.scale = layout.scale

# --- 6. レンダリングのためのシーン設定 ---
print('  [Blender] カメラとライトを設定します。')
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = 'Ground'

bpy.ops.object.camera_add(location=CAMERA_LOCATION)
camera = bpy.context.active_object
bpy.context.scene.camera = camera

look_at_target = bpy.data.objects.get(CAMERA_LOOK_AT)
if not look_at_target:
    look_at_target = bpy.data.objects.get(ASSET_NAMES[0]) if ASSET_NAMES else ground

if look_at_target:
    direction = look_at_target.location - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()


direction = look_at_target.location - camera.location
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
light = bpy.context.active_object
light.data.energy = 3
light.data.angle = np.radians(15)

# --- 7. レンダリング実行 ---
print('  [Blender] レンダリングを開始します。')
bpy.context.scene.render.engine = config.RENDER_ENGINE
bpy.context.scene.cycles.samples = config.RENDER_SAMPLES
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.resolution_x = config.RENDER_RESOLUTION_X
bpy.context.scene.render.resolution_y = config.RENDER_RESOLUTION_Y
bpy.ops.render.render(write_still=True)
print(f'  [Blender] ✔️ レンダリングが完了しました。')