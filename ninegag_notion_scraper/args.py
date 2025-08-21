import argparse
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    debug: bool = Field(default=False)
    skip_existing: bool = Field(default=False)
    save_notion_meme_locally: bool = Field(default=False)

    @classmethod
    def from_namespace(cls, ns):
        # Convert argparse.Namespace to dict and filter only model fields
        ns_dict = vars(ns)
        filtered = {
            name: ns_dict.get(name, field.default)
            for name, field in cls.model_fields.items()
        }
        return cls(**filtered)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="9gag-notion-scraper")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--skip-existing", action='store_true')
    parser.add_argument("--save-notion-meme-locally", action='store_true')
    return parser


def get_args() -> Arguments:
    args = _build_parser().parse_args()
    return Arguments.from_namespace(args)
