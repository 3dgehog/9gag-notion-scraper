import os
import logging

from .ninegag import NineGagBot
from . import notion

os.environ['PATH'] += r":/Users/maxence/Projects/9gag-notion-scraper"

START_STREAM = os.environ['START_STREAM']

logger = logging.getLogger('app')


def main():
    with NineGagBot() as bot:
        bot.landing_page()

        stream = int(START_STREAM)
        elements = None

        while True:

            # Waiting until next stream is detected or the spinner ends
            while True:
                elements = bot.get_elements_from_stream(stream)

                if elements:
                    for element in elements:
                        notion.add_gag(
                            element.name,
                            element.id,
                            element.url,
                            element.post_section,
                            element.cover_photo
                        )
                        elements = None
                        bot.scroll(sleep=0.1)
                        stream += 1
                    break

                if not bot.is_loader_spinning():
                    logger.info('Reached the bottom')
                    return

                bot.scroll(sleep=0.1)


if __name__ == '__main__':
    main()
