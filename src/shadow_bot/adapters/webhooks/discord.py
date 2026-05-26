import httpx

class DiscordAlerter:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        
    def send_alert(self, msg: str) -> None:
        httpx.post(self.webhook_url, json={"content": msg}, timeout=10.0)
