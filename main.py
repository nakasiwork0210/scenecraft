# main.py
"""
SceneCraftエージェントを実行し、テキストから3Dシーン生成プロセスを実演する。
"""
from agent import SceneCraftAgent
from utils import blender_env
from library import spatial_skill_library
from library import spatial_skill_library

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
    
    # Step 1-4 を実行
    run_result = agent.run_inner_loop(user_query)
    
    refinement_history = []
    
    # Step 5: 自己改善ループを本格実装
    num_refinement_steps = 2 # 改善試行の最大回数
    
    # agent.run_inner_loopから最終スクリプトだけでなく、シーングラフも受け取るようにする
    # (※この変更のため、agent.pyのrun_inner_loopの返り値も修正が必要です)
    run_result = agent.run_inner_loop(user_query)
    
    final_scripts = run_result["final_scripts"]
    
    for i, sub_scene_data in enumerate(final_scripts):
        script = sub_scene_data["script"]
        title = sub_scene_data["title"]
        scene_graph = sub_scene_data["scene_graph"] # 実行結果からシーングラフを取得
        
        for step in range(num_refinement_steps):
            print(f"\n>>> サブシーン '{title}' の自己改善ループ {step + 1}/{num_refinement_steps}")
            
            # a. スクリプトを実行してレンダリング
            image_path = f"output/rendered_image_subscene{i+1}_step{step}.png"
            # blender_env.pyにassetライブラリのパスを渡すように修正
            blender_env.execute_blender_script(script, image_path, "assets")
            
            # b. レビューと修正案の取得
            base64_image = blender_env.get_base64_image(image_path)
            if not base64_image:
                print("  [Warning] 画像ファイルの読み込みに失敗し、レビューをスキップします。")
                continue

            # 新しいreviewerを呼び出す
            correction = reviewer.review_and_suggest_correction(title, base64_image, scene_graph)

            # c. 修正案に基づき、シーングラフを更新してスクリプトを再生成
            if correction.get("status") == "revision_needed":
                print("  [Planner] 修正案に基づき、シーングラフを更新します。")
                # 改善履歴に修正内容を記録
                refinement_history.append({
                    "sub_scene": title,
                    "feedback": correction.get("feedback"),
                    "original_graph": scene_graph,
                    "change": correction.get("suggested_change"),
                })

                # --- シーングラフの修正ロジック ---
                # ここでは簡略化のため、既存のrelationの引数を更新する処理を実装
                change = correction["suggested_change"]
                target = correction["target_relation"]
                if change["action"] == "update_args":
                    for relation in scene_graph.get("relations", []):
                        # 型とアセットが一致する関係性を探す
                        if relation["type"] == target["type"] and \
                           set(relation["involved_assets"]) == set(target["involved_assets"]):
                            print(f"    - Relation '{target['type']}' の引数を {relation.get('args', {})} から {change['new_args']} に更新。")
                            relation["args"] = change["new_args"]
                            break
                # (ここで 'add_relation' や 'remove_relation' の処理も追加可能)
                
                print("  [Coder] 更新されたシーングラフからスクリプトを再生成します。")
                # 更新されたシーングラフでスクリプトを再生成
                script = coder.generate_script_with_solver(scene_graph, sub_scene_data["asset_list"])
                final_scripts[i]["script"] = script # 最新のスクリプトに更新
            else:
                # 修正が不要な場合はループを抜ける
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