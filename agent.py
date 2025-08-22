# agent.py
"""
SceneCraftエージェントのコアロジックを実装するモジュール
論文の Figure 2, 3 に示されたワークフロー全体を統括する。
"""
from typing import List, Dict, Any
import inspect

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
        assets_with_desc = asset_retriever.retrieve_assets(user_query)
        asset_list = list(assets_with_desc.keys())

        # Step 2: Scene Decomposition
        sub_scenes = decomposer.decompose_query(user_query, asset_list)
        
        processed_sub_scenes = [] # 変数名を final_scripts から変更
        for i, sub_scene in enumerate(sub_scenes):
            print(f"\n>>> サブシーン {i+1}/{len(sub_scenes)}: '{sub_scene['title']}' の処理を開始")
            
            # Step 3: Scene Graph Construction
            scene_graph = planner.plan_scene_graph(sub_scene['description'], sub_scene['asset_list'])

            # Step 4: Initial Script Generation
            script = coder.generate_script_with_solver(scene_graph, sub_scene['asset_list'])

            # Step 5: Iterative Refinement (Self-Improvement)
            # ... この後の改善ループは main.py で実行 ...
            
            # 【変更点】返り値に scene_graph と asset_list を追加
            processed_sub_scenes.append({
                "title": sub_scene['title'],
                "script": script,
                "scene_graph": scene_graph,
                "asset_list": sub_scene['asset_list']
            })
        
        return {"query": user_query, "processed_sub_scenes": processed_sub_scenes}


    def run_outer_loop(self, refinement_history: List[Dict]):
        """
        (Outer-Loop) 修正履歴から汎用的なスキルを学習し、ライブラリを更新する。
        論文の Section 2.4 に対応。
        """
        print("\n--- [Outer-Loop] 🎓 スキルライブラリの自己進化 ---")
        
        # 履歴の中から改善が見られた関数を特定する（ここでは'parallelism'を仮定）
        # 実際のシステムでは、コードの差分分析などを行って自動で特定する
        skill_to_improve = "parallelism"
        
        original_function_code = spatial_skill_library.get_skill_source(skill_to_improve)
        
        # 履歴から、この関数に関する修正内容を収集
        # このデモでは、手動で改善後のコードを与えることでシミュレート
        # revised_function_code = ... (履歴から抽出)
        
        # 論文 Figure 4 の例を再現
        improved_function_example = inspect.getsource(spatial_skill_library.parallelism_score) # 完成版を理想形とする
        
        print(f"  学習対象のスキル: '{skill_to_improve}'")

        prompt = f"""
        あなたは、3Dシーン生成エージェントのスキルを進化させる役割を担っています。
        以下の関数は、シーン内のオブジェクトの「平行性」を評価するものですが、これまでの利用でいくつかの問題点が発見されました。

        - **元の関数**: 位置関係しか考慮していなかった。
        - **改善の方向性**: 複数のシーンを生成する過程で、オブジェクトの「向き」も揃える必要があることが判明した。

        この学習結果を元に、元の関数を改善し、**位置と向きの両方を考慮する**より堅牢な新しい `{skill_to_improve}` 関数を生成してください。
        
        元の関数:
        ```python
        {original_function_code}
        ```
        
        改善後の理想的な関数（参考）:
        ```python
        {improved_function_example}
        ```

        あなたのタスクは、この学びを反映した最終的な `parallelism_score` 関数をPythonコードとして出力することです。
        """
        
        learned_function_code = call_llm(LEARNER_MODEL, prompt, is_json=False)
        learned_function_code = extract_python_code(learned_function_code)

        print("\n  LLMによる学習の結果、新しい関数が生成されました:")
        print(learned_function_code)
        
        # スキルライブラリを動的に更新
        spatial_skill_library.update_skill(skill_to_improve, learned_function_code)