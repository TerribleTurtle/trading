import pytest
from src.shadow_bot.adapters.webhooks.discord import DiscordAlerter

def test_discord_alerter_sends_alert(mocker):
    mock_post = mocker.patch("httpx.post")
    alerter = DiscordAlerter(webhook_url="http://fake-webhook")
    
    alerter.send_alert("Hello World")
    
    mock_post.assert_called_once_with(
        "http://fake-webhook",
        json={"content": "Hello World"},
        timeout=10.0
    )
