from typing import Generator, List
from ninegag_notion_scraper.app.entities.meme import Meme
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
