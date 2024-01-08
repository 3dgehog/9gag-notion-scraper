from ninegag_notion_scraper.app.entities.meme import Meme
from ninegag_notion_scraper.app.interfaces.repositories.meme \
    import SaveMemeRepo


class SaveMeme:
    def __init__(self, meme_repo: SaveMemeRepo) -> None:
        self.meme_repo = meme_repo

    def save_meme(self, meme: Meme):
        self.meme_repo.save_meme(meme)

    def meme_exists(self, meme: Meme) -> bool:
        return self.meme_repo.meme_exists(meme)
