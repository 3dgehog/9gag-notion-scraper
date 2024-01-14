from notion_client import Client as NotionClient


from .cli import Arguments
from .env import Environments


def main(args: Arguments, envs: Environments):
    from .infrastructure.meme_notion.get_memes import NotionGetMemes

    notion = NotionGetMemes(NotionClient(
        auth=envs.NOTION_TOKEN), envs.NOTION_DATABASE)

    notion.get_memes()
