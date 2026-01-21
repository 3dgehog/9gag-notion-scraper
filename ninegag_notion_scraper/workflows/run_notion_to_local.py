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

        filter = self._get_notion_filter()

        for memes in self.notion_get.get_memes(filter=filter):
            should_stop = self._process_meme_batch(memes)
            if should_stop:
                logger.debug("Loop stopped by evaluate_storage")
                break

    def _get_notion_filter(self) -> dict:
        """Get the filter for Notion query."""
        return {
            "property": "Tags",
            "multi_select": {
                "does_not_contain": "Meme404"
            }
        }

    def _process_meme_batch(self, memes) -> bool:
        """Process a batch of memes. Returns True if processing should stop."""
        for meme in memes:
            should_stop = self._process_single_meme(meme)
            if should_stop:
                return True
        return False

    def _process_single_meme(self, meme) -> bool:
        """Process a single meme. Returns True if processing should stop."""
        if self.file_storage.meme_exists(meme):
            logger.info(f"Meme {meme.post_id} already exists")
            return False

        logger.info(f"Meme {meme.post_id} doesn't exists locally")

        loaded_meme = self._load_meme_from_ninegag(meme)
        if loaded_meme is None:
            return False

        return self._save_and_check_stop(loaded_meme)

    def _load_meme_from_ninegag(self, meme):
        """Load meme from 9GAG. Returns None if meme doesn't exist."""
        try:
            return self.ninegag.get_meme_from_url(meme.post_url)
        except Meme404:
            logger.info(
                f"skipping Meme ID {meme.post_id} because it "
                "doesn't exist anymore"
            )
            self.notion_update.update_meme(meme.id, tags=['Meme404'])
            return None

    def _save_and_check_stop(self, meme) -> bool:
        """Save meme and check if processing should stop.
        Returns True to stop.
        """
        storage_name = self.file_storage.__class__.__name__
        exists = self.file_storage.meme_exists(meme)

        if self.args.skip_existing and exists:
            logger.info(
                f"Meme ID {meme.post_id} was skipped in '{storage_name}' "
                "because it already exists"
            )
            return False

        if exists:
            logger.debug(
                f"Stopping: Meme ID {meme.post_id} already exists in "
                f"{storage_name} and ignore_existing is False"
            )
            return True

        self.file_storage.save_meme(meme)
        return False
