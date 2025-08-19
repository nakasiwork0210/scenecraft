# utils.py
"""
補助的な関数を定義するモジュール
"""
import json
import re

def parse_llm_response_to_json(response_text: str) -> dict:
    """LLMのテキスト応答からJSONオブジェクトを抽出する。"""
    # マークダウンのコードブロックを除去
    match = re.search(r"```(json)?\s*([\s\S]+?)\s*```", response_text)
    if match:
        response_text = match.group(2)
        
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # ここでエラー処理を行う（例: evalを使う、再度LLMに問い合わせるなど）
        print("Warning: Failed to parse JSON response.")
        return {}

def extract_python_code(response_text: str) -> str:
    """LLMのテキスト応答からPythonコードブロックを抽出する。"""
    match = re.search(r"```(python)?\s*([\s\S]+?)\s*```", response_text)
    if match:
        return match.group(2)
    return response_text # コードブロックが見つからない場合は全体を返す