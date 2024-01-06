import argparse


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="9gag-notion-scraper")
    parser.add_argument("--skip-existing", action='store_true')
    return parser


def get_args() -> argparse.Namespace:
    return _build_parser().parse_args()
