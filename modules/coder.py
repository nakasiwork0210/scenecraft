# modules/coder.py
from typing import List, Dict, Any

def generate_evaluation_logic(scene_graph: Dict) -> str:
    """
    シーングラフから、評価関数のロジック部分のみを生成する。
    """
    logic_parts = []
    relations = scene_graph.get("relations", [])
    if not relations:
        return "    pass"

    for relation in relations:
        rel_type = relation.get("type", "").lower()
        involved = relation.get('involved_assets', [])
        args = relation.get("args", {})
        
        assets_to_pass = [f"current_assets['{name}']" for name in involved]
        # 引数がない場合でも対応できるように修正
        args_str = ", ".join([f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in args.items()]) if args else ""

        logic_parts.append(f"    # --- {rel_type} 関係の評価 ---")
        func_call = ""
        if len(assets_to_pass) > 1 and rel_type not in ["alignment", "parallelism", "symmetry"]:
            func_call = f"SKILLS.get('{rel_type}')({assets_to_pass[0]}, {assets_to_pass[1]}, {args_str})"
        else:
            # 複数アセットの場合、args_strの前にカンマが必要かチェック
            comma = ", " if args_str else ""
            func_call = f"SKILLS.get('{rel_type}')([{', '.join(assets_to_pass)}]{comma}{args_str})"
        
        logic_parts.append(f"    if SKILLS.get('{rel_type}'):")
        logic_parts.append(f"        total_score += {func_call}")
        
    return "\n".join(logic_parts)


def generate_script_with_solver(scene_graph: Dict, assets_info: Dict[str, Dict], camera_settings: Dict[str, Any]) -> str:
    """
    テンプレートを基に、最適化とレンダリングを行う完全なBlenderスクリプトを生成する。
    """
    print("\n--- [Step 4] 💻 テンプレートベースのスクリプトを生成 ---")

    try:
        with open("templates/blender_script_template.py", "r", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        print("❌ エラー: blender_script_template.py が templates/ ディレクトリに見つかりません。")
        return ""

    evaluation_logic = generate_evaluation_logic(scene_graph)

    script = template.format(
        asset_info=str(assets_info),
        evaluation_logic=generate_evaluation_logic(scene_graph),
        camera_location=str(camera_settings.get("location", [15, -20, 15])),
        camera_look_at=f'"{camera_settings.get("look_at", "center")}"'
    )
    
    print("✔️ テンプレートから完全なスクリプトが生成されました。")
    return script