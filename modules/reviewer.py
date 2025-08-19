# modules/reviewer.py
"""
Step 5: レビューと修正 (Critic-and-Revise)
論文の Section 2.3 の Self-Improvement に対応。
"""
from utils.llm_utils import call_vision_llm
from utils.config import REVIEWER_MODEL

def review_and_revise(sub_scene_description: str, base64_image: str, current_script: str) -> str:
    """
    レンダリング画像を評価し、問題点があればスクリプトを修正する。
    """
    print("\n--- [Step 5] 🧐 レビューと修正 (Inner-Loop) ---")
    prompt = f"""
    あなたは3Dシーンのレビュアーです。
    テキスト記述: "{sub_scene_description}"
    
    提供されたレンダリング画像が、この記述を正確に表現しているか評価してください。
    特に、アセット間の空間関係（整列、近接、平行など）が不正確または欠落している点を特定してください。
    
    評価に基づき、問題を修正するための**完全で実行可能なBlender Pythonスクリプト**を
    ```python 
    ...
    ```
    の形式で出力してください。元のスクリプトの構造を維持し、必要な箇所のみを修正してください。

    現在のスクリプトは以下の通りです：
    {current_script}
    """
    print("  GPT-4Vにレビューを依頼中...")
    revised_script = call_vision_llm(REVIEWER_MODEL, prompt, base64_image)
    print("✔️ スクリプトが修正されました。")
    return revised_script