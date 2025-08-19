# modules/decomposer.py
"""
Step 2: シーンの分解 (Scene Decomposition)
論文の Section 2.1 に対応。
"""
from typing import List
from utils.llm_utils import call_llm
from utils.config import DECOMPOSER_MODEL

def decompose_query(user_query: str, asset_list: List[str]) -> List[dict]:
    """
    複雑なシーンのクエリを、処理しやすい複数のサブシーンに分解する。
    """
    print("\n--- [Step 2] 📝 シーン分解 ---")
    prompt = f"""
    以下のシーンを生成するため、具体的な計画を複数のステップに分けて提示してください。
    シーン: "{user_query}"
    使用可能なアセット: {asset_list}
    
    各ステップはJSONオブジェクトのリストとして、以下のキーを持つ形式で出力してください:
    - "title": ステップの概要 (例: "背景の街並みを設置")
    - "asset_list": このステップで配置するアセット名のリスト
    - "description": このステップ完了後の詳細な視覚的記述
    
    環境アセットから始め、徐々に詳細なアセットを追加する順序で計画してください。
    ```json
    [
        {{ "title": "...", "asset_list": [...], "description": "..." }},
        {{ "title": "...", "asset_list": [...], "description": "..." }}
    ]
    ```
    """
    decomposed_plan = call_llm(DECOMPOSER_MODEL, prompt)
    print("✔️ 生成された計画:")
    for i, scene in enumerate(decomposed_plan):
        print(f"  - ステップ {i+1}: {scene.get('title', 'N/A')}")
    return decomposed_plan