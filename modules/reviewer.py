# modules/reviewer.py
"""
Step 5: レビューと修正 (Critic-and-Revise)
論文の Section 2.3 の Self-Improvement に対応。
"""
from utils.llm_utils import call_vision_llm, parse_llm_response_to_json
from utils.config import REVIEWER_MODEL
from typing import Dict, Any

def review_and_suggest_correction(sub_scene_description: str, base64_image: str, scene_graph: Dict) -> Dict[str, Any]:
    """
    レンダリング画像を評価し、問題点があればシーングラフの修正案をJSON形式で返す。
    """
    print("\n--- [Step 5] 🧐 レビューと修正 (Inner-Loop) ---")
    
    # scene_graphをレビューしやすい形式に変換
    relations_str = "\n".join([f"- {r['type']} on {r['involved_assets']}" for r in scene_graph.get("relations", [])])

    prompt = f"""
    あなたは3Dシーンのレビュアーです。
    目的のシーン: "{sub_scene_description}"

    現在のシーングラフの関係性:
    {relations_str}

    提供されたレンダリング画像が、目的のシーンを正確に表現しているか評価してください。
    もし問題があれば、シーングラフを修正するための**具体的な修正案を1つだけ**JSON形式で出力してください。
    問題がなければ、 "status": "OK" とだけ返してください。

    修正案の形式:
    {{
      "status": "revision_needed",
      "feedback": "（画像から読み取れる具体的な問題点）",
      "target_relation": {{
        "type": "（修正対象の関係性の種類、例: parallelism）",
        "involved_assets": ["（関連するアセットのリスト）"]
      }},
      "suggested_change": {{
        "action": "（'update_args' or 'add_relation' or 'remove_relation'）",
        "new_args": {{ "（新しい引数、例: 'axis': 'y'）" }}
      }}
    }}
    
    例：家が平行に並んでいない場合
    {{
      "status": "revision_needed",
      "feedback": "Two 'Slum house' objects are not parallel to each other along the street.",
      "target_relation": {{
        "type": "parallelism",
        "involved_assets": ["Slum house_1", "Slum house_2"]
      }},
      "suggested_change": {{
        "action": "update_args",
        "new_args": {{ "axis": "y" }}
      }}
    }}
    """
    print("  GPT-4Vにレビューを依頼中...")
    # VisionモデルはJSONモードを直接サポートしていない場合が多いため、レスポンスをパースする
    response_text = call_vision_llm(REVIEWER_MODEL, prompt, base64_image) 
    correction_suggestion = parse_llm_response_to_json(response_text)

    if correction_suggestion.get("status") == "revision_needed":
        print(f"  ✔️ 修正案を受け取りました: {correction_suggestion.get('feedback')}")
    else:
        print("  ✔️ レビューの結果、問題は見つかりませんでした。")
        
    return correction_suggestion