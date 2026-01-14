import logging

from ..args import Arguments
from ..use_cases.meme import GetDBMemes, GetPostMeme, SavePostMeme, UpdateMeme
from ..adapters.repositories.meme_ninegag_scraper.page_single import Meme404

logger = logging.getLogger('app.uc')


class NotionToLocalWorkflow:
    """Workflow for fetching memes from Notion and saving them locally"""

    def __init__(
        self,
        notion_get: GetDBMemes,
        notion_update: UpdateMeme,
        file_storage: SavePostMeme,
        ninegag: GetPostMeme,
        args: Arguments
    ) -> None:
        self.notion_get = notion_get
        self.notion_update = notion_update
        self.file_storage = file_storage
        self.ninegag = ninegag
        self.args = args

    def execute(self) -> None:
        """Execute the Notion to local workflow"""
        logger.debug("Starting to scrape memes from Notion")

        filter = {
            "property": "Tags",
            "multi_select": {
                "does_not_contain": "Meme404"
            }
        }

        should_stop = False
        for memes in self.notion_get.get_memes(filter=filter):
            for meme in memes:
                if not self.file_storage.meme_exists(meme):
                    logger.info(f"Meme {meme.post_id} doesn't exists locally")

                    try:
                        loaded_meme = self.ninegag.get_meme_from_url(
                            meme.post_url)
                    except Meme404:
                        logger.info(
                            f"skipping Meme ID {meme.post_id} because it "
                            "doesn't exist anymore")
                        self.notion_update.update_meme(meme.id, tags=['Meme404'])
                        continue

                    # Inline the evaluate_storage logic for file_storage
                    exists = self.file_storage.meme_exists(loaded_meme)
                    if self.args.skip_existing and exists:
                        logger.info(
                            f"Meme ID {loaded_meme.post_id} was skipped "
                            f"in '{self.file_storage.__class__.__name__}' because it "
                            "already exists"
                        )
                        continue
                    if exists:
                        should_stop = True
                        logger.debug(
                            f"Stopping: Meme ID {loaded_meme.post_id} "
                            "already exists in "
                            f"{self.file_storage.__class__.__name__} "
                            f"and ignore_existing is False"
                        )
                        break
                    self.file_storage.save_meme(loaded_meme)
                else:
                    logger.info(f"Meme {meme.post_id} already exists")
            if should_stop:
                logger.debug("Loop stopped by evaluate_storage")
                break
