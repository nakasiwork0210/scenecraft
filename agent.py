# agent.py
"""
SceneCraftエージェントのコアロジックを実装するモジュール
"""
import openai
import base64
from typing import List

from config import OPENAI_API_KEY, DECOMPOSER_MODEL, PLANNER_MODEL, REVIEWER_MODEL
from utils import parse_llm_response_to_json, extract_python_code

class SceneCraftAgent:
    """
    テキストから3Dシーンを生成するLLMエージェント
    """
    def __init__(self):
        openai.api_key = OPENAI_API_KEY

    def decompose_query(self, user_query: str) -> List[dict]:
        """ユーザーのクエリをサブシーンのリストに分解する (Step 2)"""
        prompt = f"""
        私はBlenderスクリプトを書いて、次のシーンを生成しようとしています: "{user_query}"
        
        このシーンを構築するための具体的な計画を、複数のステップに分けて提示してください。
        各ステップはJSONオブジェクトのリストとして、以下のキーを持つ形式で出力してください:
        - "title": ステップの概要
        - "asset_list": このステップで追加するアセット名のリスト
        - "description": このステップ完了後の詳細な視覚的記述
        
        環境アセットから始め、徐々に詳細なアセットを追加してください。
        [
            {{ "title": "...", "asset_list": [...], "description": "..." }},
            {{ "title": "...", "asset_list": [...], "description": "..." }}
        ]
        """
        response = openai.ChatCompletion.create(
            model=DECOMPOSER_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return parse_llm_response_to_json(response.choices[0].message.content)

    def plan_scene_graph(self, sub_scene_description: str, asset_list: List[str]) -> dict:
        """サブシーンのシーングラフを構築する (Step 3)"""
        prompt = f"""
        以下の記述とアセットリストに基づき、3Dシーンのリレーショナル二部グラフをJSONで構築してください。
        シーン記述: "{sub_scene_description}"
        アセットリスト: {asset_list}
        
        関係性には "Proximity", "Alignment", "Parallelism", "Perpendicularity" などを使用してください。
        
        出力形式:
        {{
            "relations": [
                {{ "type": "Alignment", "involved_assets": ["house1", "house2"], "args": {{"axis": "x"}} }},
                {{ "type": "Proximity", "involved_assets": ["lamp1", "house1"], "args": {{"min_dist": 1.0}} }}
            ]
        }}
        """
        response = openai.ChatCompletion.create(
            model=PLANNER_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return parse_llm_response_to_json(response.choices[0].message.content)

    def generate_script(self, scene_graph: dict, asset_list: List[str]) -> str:
        """シーングラフから実行可能なPythonスクリプトを生成する (Step 4)"""
        # この部分は実際のBlender APIや制約ソルバーと連携するため、
        # ここではスクリプトの骨格を生成する単純な例とします。
        script_parts = [
            "import bpy",
            "import numpy as np",
            "from spatial_skill_library import *",
            "from layout import Layout",
            "",
            "# TODO: アセットの読み込みと初期化",
            f"asset_names = {asset_list}",
            "assets = {name: Layout(...) for name in asset_names}",
            "",
            "# 制約の評価とレイアウト最適化",
            "def evaluate_layout(current_assets):",
            "    total_score = 0"
        ]

        for relation in scene_graph.get("relations", []):
            func_name = f"{relation['type'].lower()}_score"
            assets_str = ", ".join([f"current_assets['{name}']" for name in relation['involved_assets']])
            args_str = ", ".join([f"{k}={v}" for k, v in relation.get("args", {}).items()])
            
            script_parts.append(f"    score = {func_name}({assets_str}, {args_str})")
            script_parts.append("    total_score += score")
        
        script_parts.extend([
            "    return total_score",
            "",
            "# TODO: 最適化ループ（例: 焼きなまし法、遺伝的アルゴリズムなど）",
            "# best_layout = optimize(assets, evaluate_layout)",
            "# TODO: best_layoutをBlenderシーンに適用"
        ])
        
        return "\n".join(script_parts)

    def review_and_revise(self, sub_scene_description: str, image_path: str, current_script: str) -> str:
        """レンダリング画像を評価し、スクリプトを修正する (Step 5)"""
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        prompt = f"""
        あなたは3Dシーンのレビュアーです。
        テキスト記述: "{sub_scene_description}"
        
        提供された画像が記述を正確に表現しているか評価し、問題点があれば指摘してください。
        その後、問題を修正するための完全なBlender Pythonスクリプトを```python ... ```形式で出力してください。

        現在のスクリプト:
        {current_script}
        """
        response = openai.ChatCompletion.create(
            model=REVIEWER_MODEL,
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ],
            max_tokens=4096
        )
        return extract_python_code(response.choices[0].message.content)