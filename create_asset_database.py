from sentence_transformers import SentenceTransformer
from PIL import Image
import os
import json

# 1. CLIPモデルをロード
print("CLIPモデルをロード中...")
model = SentenceTransformer('clip-ViT-B-32')
print("ロード完了。")

ASSET_DIR = "assets" # あなたのアセットが保存されているフォルダ
DB_PATH = "library/asset_database.json"
asset_database = []

# 2. 各アセットを処理
for root, _, files in os.walk(ASSET_DIR):
    for file in files:
        if file.lower().endswith(('.obj', '.fbx', '.glb')):
            asset_path = os.path.join(root, file)
            image_path = os.path.splitext(asset_path)[0] + ".png"

            if os.path.exists(image_path):
                print(f"{asset_path} を処理中...")
                
                # 3. 画像をベクトル化
                image = Image.open(image_path)
                image_embedding = model.encode(image).tolist() # JSON保存用にリストに変換

                # 4. アセットの説明文をベクトル化 (ファイル名から簡易的に生成)
                description = file.replace("_", " ").replace(".obj", "")
                text_embedding = model.encode(description).tolist()

                asset_database.append({
                    "description": description,
                    "file_path": asset_path,
                    "image_embedding": image_embedding,
                    "text_embedding": text_embedding
                })

# 5. データベースをJSONファイルとして保存
print(f"\nデータベースを {DB_PATH} に保存中...")
with open(DB_PATH, 'w', encoding='utf-8') as f:
    json.dump(asset_database, f, indent=4)
print("アセットデータベースの作成が完了しました。")