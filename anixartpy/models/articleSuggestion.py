from datetime import datetime
from typing import Union, Optional, TYPE_CHECKING
from .. import utils, errors
from .payload import Payload

if TYPE_CHECKING:
    from .article import Article
    from .channel import Channel


class ArticleSuggestion:
    id: int
    channel: "Channel"
    author: dict
    payload: Payload
    is_under_moderation: bool
    is_deleted: bool
    under_moderation_reason: Optional[str]

    def __init__(self, data: dict, api):
        self.__api = api
        from .article import Article
        article = Article(data, api)
        for attr, value in article.__dict__.items():
            setattr(self, attr, value)

    def edit(self, article_data: Union[utils.ArticleBuilder, dict]) -> "ArticleSuggestion":
        if isinstance(article_data, utils.ArticleBuilder):
            article_data = article_data.build(channel_id=self.channel.id, is_suggestion=True, is_edit_mode=True)
        response = self.__api._post(f"/article/suggestion/edit/{self.id}", article_data)
        if response["code"] == 0:
            self.payload = Payload(article_data["payload"])
        else:
            raise errors.ArticleCreateEditError(response["code"])
        return self

    def delete(self) -> "ArticleSuggestion":
        response = self.__api._post(f"/article/suggestion/delete/{self.id}")
        if response["code"] == 0:
            self.is_deleted = True
        else:
            raise errors.ArticleSuggestionDeleteError(response["code"])
        return self

    def publish(self) -> "ArticleSuggestion":
        response = self.__api._post(f"/article/suggestion/publish/{self.id}")
        if response["code"] == 0:
            self.creation_date = int(datetime.now().timestamp())
        else:
            raise errors.ArticleSuggestionPublishError(response["code"])
        return self

    def set_vote(self, *args, **kwargs):
        raise NotImplementedError("Voting not available for article suggestions")

    def get_votes(self, *args, **kwargs):
        raise NotImplementedError("Getting votes not available for article suggestions")

    def get_reposts(self, *args, **kwargs):
        raise NotImplementedError("Getting reposts not available for article suggestions")

    def get_comments(self, *args, **kwargs):
        raise NotImplementedError("Getting comments not available for article suggestions")