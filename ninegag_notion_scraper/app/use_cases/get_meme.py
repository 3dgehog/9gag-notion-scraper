from validators import url as validate_url

from ninegag_notion_scraper.app.entities.meme import Meme
from ninegag_notion_scraper.app.interfaces.repositories.meme \
    import GetMemeRepo


class GetMeme:
    def __init__(self, memes_repo: GetMemeRepo) -> None:
        self.meme_repo = memes_repo

    def get_meme_from_url(self, url: str) -> Meme:
        if not validate_url(url):
            raise ValueError(f"URL is not valid {url}")

        return self.meme_repo.get_meme_from_url(url)
