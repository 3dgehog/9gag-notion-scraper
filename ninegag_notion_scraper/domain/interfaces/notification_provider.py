from typing import Protocol
from ninegag_notion_scraper.domain.entities.notification import Notification


class NotificationProvider(Protocol):
    is_setup: bool

    def send_notification(self, notification: Notification) -> None:
        ...
