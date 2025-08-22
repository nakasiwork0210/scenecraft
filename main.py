# main.py
"""
SceneCraftエージェントを実行し、テキストから3Dシーン生成プロセスを実演する。
"""
from agent import SceneCraftAgent
from utils import blender_env
from library import spatial_skill_library
from modules import reviewer, coder # coder と reviewer をインポート
import copy

def main():
    print("============== SceneCraft Agent Initializing ==============")
    spatial_skill_library.initialize_skills()
    agent = SceneCraftAgent()
    
    # 論文の例に基づくユーザーからのクエリ
    user_query = "a girl hunter walking in a slum village with fantasy creatures"
    print(f"▶️ ユーザーのクエリ: \"{user_query}\"")
    
    # =================================================================
    # Inner-Loop: 個別のシーン生成と改善
    # =================================================================
    print("\n============== Starting Inner-Loop ==============")
    
    #inner_loopを実行してアセット選定、初めの配置決定を行う
    run_result = agent.run_inner_loop(user_query)
    
    refinement_history = []
    
    # Step 5: 自己改善ループを本格実装
    num_refinement_steps = 2 # 改善試行の最大回数
    
    # 【変更点】agentから渡された、処理済みのサブシーンリストを使用する
    processed_sub_scenes = run_result["processed_sub_scenes"]
    
    for i, sub_scene_data in enumerate(processed_sub_scenes):
        script = sub_scene_data["script"]
        title = sub_scene_data["title"]
        scene_graph = sub_scene_data["scene_graph"]
        asset_list = sub_scene_data["asset_list"] # asset_listも取得
        
        for step in range(num_refinement_steps):
            print(f"\n>>> サブシーン '{title}' の自己改善ループ {step + 1}/{num_refinement_steps}")
            
            # a. スクリプトを実行してレンダリング
            image_path = f"output/rendered_image_subscene{i+1}_step{step}.png"
            blender_env.execute_blender_script(script, image_path, "assets")
            base64_image = blender_env.get_base64_image(image_path)
            if not base64_image:
                print("  [Warning] 画像ファイルの読み込みに失敗し、レビューをスキップします。")
                continue
            
            # b. レビューと修正案の取得
            correction = reviewer.review_and_suggest_correction(title, base64_image, scene_graph)

            # c. 修正案に基づき、シーングラフを更新してスクリプトを再生成
            if correction.get("status") == "revision_needed":
                print("  [Planner] 修正案に基づき、シーングラフを更新します。")
                refinement_history.append({
                    "sub_scene": title,
                    "feedback": correction.get("feedback"),
                    "original_graph": copy.deepcopy(scene_graph),
                    "change": correction.get("suggested_change"),
                })

                # --- シーングラフの修正ロジック ---
                change = correction["suggested_change"]
                target = correction["target_relation"]
                if change["action"] == "update_args":
                    for relation in scene_graph.get("relations", []):
                        if relation["type"] == target["type"] and \
                           set(relation["involved_assets"]) == set(target["involved_assets"]):
                            print(f"    - Relation '{target['type']}' の引数を {relation.get('args', {})} から {change['new_args']} に更新。")
                            relation["args"].update(change['new_args']) # updateメソッドで引数を更新
                            break
                
                assets_info = sub_scene_data["assets_info"]
                script = coder.generate_script_with_solver(scene_graph, assets_info)
                processed_sub_scenes[i]["script"] = script
            else:
                print("  [Reviewer] 修正は不要と判断されました。このサブシーンの処理を完了します。")
                break
    
    print("\n============== Inner-Loop Finished ==============")
    
    # =================================================================
    # Outer-Loop: 経験からの学習と自己進化
    # =================================================================
    print("\n============== Starting Outer-Loop ==============")
    
    agent.run_outer_loop(refinement_history)
    
    print("\n============== Outer-Loop Finished ==============")
    print("\n✅ 全てのプロセスが完了しました。エージェントは新たなスキルを学習し、進化しました。")

if __name__ == "__main__":
    main()