import logging
from ninegag_notion_scraper.domain.entities.notification import Notification
from ninegag_notion_scraper.domain.interfaces.notification_provider import \
    NotificationProvider
import requests

logger = logging.getLogger('app.notifications')


class DiscordNotificationProvider(NotificationProvider):
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url
        self.is_setup = self._validate_webhook_url()

    def _validate_webhook_url(self) -> bool:
        is_validated = self.webhook_url != "" and (
                self.webhook_url.startswith("http://") or
                self.webhook_url.startswith("https://")
            )
        if not is_validated:
            logger.warning(
                "Discord webhook URL is not set up correctly, "
                "notifications will be disabled")
        return is_validated

    def send_notification(self, notification: Notification) -> None:
        if not self.is_setup:
            logger.warning(
                "Discord webhook URL is not set up correctly, notification "
                "not sent")
            return
        payload = {
            "content": notification.message
        }
        response = requests.post(self.webhook_url, json=payload)
        response.raise_for_status()
