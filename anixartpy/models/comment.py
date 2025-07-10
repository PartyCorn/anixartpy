from typing import Union, Optional, TYPE_CHECKING
from .. import enums, utils
from .base import BaseModel
from datetime import datetime

if TYPE_CHECKING:
    from .profile import Profile
    from .article import Article


class Comment(BaseModel):
    id: int
    message: str
    type: int  #  maybe 0 - comment, 1 - reply
    vote: enums.Vote
    parent_comment_id: Optional[int]
    vote_count: int
    likes_count: int
    reply_count: int
    is_spoiler: bool
    is_edited: bool
    is_deleted: bool
    is_reply: bool
    can_like: bool

    def __init__(self, data: dict, api):
        super().__init__(data)
        self.__api = api
        from .profile import Profile
        self.author = self.profile = Profile(data["author"], api)
        self.timestamp = datetime.fromtimestamp(data["timestamp"])
        self.text = self.message

    def edit(self, message: str) -> "Comment":
        return

    def delete(self) -> dict:
        return

    def set_vote(self, vote: Union[enums.Vote, int]) -> dict:
        return


class ArticleComment(Comment):
    article: "Article"
    
    def __init__(self, data: dict, api):
        super().__init__(data, api)
        from .article import Article
        self.article = Article(data["article"], api)