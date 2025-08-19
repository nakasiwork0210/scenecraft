# modules/planner.py
"""
Step 3: シーングラフの構築 (Scene Graph Construction)
論文の Section 2.2 に対応。
"""
from typing import List, Dict
from utils.llm_utils import call_llm
from utils.config import PLANNER_MODEL
from library.spatial_skill_library import SKILLS

def plan_scene_graph(sub_scene_description: str, asset_list: List[str]) -> Dict:
    """
    サブシーンの説明から、アセット間の空間関係を示すシーングラフを生成する。
    """
    print("\n--- [Step 3] 🗺️ シーングラフ構築 ---")
    available_skills = list(SKILLS.keys())
    prompt = f"""
    以下の記述とアセットリストに基づき、3Dシーンのリレーショナル二部グラフをJSONで構築してください。
    シーン記述: "{sub_scene_description}"
    アセットリスト: {asset_list}
    
    利用可能な関係性の種類: {available_skills}
    
    出力形式:
    ```json
    {{
        "relations": [
            {{ "type": "alignment", "involved_assets": ["house1", "house2"], "args": {{"axis": "x"}} }},
            {{ "type": "proximity", "involved_assets": ["lamp1", "house1"], "args": {{"min_dist": 1.0}} }}
        ]
    }}
    ```
    """
    scene_graph = call_llm(PLANNER_MODEL, prompt)
    print("✔️ シーングラフが構築されました。")
    return scene_graph