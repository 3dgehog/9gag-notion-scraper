from ninegag_notion_scraper.domain.entities.notification import Notification
from ninegag_notion_scraper.domain.interfaces.notification_provider import \
    NotificationProvider


class SendNotification:
    is_setup: bool

    def __init__(self,
                 notification_provider: NotificationProvider
                 ) -> None:
        self.notification_provider = notification_provider
        self.is_setup = self.notification_provider.is_setup

    def send(self, message: str) -> None:
        notification = Notification(message=message)
        self.notification_provider.send_notification(notification)
