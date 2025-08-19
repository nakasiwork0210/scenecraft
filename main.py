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
    
    # Step 5: 自己改善ループをシミュレート
    num_refinement_steps = 2
    for i, sub_scene_script in enumerate(run_result["final_scripts"]):
        script = sub_scene_script["script"]
        title = sub_scene_script["title"]
        
        for step in range(num_refinement_steps):
            print(f"\n>>> サブシーン '{title}' の自己改善ループ {step + 1}/{num_refinement_steps}")
            
            # a. スクリプトを実行してレンダリング (シミュレーション)
            image_path = f"output/rendered_image_subscene{i+1}_step{step}.png"
            blender_env.execute_blender_script(script, image_path)
            
            # b. レビューと修正
            base64_image = blender_env.get_base64_image(image_path)
            if base64_image:
                # 実際のVisionモデル呼び出しは高コストなため、ここではダミーの修正で代用
                # revised_script = reviewer.review_and_revise(title, base64_image, script)
                revised_script = script + f"\n# Revision {step+1}: Fixed alignment based on visual feedback."
                
                # 履歴を保存
                refinement_history.append({
                    "sub_scene": title,
                    "original_script": script,
                    "revised_script": revised_script
                })
                script = revised_script
    
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