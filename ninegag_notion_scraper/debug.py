from .app.use_cases.get_meme import GetMeme
from .app.use_cases.cookies import CookiesUseCase
from .infrastructure.meme_ninegag_scraper.page_single \
    import NineGagSinglePageScraperRepo
from .infrastructure.cookie_filestorage \
    import FileCookiesRepo

from .cli import Arguments
from .env import Environments
from .webdriver import WEB_DRIVER


def main(args: Arguments, envs: Environments):
    ninegag_scraper = NineGagSinglePageScraperRepo(
        envs.NINEGAG_USERNAME, envs.NINEGAG_PASSWORD,
        WEB_DRIVER, CookiesUseCase(FileCookiesRepo()))

    with ninegag_scraper:
        UC = GetMeme(ninegag_scraper)

        meme = UC.get_meme_from_url("https://9gag.com/gag/aOBmnq2")

        pass
