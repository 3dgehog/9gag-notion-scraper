import copy
from typing import Awaitable, List, Optional
from notion_client import Client
from ninegag_notion_scraper.app.entities.meme import DBMeme
from ninegag_notion_scraper.app.interfaces.meme_repo \
    import GetDBMemesRepo

from .base import NotionBase
from .converters import PageIDConverter, PostTitleConverter, PostIDConverter, \
    PostURLConverter, PostTagsConverter, PostCoverURLConverter, \
    TagsConverter, NoteConverter


class NotionGetMemes(NotionBase, GetDBMemesRepo):
    def __init__(self, client: Client, database_id: str) -> None:
        NotionBase.__init__(self, client, database_id)
        self.at_end = False
        self._next_cursor = None
        self._current_cursor = None
        self._has_more = None
        self._next_count = 0

    def get_memes(self, filter: Optional[dict]) -> List[DBMeme]:
        if self._current_cursor:
            if filter:
                query = self._client.databases.query(
                    self._db_id,
                    start_cursor=self._current_cursor,
                    filter=filter
                )
            else:
                query = self._client.databases.query(
                    self._db_id,
                    start_cursor=self._current_cursor
                )

        else:
            if filter:
                query = self._client.databases.query(self._db_id,
                                                     filter=filter)
            else:
                query = self._client.databases.query(self._db_id)

        assert not isinstance(query, Awaitable)
        pages: list = query.get('results')

        memes = []

        for page in pages:
            memes.append(DBMeme(
                post_title=PostTitleConverter.decode(page),
                post_id=PostIDConverter.decode(page),
                post_url=PostURLConverter.decode(page),
                post_tags=PostTagsConverter.decode(page),
                post_cover_photo_url=PostCoverURLConverter.decode(page),
                id=PageIDConverter.decode(page),
                note=NoteConverter.decode(page),
                tags=TagsConverter.decode(page)
            ))

        self._next_cursor = query['next_cursor']
        self._has_more = query['has_more']

        return memes

    def next(self) -> int:
        if not self._has_more:
            self.at_end = True
            return self._next_count

        self._current_cursor = copy.deepcopy(self._next_cursor)
        self._next_count += 1
        return self._next_count
