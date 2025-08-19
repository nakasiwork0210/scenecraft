import json
import numpy as np
from typing import Dict, List
from sentence_transformers import SentenceTransformer
from utils.llm_utils import call_llm
from utils.config import ASSET_MODEL

# --- グローバル変数としてモデルとDBを一度だけロード ---
print("[Asset Retriever] CLIPモデルとデータベースをロード中...")
CLIP_MODEL = SentenceTransformer('clip-ViT-B-32')
with open("library/asset_database.json", 'r', encoding='utf-8') as f:
    ASSET_DATABASE = json.load(f)
# 高速な検索のために、ベクトルをNumpy配列に変換しておく
for asset in ASSET_DATABASE:
    asset['image_embedding'] = np.array(asset['image_embedding'])
    asset['text_embedding'] = np.array(asset['text_embedding'])
print("[Asset Retriever] ✔️ ロード完了。")
# ----------------------------------------------------

def find_best_asset(query_description: str) -> Dict:
    """
    説明文に最も合うアセットをデータベースから検索する。
    """
    # 1. 検索クエリをベクトル化
    query_embedding = CLIP_MODEL.encode(query_description)
    
    best_score = -1
    best_asset = None
    
    # 2. データベース内の全アセットと類似度を比較
    for asset in ASSET_DATABASE:
        # コサイン類似度を計算 (A・B) / (|A| * |B|)
        # ここでは簡易的に内積で代用 (ベクトルは正規化済みと仮定)
        score = np.dot(query_embedding, asset['text_embedding'])
        
        if score > best_score:
            best_score = score
            best_asset = asset
            
    return best_asset

def retrieve_assets(user_query: str) -> Dict[str, str]:
    """
    ユーザーのクエリからアセットの説明をLLMで生成し、
    最も一致するアセットのファイルパスを返す。
    """
    print("\n--- [Step 1] 🖼️ アセット選定 ---")
    
    # (ここは変更なし) LLMにどのようなアセットが必要か考えさせる
    prompt = f"""
    以下のクエリに必要なアセットのリストと、それぞれの詳細な視覚的説明をJSON辞書で生成してください。
    クエリ: "{user_query}"
    ```json
    {{ "asset_name_1": "description_1", "asset_name_2": "description_2" }}
    ```
    """
    assets_to_find = call_llm(ASSET_MODEL, prompt)
    
    # 【ここからが新しい処理】
    retrieved_assets = {}
    print("✔️ 選定されたアセット:")
    for asset_name, description in assets_to_find.items():
        print(f"  - '{description}' を検索中...")
        best_match = find_best_asset(description)
        if best_match:
            print(f"    ✅ 発見: {best_match['file_path']}")
            # 結果を「アセット名: ファイルパス」の形式で保存
            retrieved_assets[asset_name] = best_match['file_path']
        else:
            print(f"    ❌ 該当アセットが見つかりませんでした。")
            retrieved_assets[asset_name] = None
            
    return retrieved_assets