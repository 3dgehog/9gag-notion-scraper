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

        exists_filestorage = False
        exists_notion = False
        count_memes_saved_in_notion = 0
        count_memes_saved_in_filestorage = 0

        try:
            for memes in self.get_post_memes.get_memes():
                for meme in memes:
                    # Check if the meme is already saved in File Storage
                    FILE_STORAGE_NAME = "File Storage"
                    exists_file = self.save_to_filestorage.meme_exists(meme)
                    if self.args.skip_existing and exists_file:
                        logger.info(
                            f"Meme ID {meme.post_id} was skipped "
                            f"in '{FILE_STORAGE_NAME}' because it "
                            "already exists"
                        )
                    elif exists_file:
                        logger.info(f"Meme ID {meme.post_id} already "
                                    f"exists in {FILE_STORAGE_NAME}")
                        exists_filestorage = True
                    else:
                        self.save_to_filestorage.save_meme(meme)
                        count_memes_saved_in_filestorage += 1

                    # Check if the meme is already saved in Notion
                    NOTION_STORAGE_NAME = "Notion DB"
                    exists_notion = self.save_to_notion.meme_exists(meme)
                    if self.args.skip_existing and exists_notion:
                        logger.info(
                            f"Meme ID {meme.post_id} was skipped "
                            f"in '{NOTION_STORAGE_NAME}' because it "
                            "already exists"
                        )
                    elif exists_notion:
                        exists_notion = True
                        logger.info(f"Meme ID {meme.post_id} already "
                                    f"exists in {NOTION_STORAGE_NAME}")
                    else:
                        self.save_to_notion.save_meme(meme)
                        count_memes_saved_in_notion += 1

                    if exists_filestorage or exists_notion:
                        match [exists_filestorage, exists_notion]:
                            case [True, True]:
                                logger.debug(
                                    f"Meme ID {meme.post_id} already exists "
                                    f"in both {FILE_STORAGE_NAME} and "
                                    f"{NOTION_STORAGE_NAME}"
                                )
                            case [True, False]:
                                logger.debug(
                                    f"Meme ID {meme.post_id} already "
                                    f"exists in {FILE_STORAGE_NAME}"
                                )
                            case [False, True]:
                                logger.debug(
                                    f"Meme ID {meme.post_id} already "
                                    f"exists in {NOTION_STORAGE_NAME}"
                                )
                        if self.send_notification.is_setup:
                            self.send_notification.send(
                                message=(
                                    "Scraping stopped: existing meme found. "
                                    f" {count_memes_saved_in_notion} memes "
                                    "saved in Notion and "
                                    f"{count_memes_saved_in_filestorage} "
                                    "memessaved in File Storage."
                                )
                            )
                        # Break both inner and outer loops
                        return
        except Exception as e:
            logger.error(f"An error occurred during scraping: {e}")
            if self.send_notification.is_setup:
                self.send_notification.send(
                    message=f"An error occurred during scraping: {e}"
                )
            return
