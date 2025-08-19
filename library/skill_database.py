# library/skill_database.py
"""
学習したスキルをJSONデータベースに永続化するためのモジュール
"""
import json
import os
from typing import Dict

# データベースファイルのパス
DB_PATH = "library/skills_database.json"

def save_skills_to_db(skills_source_code: Dict[str, str]):
    """
    現在のスキルライブラリ（ソースコード）をJSONファイルに保存する。
    
    Args:
        skills_source_code: スキル名と関数のソースコードを格納した辞書。
    """
    print(f"[Database] 🧠 学習したスキルを '{DB_PATH}' に保存しています...")
    try:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(skills_source_code, f, indent=4, ensure_ascii=False)
        print("[Database] ✔️ 保存が完了しました。")
    except Exception as e:
        print(f"[Database] ❌ エラー: データベースへの保存に失敗しました - {e}")

def load_skills_from_db() -> Dict[str, str]:
    """
    JSONファイルから保存されたスキルライブラリ（ソースコード）を読み込む。
    
    Returns:
        スキル名と関数のソースコードを格納した辞書。
    """
    print(f"[Database] 📚 '{DB_PATH}' から学習済みスキルを読み込んでいます...")
    if not os.path.exists(DB_PATH):
        print("[Database] ℹ️ データベースファイルが見つかりません。デフォルトのスキルで起動します。")
        return {}
        
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            skills_source_code = json.load(f)
        print("[Database] ✔️ スキルの読み込みが完了しました。")
        return skills_source_code
    except Exception as e:
        print(f"[Database] ❌ エラー: データベースの読み込みに失敗しました - {e}")
        return {}