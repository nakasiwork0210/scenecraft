"""
OpenAI APIとの通信やレスポンス処理を補助するモジュール
"""
import openai
import json
import re
from typing import List, Dict, Any

from .config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def call_llm(model: str, prompt: str, is_json: bool = True) -> Any:
    """汎用的なLLM呼び出し関数"""
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        return parse_llm_response_to_json(content) if is_json else content
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return {} if is_json else ""

def call_vision_llm(model: str, prompt: str, base64_image: str) -> str:
    """Visionモデルを呼び出す関数"""
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ],
            max_tokens=4096
        )
        return extract_python_code(response.choices[0].message.content)
    except Exception as e:
        print(f"Error calling Vision LLM: {e}")
        return ""

def parse_llm_response_to_json(response_text: str) -> Any:
    """LLMのテキスト応答からJSONオブジェクトを抽出する"""
    match = re.search(r"```(json)?\s*([\s\S]+?)\s*```", response_text)
    if match:
        response_text = match.group(2)
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        print("Warning: Failed to parse JSON. Returning raw text.")
        return response_text

def extract_python_code(response_text: str) -> str:
    """LLMのテキスト応答からPythonコードブロックを抽出する"""
    match = re.search(r"```(python)?\s*([\s\S]+?)\s*```", response_text)
    if match:
        return match.group(2).strip()
    # コードブロックが見つからない場合、応答全体がコードであると仮定して返す
    return response_text.strip()