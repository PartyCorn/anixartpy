from datetime import datetime
from typing import Optional, List, Union, Iterator, TYPE_CHECKING
from .. import enums, errors, utils
from .base import BaseModel
from .payload import Payload
from .user_vote import UserVote

if TYPE_CHECKING:
    from .channel import Channel
    from .comment import ArticleComment


class Article(BaseModel):
    id: int
    channel: "Channel"
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
    contains_repost_article: bool

    def __init__(self, data: dict, api):
        super().__init__(data)
        self.__api = api
        from .channel import Channel
        self.channel = Channel(data["channel"], api)
        self.payload = Payload(data["payload"])
        self.creation_date: datetime = datetime.fromtimestamp(data["creation_date"])
        self.last_update_date: datetime = datetime.fromtimestamp(data["last_update_date"])
        self.repost_article = Article(data["repost_article"], self.__api) if data.get("repost_article") else None
        self.vote = enums.Vote(data["vote"]) if data.get("vote") else None

    def edit(self, article_data: Union[utils.ArticleBuilder, dict], repost_article_id: Optional[int] = None) -> "Article":
        if isinstance(article_data, utils.ArticleBuilder):
            article_data = article_data.build(channel_id=self.channel.id, is_edit_mode=True)
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

    def _fetch_votes_page(self, sort: enums.Sorting, page: int) -> tuple[list[UserVote], int]:
        response = self.__api._get(f"/article/votes/{self.id}/{page}?sort={sort}")
        if response["code"] == 0:
            items = [UserVote(vote) for vote in response["content"]]
            return items, response["total_page_count"]
        raise errors.AnixartError(response["code"], "Ошибка загрузки голосов")

    def get_votes(self, sort: enums.Sorting, page: Union[int, range, None] = None) -> Union[list[UserVote], Iterator[UserVote]]:
        return utils.paginate(lambda pg: self._fetch_votes_page(sort, pg), page)

    def _fetch_reposts_page(self, sort: enums.Sorting, page: int) -> tuple[list["Article"], int]:
        response = self.__api._get(f"/article/reposts/{self.id}/{page}?sort={sort}")
        if response["code"] == 0:
            items = [Article(repost, self.__api) for repost in response["content"]]
            return items, response["total_page_count"]
        raise errors.AnixartError(response["code"], "Ошибка загрузки репостов")

    def get_reposts(self, sort: enums.Sorting, page: Union[int, range, None] = None) -> Union[list["Article"], Iterator["Article"]]:
        return utils.paginate(lambda pg: self._fetch_reposts_page(sort, pg), page)
    
    def _fetch_comments_page(self, sort: enums.Sorting, page: int) -> tuple[list["ArticleComment"], int]:
        from .comment import ArticleComment
        response = self.__api._get(f"/article/comment/all/{self.id}/{page}?sort={sort}")
        if response["code"] == 0:
            items = [ArticleComment(comment, self.__api) for comment in response["content"]]
            return items, response["total_page_count"]
        raise errors.AnixartError(response["code"], "Ошибка загрузки комментариев")
    
    def get_comments(self, sort: enums.Sorting, page: Union[int, range, None] = 0) -> Union[list["ArticleComment"], Iterator["ArticleComment"]]:
        return utils.paginate(lambda pg: self._fetch_comments_page(sort, pg), page)