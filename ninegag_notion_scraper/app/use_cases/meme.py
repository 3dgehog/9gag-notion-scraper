import logging
from validators import url as validate_url
from typing import Generator, List, Optional

from ninegag_notion_scraper.app.entities.meme import DBMeme, PostMeme
from ninegag_notion_scraper.app.interfaces.repositories.meme \
    import GetMemeRepo, UpdateMemeRepo
from ninegag_notion_scraper.app.interfaces.repositories.meme \
    import SaveMemeRepo
from ninegag_notion_scraper.app.interfaces.repositories.meme \
    import GetPostMemesRepo, GetDBMemesRepo


logger = logging.getLogger('app.uc')


class GetPostMemes:
    def __init__(self, memes_repo: GetPostMemesRepo) -> None:
        self.memes_repo = memes_repo

    def get_memes(self) -> Generator[List[PostMeme], None, None]:
        while not self.memes_repo.at_end:
            memes_entities = self.memes_repo.get_memes()

            yield memes_entities

            self.memes_repo.next()


class GetPostMeme:
    def __init__(self, memes_repo: GetMemeRepo) -> None:
        self.meme_repo = memes_repo

    def get_meme_from_url(self, url: str) -> PostMeme:
        if not validate_url(url):
            raise ValueError(f"URL is not valid {url}")

        return self.meme_repo.get_meme_from_url(url)


class SavePostMeme:
    def __init__(self, meme_repo: SaveMemeRepo) -> None:
        self.meme_repo = meme_repo

    def save_meme(self, meme: PostMeme):
        self.meme_repo.save_meme(meme)

    def meme_exists(self, meme: PostMeme | DBMeme) -> bool:
        return self.meme_repo.meme_exists(meme)


class GetDBMemes:
    def __init__(self, memes_repo: GetDBMemesRepo) -> None:
        self.memes_repo = memes_repo

    def get_memes(self,
                  filter: Optional[dict] = None
                  ) -> Generator[List[DBMeme], None, None]:
        while not self.memes_repo.at_end:
            memes_entities = self.memes_repo.get_memes(filter=filter)

            yield memes_entities

            self.memes_repo.next()


class UpdateMeme:
    def __init__(self, meme_repo: UpdateMemeRepo) -> None:
        self.meme_repo = meme_repo

    def update_meme(self, id: str, tags: list):

        logger.debug(f"Meme from id: '{id}' updated tags to: {tags}")
        self.meme_repo.update_meme(id=id, tags=tags)
