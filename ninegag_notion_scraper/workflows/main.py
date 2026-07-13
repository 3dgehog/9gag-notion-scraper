import logging

from ..args import Arguments
from ..use_cases.meme import GetPostMemes, SavePostMeme
from ..use_cases.notifications import SendNotification

logger = logging.getLogger('app.uc')


class ScrapeNineGagToNotionAndStorageWorkflow:
    """Use case for scraping memes from 9GAG and saving to Notion
    and File Storage"""

    def __init__(
        self,
        get_post_memes: GetPostMemes,
        save_to_notion: SavePostMeme,
        save_to_filestorage: SavePostMeme,
        send_notification: SendNotification,
        args: Arguments
    ) -> None:
        self.get_post_memes = get_post_memes
        self.save_to_notion = save_to_notion
        self.save_to_filestorage = save_to_filestorage
        self.send_notification = send_notification
        self.args = args

    def execute(self) -> None:
        """Execute the scraping workflow"""
        logger.debug("Starting to scrape memes from 9GAG")

        self.count_memes_saved_in_notion = 0
        self.count_memes_saved_in_filestorage = 0

        try:
            for memes in self.get_post_memes.get_memes():
                should_stop = self._process_meme_batch(memes)
                if should_stop:
                    return
        except Exception as e:
            self._handle_error(e)

    def _process_meme_batch(self, memes) -> bool:
        """Process a batch of memes. Returns True if scraping should stop."""
        for meme in memes:
            exists_file = self._save_to_storage(
                meme,
                self.save_to_filestorage,
                "File Storage"
            )
            exists_notion = self._save_to_storage(
                meme,
                self.save_to_notion,
                "Notion DB"
            )

            if not exists_file:
                self.count_memes_saved_in_filestorage += 1
            if not exists_notion:
                self.count_memes_saved_in_notion += 1

            if exists_file or exists_notion:
                self._log_existing_meme(meme, exists_file, exists_notion)
                self._notify_stop()
                return True

        return False

    def _save_to_storage(self, meme, save_handler, storage_name: str) -> bool:
        """Save meme to storage. Returns True if meme already exists."""
        exists = save_handler.meme_exists(meme)

        if self.args.skip_existing and exists:
            logger.info(
                f"Meme ID {meme.post_id} was skipped in '{storage_name}' "
                "because it already exists"
            )
            return True

        if exists:
            logger.info(
                f"Meme ID {meme.post_id} already exists in {storage_name}")
            return True

        save_handler.save_meme(meme)
        return False

    def _log_existing_meme(self,
                           meme, exists_file: bool,
                           exists_notion: bool) -> None:
        """Log information about existing meme."""
        if exists_file and exists_notion:
            logger.debug(
                f"Meme ID {meme.post_id} already exists in both "
                "File Storage and Notion DB"
            )
        elif exists_file:
            logger.debug(
                f"Meme ID {meme.post_id} already exists in File Storage")
        elif exists_notion:
            logger.debug(f"Meme ID {meme.post_id} already exists in Notion DB")

    def _notify_stop(self) -> None:
        """Send notification about scraping stop."""
        if not self.send_notification.is_setup:
            return

        self.send_notification.send(
            message=(
                "Notion scraper ran successfully. "
                f"{self.count_memes_saved_in_notion} "
                "memes saved in Notion and "
                f"{self.count_memes_saved_in_filestorage} memes "
                "saved in File Storage."
            )
        )

    def _handle_error(self, error: Exception) -> None:
        """Handle scraping errors."""
        logger.error(f"An error occurred during scraping: {error}")

        if self.send_notification.is_setup:
            self.send_notification.send(
                message=f"An error occurred during scraping: {error}"
            )
