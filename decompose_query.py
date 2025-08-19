import openai

def decompose_query(api_key: str, user_query: str) -> List[dict]:
    """
    LLMを使用してユーザーのクエリをサブシーンの計画に分解する。
    """
    openai.api_key = api_key
    
    prompt = f"""
    私はBlenderスクリプトを書いて、次のシーンを生成しようとしています: "{user_query}"
    
    このシーンを構築するための具体的な計画が必要です。
    段階的に考え、アセットをシーンに配置するための複数ステップの計画を提示してください。
    各ステップは、以下の形式で出力してください：
    
    layout_plan_1 = {{
        "title": "このステップの概要を示すタイトル",
        "asset_list": ["asset_name_1", "asset_name_2"],
        "description": "このステップ完了後の見た目に関する詳細な視覚的テキスト記述"
    }}
    
    環境的なアセットから始め、徐々に詳細なアセットを配置するように計画してください。
    layout_plan_1, layout_plan_2,... の形式でPython辞書のリストを返してください。
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # レスポンスからPython辞書のリストをパースする処理
    # (例: response.choices.message.content から正規表現やevalで抽出)
    parsed_plans = parse_llm_response(response.choices.message.content)
    return parsed_plans