# modules/asset_retriever.py
"""
Step 1: アセット選定 (Asset Retrieval)
論文の Section 2.1 に対応。
"""
from typing import Dict
from utils.llm_utils import call_llm
from utils.config import ASSET_MODEL

def retrieve_assets(user_query: str) -> Dict[str, str]:
    """
    ユーザーのクエリから、シーンに必要なアセットのリストと説明をLLMで生成する。
    """
    print("\n--- [Step 1] 🖼️ アセット選定 ---")
    prompt = f"""
    3Dシーンを生成するため、以下のクエリに登場すべきアセットのリストと、それぞれの詳細な視覚的説明を生成してください。
    クエリ: "{user_query}"
    
    出力はJSON形式の辞書で、キーはアセット名、バリューはその説明とします。
    例: {{ "Slum house": "壊れたタイルと汚れた壁を持つ、荒廃した建物", "Hunter": "13-15歳くらいの、革の服を着た少女ハンター" }}
    ```json
    {{
        "asset_name_1": "description_1",
        "asset_name_2": "description_2"
    }}
    ```
    """
    assets_with_desc = call_llm(ASSET_MODEL, prompt)
    
    # この後、実際には説明文を元にCLIP等で3Dモデルデータベースからアセットを検索・取得する
    print("✔️ 選定されたアセット:")
    for name, desc in assets_with_desc.items():
        print(f"  - {name}: {desc}")
    return assets_with_desc