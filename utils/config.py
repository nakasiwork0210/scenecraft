"""
設定を管理するモジュール
"""
import os

# TODO: ご自身のOpenAI APIキーを設定してください
# 環境変数から読み込むことを推奨します
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")

# 各処理で使用するLLMのモデル名
# 論文の記述に基づき、能力に応じてモデルを使い分けます
ASSET_MODEL = "gpt-4-turbo"
DECOMPOSER_MODEL = "gpt-4-turbo"
PLANNER_MODEL = "gpt-4-turbo"
CODER_MODEL = "gpt-4-turbo"
REVIEWER_MODEL = "gpt-4-vision-preview" # Visionモデル
LEARNER_MODEL = "gpt-4-turbo" # 自己進化のための高度な推論モデル
