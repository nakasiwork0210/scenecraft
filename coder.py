def generate_initial_script(scene_graph: dict, asset_list: List[str]) -> str:
    """
    シーングラフに基づいて初期のBlender Pythonスクリプトを生成する。
    """
    script_parts = [
        "import bpy",
        "import numpy as np",
        "#... 空間スキルライブラリの関数定義...",
        "from spatial_skill_library import *",
        "",
        "# アセットの読み込みと初期レイアウトの定義",
        "assets = {}",
        "for asset_name in {asset_list}:",
        "    # assets[asset_name] = load_asset(asset_name,...)",
        "",
        "# 制約の定義",
        "constraints ="
    ]
    
    for relation in scene_graph["relations"]:
        func_name = f"{relation['type'].lower()}_score"
        involved_assets_str = ", ".join([f"assets['{name}']" for name in relation['involved_assets']])
        
        # 例: constraints.append((proximity_score, [assets['lamp1'], assets['house1']], {{'min_distance': 1.0}}))
        # LLMが関数の引数も予測する必要がある
        constraint_line = f"constraints.append(create_constraint('{func_name}', [{involved_assets_str}]))"
        script_parts.append(constraint_line)
        
    script_parts.extend()
    
    return "\n".join(script_parts)