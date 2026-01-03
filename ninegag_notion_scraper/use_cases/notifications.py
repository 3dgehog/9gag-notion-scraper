from ninegag_notion_scraper.domain.entities.notification import Notification
from ninegag_notion_scraper.domain.interfaces.notification_provider import \
    NotificationProvider


class SendNotification:
    def __init__(self,
                 notification_provider: NotificationProvider
                 ) -> None:
        self.notification_provider = notification_provider

    def send(self, message: str) -> None:
        notification = Notification(message=message)
        self.notification_provider.send_notification(notification)
