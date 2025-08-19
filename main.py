# main.py
"""
SceneCraftエージェントを実行し、テキストから3Dシーン生成プロセスを実演する。
"""
from agent import SceneCraftAgent

def main():
    # 1. エージェントの初期化
    agent = SceneCraftAgent()
    
    # 2. ユーザーからのクエリ
    user_query = "a girl hunter walking in a slum village with fantasy creatures"
    print(f"ユーザーのクエリ: {user_query}\n")

    # 3. クエリをサブシーンに分解 (Step 2)
    sub_scenes = agent.decompose_query(user_query)
    print("--- 1. クエリの分解 ---")
    for i, scene in enumerate(sub_scenes):
        print(f"  ステップ {i+1}: {scene['title']}")
        print(f"    アセット: {scene['asset_list']}")
    print("\n")
    
    # --- 内部ループ (Inner-Loop) ---
    # 各サブシーンに対して処理を実行
    for i, sub_scene in enumerate(sub_scenes):
        print(f"--- 2. サブシーン {i+1} の処理: '{sub_scene['title']}' ---")
        
        # 4. シーングラフの構築 (Step 3)
        print("  シーングラフを構築中...")
        scene_graph = agent.plan_scene_graph(sub_scene['description'], sub_scene['asset_list'])
        print("  完了:", scene_graph)
        
        # 5. 初期スクリプトの生成 (Step 4)
        print("\n  初期スクリプトを生成中...")
        script = agent.generate_script(scene_graph, sub_scene['asset_list'])
        print("  完了:\n", script)
        
        # 6. 自己改善ループ (Step 5)
        # 実際の運用では、ここでスクリプトを実行して画像をレンダリングし、
        # その画像をエージェントにフィードバックしてスクリプトを改善する
        # このループを数回繰り返す
        
        # num_refinement_steps = 3
        # for step in range(num_refinement_steps):
        #     print(f"\n  自己改善ループ {step + 1}/{num_refinement_steps}")
        #     
        #     # a. スクリプトを実行してレンダリング (ダミー)
        #     # execute_blender_script(script) -> 'rendered_image.png'
        #     dummy_image_path = "path/to/your/rendered_image.png" # 要変更
        #     
        #     # b. レビューと修正
        #     print("    レンダリング結果をレビューし、スクリプトを修正中...")
        #     revised_script = agent.review_and_revise(sub_scene['description'], dummy_image_path, script)
        #     script = revised_script
        #     print("    修正後のスクリプト:\n", script)
            
    print("\n--- 全ての処理が完了しました ---")


if __name__ == "__main__":
    main()