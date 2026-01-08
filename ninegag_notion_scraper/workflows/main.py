import logging

from ..args import Arguments
from ..use_cases.meme import GetPostMemes, SavePostMeme

logger = logging.getLogger('app.uc')


class ScrapeNineGagToNotionAndStorageWorkflow:
    """Use case for scraping memes from 9GAG and saving to Notion
    and File Storage"""

    def __init__(
        self,
        get_post_memes: GetPostMemes,
        save_to_notion: SavePostMeme,
        save_to_filestorage: SavePostMeme,
        args: Arguments
    ) -> None:
        self.get_post_memes = get_post_memes
        self.save_to_notion = save_to_notion
        self.save_to_filestorage = save_to_filestorage
        self.args = args

    def execute(self) -> None:
        """Execute the scraping workflow"""
        logger.debug("Starting to scrape memes from 9GAG")

        exists_filestorage = False
        exists_notion = False

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
                    logger.info(f"Meme ID {meme.post_id} already exists in "
                                f"{FILE_STORAGE_NAME}")
                    exists_filestorage = True
                else:
                    self.save_to_filestorage.save_meme(meme)

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
                    logger.info(f"Meme ID {meme.post_id} already exists in "
                                f"{NOTION_STORAGE_NAME}")
                else:
                    self.save_to_notion.save_meme(meme)

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
                                f"Meme ID {meme.post_id} already exists in "
                                f"{FILE_STORAGE_NAME}"
                            )
                        case [False, True]:
                            logger.debug(
                                f"Meme ID {meme.post_id} already exists in "
                                f"{NOTION_STORAGE_NAME}"
                            )
                    # Break both inner and outer loops
                    return
