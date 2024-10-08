import argparse
from pydantic import BaseModel


class Arguments(BaseModel):
    debug: bool
    skip_existing: bool
    save_notion_meme_locally: bool
    ignore_existing: bool


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="9gag-notion-scraper")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--skip-existing", action='store_true')
    parser.add_argument("--ignore-existing", action='store_true')
    parser.add_argument("--save-notion-meme-locally", action='store_true')
    return parser


def get_args() -> Arguments:
    # return _build_parser().parse_args()
    args = _build_parser().parse_args()
    return Arguments(
        debug=args.debug,
        skip_existing=args.skip_existing,
        save_notion_meme_locally=args.save_notion_meme_locally,
        ignore_existing=args.ignore_existing
    )
