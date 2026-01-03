from ninegag_notion_scraper.domain.entities.notification import Notification
from ninegag_notion_scraper.domain.interfaces.notification_provider import \
    NotificationProvider
import requests


class DiscordNotificationProvider(NotificationProvider):
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    def send_notification(self, notification: Notification) -> None:
        payload = {
            "content": notification.message
        }
        response = requests.post(self.webhook_url, json=payload)
        response.raise_for_status()
