def plan_scene_graph(api_key: str, sub_scene_description: str, asset_list: List[str]) -> dict:
    """
    LLMを使用してサブシーンのリレーショナル・シーングラフを構築する。
    """
    openai.api_key = api_key
    
    prompt = f"""
    与えられた記述とアセットリストに基づき、3Dシーンのリレーショナル二部グラフを構築するタスクです。
    シーン記述: "{sub_scene_description}"
    アセットリスト: {asset_list}
    
    アセット間の空間的・文脈的関係性（近接、整列、平行など）を特定し、
    以下の形式で構造化されたグラフを出力してください：
    
    {{
        "relations": [
            {{ "type": "Alignment", "involved_assets": ["house1", "house2", "house3"] }},
            {{ "type": "Proximity", "involved_assets": ["lamp1", "house1"] }}
        ]
    }}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # レスポンスからJSON形式のグラフ構造をパース
    parsed_graph = json.loads(response.choices.message.content)
    return parsed_graph