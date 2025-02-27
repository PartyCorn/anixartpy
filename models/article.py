from datetime import datetime
from typing import Optional, List, Union
from .. import enums, errors, utils
from .base import BaseModel
from .channel import Channel
from .payload import Payload
from .user_vote import UserVote
from .comment import ArticleComment


class Article(BaseModel):
    id: int
    channel: Channel
    author: dict
    payload: Payload
    vote: enums.Vote
    repost_article: Optional["Article"]
    comment_count: int
    repost_count: int
    vote_count: int
    is_under_moderation: bool
    is_deleted: bool
    under_moderation_reason: Optional[str]

    def __init__(self, data: dict, api):
        super().__init__(data)
        self.__api = api
        self.channel = Channel(data["channel"], api)
        self.payload = Payload(data["payload"])
        self.creation_date: datetime = datetime.fromtimestamp(data["creation_date"])
        self.last_update_date: datetime = datetime.fromtimestamp(data["last_update_date"])
        self.repost_article = Article(data["repost_article"], self.__api) if data.get("repost_article") else {}
        self.vote = enums.Vote(data["vote"]) if data.get("vote") else None

    def edit(self, article_data: Union[utils.ArticleBuilder, dict], repost_article_id: Optional[int] = None) -> "Article":
        if isinstance(article_data, utils.ArticleBuilder):
            article_data = article_data.build()
        if repost_article_id is not None:
            article_data["repost_article_id"] = repost_article_id
        response = self.__api._post(f"/article/edit/{self.id}", article_data)
        if response["code"] == 0:
            self.payload = Payload(article_data["payload"])
            self.repost_article = Article(response["article"]["repost_article"], self.__api) if response["article"]["repost_article"] else None
        else:
            raise errors.ArticleCreateEditError(response["code"])
        return self

    def delete(self) -> "Article":
        response = self.__api._post(f"/article/delete/{self.id}")
        if response["code"] == 0:
            self.is_deleted = True
        else:
            raise errors.AnixartError(response["code"], "Статья не найдена.")
        return self
    
    def set_vote(self, vote: Union[enums.Vote, int]) -> dict:
        response = self.__api._get(f"/article/vote/{self.id}/{vote}")
        if response["code"] == 0:
            self.vote = enums.Vote(vote)
        else:
            raise errors.DefaultError(response["code"])
        return response

    def get_votes(self, page: int = 0) -> List[UserVote]:
        response = self.__api._get(f"/article/votes/{self.id}/{page}")
        if response["code"] == 0:
            return list([UserVote(vote) for vote in response["content"]])
        else:
            raise errors.AnixartError(response["code"], "Статья не найдена.")
    
    def get_reposts(self, page: int = 0) -> List["Article"]:
        response = self.__api._get(f"/article/reposts/{self.id}/{page}")
        if response["code"] == 0:
            return list([Article(repost, self.__api) for repost in response["content"]])
        else:
            raise errors.AnixartError(response["code"], "Статья не найдена.")
    
    def get_comments(self, sort: Union[enums.CommentSort, int] = enums.CommentSort.NEW, page: int = 0) -> List[ArticleComment]:
        response = self.__api._get(f"/article/comment/all/{self.id}/{page}?sort={sort}")
        if response["code"] == 0:
            return list([ArticleComment(comment, self.__api) for comment in response["content"]])
        else:
            raise errors.AnixartError(response["code"], "Статья не найдена.")