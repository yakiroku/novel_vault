import requests


class NocturneHelper:
    @staticmethod
    def request(url: str) -> requests.Response:
        # ブラウザから取得したクッキーをここに追加
        cookies = {
            "over18": "yes",  # 例: "session_id": "abcd1234"
            # 必要なクッキーをすべて追加
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        
        # クッキーをrequestsのgetに渡す
        return requests.get(url, headers=headers, cookies=cookies, timeout=10)