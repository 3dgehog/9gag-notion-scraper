from validators import url as validate_url
from typing import Generator, List

from ninegag_notion_scraper.app.entities.meme import Meme
from ninegag_notion_scraper.app.interfaces.repositories.meme \
    import GetMemeRepo
from ninegag_notion_scraper.app.interfaces.repositories.meme \
    import SaveMemeRepo
from ninegag_notion_scraper.app.interfaces.repositories.meme \
    import GetMemesRepo


class GetMemes:
    def __init__(self, memes_repo: GetMemesRepo) -> None:
        self.memes_repo = memes_repo

    def get_memes(self) -> Generator[List[Meme], None, None]:
        while not self.memes_repo.at_end:
            memes_entities = self.memes_repo.get_memes()

            yield memes_entities

            self.memes_repo.next()


class GetMeme:
    def __init__(self, memes_repo: GetMemeRepo) -> None:
        self.meme_repo = memes_repo

    def get_meme_from_url(self, url: str) -> Meme:
        if not validate_url(url):
            raise ValueError(f"URL is not valid {url}")

        return self.meme_repo.get_meme_from_url(url)


class SaveMeme:
    def __init__(self, meme_repo: SaveMemeRepo) -> None:
        self.meme_repo = meme_repo

    def save_meme(self, meme: Meme):
        self.meme_repo.save_meme(meme)

    def meme_exists(self, meme: Meme) -> bool:
        return self.meme_repo.meme_exists(meme)
