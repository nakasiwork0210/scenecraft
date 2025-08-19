import base64

def review_and_revise_script(api_key: str, sub_scene_description: str, image_path: str, current_script: str) -> str:
    """
    GPT-4Vを使用してレンダリング画像を評価し、スクリプトを修正する。
    """
    openai.api_key = api_key
    
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    prompt = f"""
    あなたは3Dシーンのレビュアーです。
    以下のテキスト記述に基づいて、提供されたレンダリング画像がそれを正確に表現しているか評価してください。
    テキスト記述: "{sub_scene_description}"
    
    特に、不正確または欠落している空間的関係性を特定してください。
    まず、あなたのフィードバックをテキストで記述してください。
    次に、特定したエラーを修正するための、完全で実行可能なBlender Pythonスクリプトを
    ```python
   ...
    ```
    の形式で出力してください。
    
    現在のスクリプトは以下の通りです：
    {current_script}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        max_tokens=4096
    )
    
    # レスポンスから修正されたPythonスクリプト部分を抽出
    revised_script = extract_python_code(response.choices.message.content)
    return revised_script