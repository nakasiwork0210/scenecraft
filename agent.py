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

    def run_inner_loop(self, user_query: str) -> Dict[str, Any]:
        """
        Inner-Loop を実行し、単一のシーンを生成・改善する。
        """
        # Step 1: Asset Retrieval
        # assets_with_paths を受け取るように asset_retriever を呼び出す
        assets_with_paths = asset_retriever.retrieve_assets(user_query)
        
        # Step 2: Scene Decomposition
        asset_list = list(assets_with_paths.keys())
        sub_scenes = decomposer.decompose_query(user_query, asset_list)
        
        processed_sub_scenes = []
        for i, sub_scene in enumerate(sub_scenes):
            print(f"\n>>> サブシーン {i+1}/{len(sub_scenes)}: '{sub_scene['title']}' の処理を開始")
            
            # Step 3: Scene Graph Construction
            scene_graph = planner.plan_scene_graph(sub_scene['description'], sub_scene['asset_list'])

            # Step 4: Initial Script Generation
            # coderにはアセット名とパスの辞書を渡す
            script = coder.generate_script_with_solver(scene_graph, {name: assets_with_paths[name] for name in sub_scene['asset_list']})

            processed_sub_scenes.append({
                "title": sub_scene['title'],
                "script": script,
                "scene_graph": scene_graph,
                "asset_list": sub_scene['asset_list'],
                "assets_with_paths": {name: assets_with_paths[name] for name in sub_scene['asset_list']}
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