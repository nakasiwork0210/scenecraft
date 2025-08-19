# SceneCraft: An LLM Agent for Synthesizing 3D Scenes

このプロジェクトは、論文「SceneCraft: An LLM Agent for Synthesizing 3D Scenes as Blender Code」で提案されたアーキテクチャを完全に実装したものです。

ユーザーのテキスト入力から3Dシーンを生成するだけでなく、生成プロセスを通じて自律的に学習し、自身のスキルを進化させる**デュアルループ（Dual-Loop）**の仕組みを特徴としています。

## 🚀 プロジェクト構造

- **`main.py`**: 全体のワークフローを実行するメインスクリプトです。
- **`agent.py`**: SceneCraftエージェントの頭脳となるクラスです。
- **`modules/`**: エージェントの各思考プロセス（アセット選定、計画、コーディングなど）をカプセル化したモジュール群です。
- **`library/`**: 進化するスキルライブラリと、アセットのデータ構造を格納します。
- **`utils/`**: 設定ファイルやBlenderのシミュレーターなど、補助的なツールを含みます。

## ⚙️ 実行前の準備

1.  **OpenAI APIキーの設定**:
    `utils/config.py` ファイルを開き、`OPENAI_API_KEY`にご自身のAPIキーを設定してください。

    ```python
    # utils/config.py
    OPENAI_API_KEY = "sk-YourOwnSecretApiKey"
    ```

2.  **必要なライブラリのインストール**:
    ```bash
    pip install openai numpy
    ```

## ▶️ 実行方法

プロジェクトのルートディレクトリで以下のコマンドを実行します。

```bash
python main.py