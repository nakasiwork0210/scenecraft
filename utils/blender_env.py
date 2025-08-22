# utils/blender_env.py
"""
Blender環境との連携を行うモジュール
"""
import os
import base64
import subprocess # subprocessモジュールを追加
import sys # sysモジュールを追加

# --- Blenderのパス設定 ---
# 環境に合わせてBlenderの実行可能ファイルへのパスを設定してください。
# 環境変数 `BLENDER_PATH` から読み込むか、直接指定します。
BLENDER_PATH = os.environ.get("BLENDER_PATH", "blender") # デフォルトは'blender'コマンド

def find_blender_executable():
    """OSに応じてBlenderの実行可能ファイルを探す（補助関数）"""
    if sys.platform == "win32":
        # Windowsの場合、一般的なインストール先を探す
        for path in ["C:\\Program Files\\Blender Foundation\\Blender\\blender.exe", "C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe"]:
            if os.path.exists(path):
                return path
    elif sys.platform == "darwin": # macOS
        if os.path.exists("/Applications/Blender.app/Contents/MacOS/Blender"):
            return "/Applications/Blender.app/Contents/MacOS/Blender"
    # Linuxや、PATHが通っている場合は'blender'でOK
    return "blender"

def execute_blender_script(script: str, output_image_path: str, asset_library_path: str) -> bool:
    """
    生成されたPythonスクリプトをバックグラウンドでBlenderに実行させ、画像をレンダリングする
    """
    global BLENDER_PATH
    if BLENDER_PATH == "blender": # パスがデフォルトのままなら探査
        BLENDER_PATH = find_blender_executable()

    print(f"\n[Blender] Blenderスクリプトを実行中 (using: {BLENDER_PATH})...")

    # 一時的なスクリプトファイルを作成
    script_path = "temp_blender_script.py"
    with open(script_path, "w", encoding="utf-8") as f:
        # スクリプトの先頭で、ライブラリへのパスを追加する
        # これにより、BlenderのPython環境がプロジェクトのモジュールをインポートできるようになる
        f.write("import sys\n")
        f.write(f"sys.path.append('{os.path.abspath('.')}')\n\n")
        # アセットのパスを渡すためのグローバル変数を設定
        f.write(f"ASSET_PATH = '{os.path.abspath(asset_library_path)}'\n\n")
        f.write(script)

    # Blenderをバックグラウンドモードで実行するコマンド
    # --background: GUIなしで実行
    # --python: 指定したPythonスクリプトを実行
    # -o: レンダリング結果の出力先
    # -f 1: 1フレーム目のみをレンダリング
    command = [
        BLENDER_PATH,
        "--background",
        "--python", script_path,
        "-o", os.path.abspath(output_image_path),
        "-f", "1"
    ]

    try:
        # コマンドを実行
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"[Blender] ✔️ レンダリングが完了し、画像を '{output_image_path}' に保存しました。")
        # print("[Blender Log]\n", process.stdout) # Blenderのログを出力
        return True
    except FileNotFoundError:
        print(f"[Blender] ❌ エラー: Blenderの実行可能ファイルが見つかりません。")
        print(f"  '{BLENDER_PATH}' が正しいパスか確認するか、環境変数 BLENDER_PATH を設定してください。")
        return False
    except subprocess.CalledProcessError as e:
        print(f"[Blender] ❌ エラー: Blenderスクリプトの実行に失敗しました。")
        print(f"  Return Code: {e.returncode}")
        print(f"  --- STDOUT ---\n{e.stdout}")
        print(f"  --- STDERR ---\n{e.stderr}")
        return False
    finally:
        # 一時ファイルを削除
        if os.path.exists(script_path):
            os.remove(script_path)

def get_base64_image(image_path: str) -> str:
    """
    画像ファイルをBase64エンコードする (変更なし)
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Warning: Image file not found at {image_path}")
        return ""