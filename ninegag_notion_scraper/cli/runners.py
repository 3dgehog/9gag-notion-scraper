"""Application runners for different modes"""

import logging
from selenium.webdriver.remote.webdriver import WebDriver
from notion_client import Client as NotionClient

from ..args import Arguments
from ..env import Environments
from ..use_cases.meme import GetDBMemes, \
    GetPostMeme, SavePostMeme, UpdateMeme
from ..use_cases.cookies import get_cookies
from ..domain.interfaces.repositories.cookie import CookieRepo
from ..adapters.repositories.meme_ninegag_scraper.page_single \
    import Meme404, NineGagSinglePageScraperRepo
from ..adapters.repositories.meme_notion.get_memes \
    import NotionGetMemes
from ..adapters.repositories.meme_notion import NotionSaveMeme
from ..adapters.repositories.meme_filestorage import FileStorageRepo

logger = logging.getLogger('app')


def run_notion_to_local(
    args: Arguments,
    envs: Environments,
    webdriver: WebDriver,
    cookie_repo: CookieRepo
):
    """Run the Notion to local file storage workflow"""
    notion_client = NotionClient(auth=envs.NOTION_TOKEN)
    notion_get = NotionGetMemes(notion_client, envs.NOTION_DATABASE)
    notion_update = NotionSaveMeme(notion_client, envs.NOTION_DATABASE)
    file_storage = FileStorageRepo(
        covers_path=envs.COVERS_PATH,
        memes_path=envs.MEMES_PATH,
        _selenium_cookies_func=lambda: get_cookies(cookie_repo)
    )
    ninegag = NineGagSinglePageScraperRepo(
        envs.NINEGAG_USERNAME,
        envs.NINEGAG_PASSWORD,
        webdriver,
        cookie_repo
    )
    memes_from_notion_to_save_locally(
        notion_get=GetDBMemes(notion_get),
        notion_update=UpdateMeme(notion_update),
        file_storage=SavePostMeme(file_storage),
        ninegag=GetPostMeme(ninegag),
        args=args
    )


def memes_from_notion_to_save_locally(
        notion_get: GetDBMemes,
        notion_update: UpdateMeme,
        file_storage: SavePostMeme,
        ninegag: GetPostMeme,
        args: Arguments
):
    """Process memes from Notion and save them locally"""
    logger.debug("Starting to scrape memes from Notion")

    filter = {
        "property": "Tags",
        "multi_select": {
            "does_not_contain": "Meme404"
        }
    }

    should_stop = False
    for memes in notion_get.get_memes(filter=filter):
        for meme in memes:
            if not file_storage.meme_exists(meme):
                logger.info(f"Meme {meme.post_id} doesn't exists locally")

                try:
                    loaded_meme = ninegag.get_meme_from_url(
                        meme.post_url)
                except Meme404:
                    logger.info(
                        f"skipping Meme ID {meme.post_id} because it "
                        "doesn't exist anymore")
                    notion_update.update_meme(meme.id, tags=['Meme404'])
                    continue

                # Inline the evaluate_storage logic for file_storage
                exists = file_storage.meme_exists(loaded_meme)
                if args.skip_existing and exists:
                    logger.info(
                        f"Meme ID {loaded_meme.post_id} was skipped "
                        f"in '{file_storage.__class__.__name__}' because it "
                        "already exists"
                    )
                    continue
                if exists:
                    should_stop = True
                    logger.debug(
                        f"Stopping: Meme ID {loaded_meme.post_id} "
                        "already exists in "
                        f"{file_storage.__class__.__name__} "
                        f"and ignore_existing is False"
                    )
                    break
                file_storage.save_meme(loaded_meme)
            else:
                logger.info(f"Meme {meme.post_id} already exists")
        if should_stop:
            logger.debug("Loop stopped by evaluate_storage")
            break
