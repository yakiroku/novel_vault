import os

class EnvConfigLoader:
    """環境変数を安全に読み込むためのヘルパークラス"""

    @staticmethod
    def get_variable(key: str) -> str:
        """指定された環境変数を取得。存在しない場合は例外をスローする"""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"環境変数が設定されていない: {key}")
        return value
