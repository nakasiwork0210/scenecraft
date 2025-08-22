# modules/asset_retriever.py
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
def predict_asset_scales(assets_with_paths: Dict[str, str]) -> Dict[str, float]:
    """
    【新規追加】LLMを使い、アセットの現実的な高さをメートル単位で予測する。
    """
    print("  - LLMにアセットの現実的な高さの予測を依頼中...")
    
    asset_names = list(assets_with_paths.keys())
    
    prompt = f"""
    以下の3Dアセットリストがシーンに配置されます。
    各アセットの現実的な高さをメートル単位で予測し、Pythonの辞書形式で出力してください。
    例えば、人間なら1.7、車なら1.5のように常識的な値を設定してください。

    アセットリスト: {asset_names}

    出力形式の例:
    ```json
    {{
      "Slum house": 10.0,
      "Hunter": 1.65,
      "Street Lamp": 3.0
    }}
    ```
    """
    
    predicted_scales = call_llm(ASSET_MODEL, prompt)
    
    if not isinstance(predicted_scales, dict):
        print("    [Warning] 高さの予測に失敗しました。デフォルト値を使用します。")
        return {name: 1.0 for name in asset_names} # 失敗した場合はすべて1.0とする
        
    print("    ✔️ 高さの予測が完了しました。")
    return predicted_scales

def retrieve_assets(user_query: str) -> Dict[str, Dict]:
    """
    ユーザーのクエリからアセットを検索し、ファイルパスと予測された高さを返す。
    """
    print("\n--- [Step 1] 🖼️ アセット選定 (高精度) ---")
    
    # ... (LLMによるアセット説明の生成部分は変更なし) ...
    assets_to_find = call_llm(ASSET_MODEL, f"...") # promptは省略

    # ... (2段階検索によるファイルパスの取得部分は変更なし) ...
    retrieved_assets_paths = {}
    # ...
            
    # 【追加】取得したアセットのスケールを予測
    predicted_scales = predict_asset_scales(retrieved_assets_paths)
    
    # 【変更】返り値にファイルパスとスケール(高さ)の両方を含める
    final_assets_info = {}
    for name, path in retrieved_assets_paths.items():
        final_assets_info[name] = {
            "file_path": path,
            "height": predicted_scales.get(name, 1.0) # 予測がなければデフォルト1.0
        }
        
    return final_assets_info

def find_best_asset_with_reranking(query_description: str, top_k: int = 10) -> Dict:
    """
    【改善点】テキストと画像の両方を用いて、最も一致するアセットを検索する。
    論文で言及されている2段階の検索プロセスを実装。
    """
    # 1. 検索クエリをベクトル化
    query_embedding = CLIP_MODEL.encode(query_description)
    
    # --- Stage 1: テキスト類似度による候補の絞り込み ---
    text_scores = []
    for asset in ASSET_DATABASE:
        score = np.dot(query_embedding, asset['text_embedding'])
        text_scores.append((score, asset))
    
    # スコアで降順にソートし、上位k件を取得
    text_scores.sort(key=lambda x: x[0], reverse=True)
    top_k_candidates = [asset for score, asset in text_scores[:top_k]]

    if not top_k_candidates:
        return None

    # --- Stage 2: 画像類似度による再ランク付け (Re-ranking) ---
    best_asset = None
    highest_image_score = -1

    print(f"    - テキスト検索で{len(top_k_candidates)}件の候補を発見。画像で再ランク付けを実行...")
    for candidate_asset in top_k_candidates:
        # 候補アセットの画像埋め込みとクエリのテキスト埋め込みで類似度を計算
        image_score = np.dot(query_embedding, candidate_asset['image_embedding'])
        
        if image_score > highest_image_score:
            highest_image_score = image_score
            best_asset = candidate_asset
            
    return best_asset

def retrieve_assets(user_query: str) -> Dict[str, str]:
    """
    ユーザーのクエリからアセットの説明をLLMで生成し、
    最も一致するアセットのファイルパスを返す。
    """
    print("\n--- [Step 1] 🖼️ アセット選定 (高精度) ---")
    
    prompt = f"""
    以下のクエリに必要なアセットのリストと、それぞれの詳細な視覚的説明をJSON辞書で生成してください。
    クエリ: "{user_query}"
    ```json
    {{ "asset_name_1": "description_1", "asset_name_2": "description_2" }}
    ```
    """
    assets_to_find = call_llm(ASSET_MODEL, prompt)
    
    if not isinstance(assets_to_find, dict):
        print("  [Warning] LLMから有効なアセットリストを取得できませんでした。")
        return {}

    retrieved_assets = {}
    print("✔️ 選定されたアセット:")
    for asset_name, description in assets_to_find.items():
        print(f"  - '{description}' を検索中...")
        
        # 【改善点】新しい2段階検索関数を呼び出す
        best_match = find_best_asset_with_reranking(description)
        
        if best_match:
            print(f"    ✅ 発見 (画像スコアで選定): {best_match['file_path']}")
            retrieved_assets[asset_name] = best_match['file_path']
        else:
            print(f"    ❌ 該当アセットが見つかりませんでした。")
            retrieved_assets[asset_name] = None
            
    return retrieved_assets