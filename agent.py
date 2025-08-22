# agent.py
"""
SceneCraftエージェントのコアロジックを実装するモジュール
論文の Figure 2, 3 に示されたワークフロー全体を統括する。
"""
from typing import List, Dict, Any
import inspect
from collections import Counter # Counterをインポート

from modules import asset_retriever, decomposer, planner, coder, reviewer
from utils.llm_utils import call_llm, extract_python_code
from utils.config import LEARNER_MODEL
from library import spatial_skill_library

class SceneCraftAgent:
    """
    テキストから3Dシーンを生成し、自己進化するLLMエージェント
    """
    def __init__(self):
        self.history = [] # Outer-Loopのための履歴
        def predict_camera_work(self, scene_description: str, all_asset_names: List[str]) -> Dict[str, Any]:
        """
        【新規追加】LLMを使い、シーンに最適なカメラの位置と注視点を予測する。
        """
        print("\n--- [Camera Planner] 📸 LLMに最適なカメラワークを考案させています ---")
        
        prompt = f"""
        これから「{scene_description}」というテーマの3Dシーンをレンダリングします。
        このシーンの魅力を最大限に引き出すための、プロのカメラマンのようなカメラ設定を提案してください。

        シーンに含まれるアセット: {all_asset_names}

        提案は、カメラの「位置(location)」と「注視点(look_at)」の2つのキーを持つJSON形式で出力してください。
        - location: カメラを配置する座標 (x, y, z)
        - look_at: カメラがどのオブジェクト名を見るべきか。シーンの中心を見る場合は "center" と指定。

        出力形式の例:
        ```json
        {{
          "location": [15.0, -25.0, 12.0],
          "look_at": "Hunter"
        }}
        ```
        """
        
        camera_settings = call_llm(LEARNER_MODEL, prompt) # 高度な推論が可能なモデルを使用
        
        if isinstance(camera_settings, dict) and "location" in camera_settings and "look_at" in camera_settings:
            print(f"    ✔️ カメラ設定が決定しました: 位置={camera_settings['location']}, 注視点='{camera_settings['look_at']}'")
            return camera_settings
        else:
            print("    [Warning] カメラ設定の予測に失敗しました。デフォルト設定を使用します。")
            return {"location": [15, -20, 15], "look_at": "center"}

    def run_inner_loop(self, user_query: str) -> Dict[str, Any]:
        """
        Inner-Loop を実行し、単一のシーンを生成・改善する。
        """
        # Step 1: Asset Retrieval
        assets_info = asset_retriever.retrieve_assets(user_query)
        
        # Step 2: Scene Decomposition
        asset_list = list(assets_info.keys())
        sub_scenes = decomposer.decompose_query(user_query, asset_list)
        
        processed_sub_scenes = []
        for i, sub_scene in enumerate(sub_scenes):
            # ... (Step 3: Scene Graph Construction) ...
            
            # 【変更】coderに渡す情報に、ファイルパスと高さの両方を含める
            assets_for_coder = {name: assets_info[name] for name in sub_scene['asset_list']}
            script = coder.generate_script_with_solver(scene_graph, assets_for_coder)

            processed_sub_scenes.append({
                "title": sub_scene['title'],
                "script": script,
                "scene_graph": scene_graph,
                "asset_list": sub_scene['asset_list'],
                "assets_info": assets_for_coder # 改善ループで再利用するために保存
            })
        
        return {"query": user_query, "processed_sub_scenes": processed_sub_scenes}

    def run_outer_loop(self, refinement_history: List[Dict]):
        """
        (Outer-Loop) 修正履歴から汎用的なスキルを学習し、ライブラリを更新する。
        論文の Section 2.4 に対応。
        """
        print("\n--- [Outer-Loop] 🎓 スキルライブラリの自己進化 ---")
        
        if not refinement_history:
            print("  [Info] 修正履歴がないため、スキル学習をスキップします。")
            return

        # --- 【改善点】修正履歴から学習すべきスキルを動的に特定 ---
        # 修正されたリレーションのタイプを集計
        fixed_relation_types = []
        for revision in refinement_history:
            # 'change' と 'action' の存在を確認
            change_info = revision.get("change", {})
            if change_info.get("action") == "update_args":
                # 'target_relation' と 'type' の存在を確認
                target_relation = revision.get("target_relation", {})
                target_type = target_relation.get("type")
                if target_type:
                    fixed_relation_types.append(target_type)
        
        if not fixed_relation_types:
            print("  [Info] 有効な修正履歴（update_argsアクション）がないため、スキル学習をスキップします。")
            return

        # 最も頻繁に修正されたスキルを学習対象とする
        skill_to_improve = Counter(fixed_relation_types).most_common(1)[0][0]
        
        print(f"  🔥 最も頻繁に修正されたスキル '{skill_to_improve}' を学習対象として特定しました。")

        original_function_code = spatial_skill_library.get_skill_source(skill_to_improve)
        
        # 論文 Figure 4 の例を再現
        improved_function_example = inspect.getsource(spatial_skill_library.SKILLS[skill_to_improve])
        
        prompt = f"""
        あなたは、3Dシーン生成エージェントのスキルを進化させる役割を担っています。
        以下の関数は、シーン内のオブジェクトの '{skill_to_improve}' 関係を評価するものですが、これまでの利用でいくつかの問題点が発見されました。

        - **改善の方向性**: これまでのシーン生成過程で、このスキルは何度も修正が必要でした。より堅牢で汎用的な関数へと進化させる必要があります。

        この学習結果を元に、元の関数を改善し、より堅牢な新しい `{skill_to_improve}` 関数を生成してください。
        
        元の関数:
        ```python
        {original_function_code}
        ```
        
        改善後の理想的な関数（参考）:
        ```python
        {improved_function_example}
        ```

        あなたのタスクは、この学びを反映した最終的な `{skill_to_improve}_score` 関数をPythonコードとして出力することです。
        """
        
        learned_function_code = call_llm(LEARNER_MODEL, prompt, is_json=False)
        learned_function_code = extract_python_code(learned_function_code)

        print("\n  LLMによる学習の結果、新しい関数が生成されました:")
        print(learned_function_code)
        
        # スキルライブラリを動的に更新
        spatial_skill_library.update_skill(skill_to_improve, learned_function_code)