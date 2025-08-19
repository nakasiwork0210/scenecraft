# config.py
"""
設定を管理するモジュール
"""

# 使用するOpenAI APIのキー
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# 各処理で使用するLLMのモデル名
DECOMPOSER_MODEL = "gpt-4"
PLANNER_MODEL = "gpt-4"
REVIEWER_MODEL = "gpt-4-vision-preview"