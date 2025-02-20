from typing import Optional, List
from datetime import datetime
from . import errors


class BaseModel:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.__dict__})>"


class Channel(BaseModel):
    id: int
    title: str
    description: str
    cover: str
    avatar: str
    permission: int
    article_count: int
    subscriber_count: int
    is_blog: bool
    is_commenting_enabled: bool
    is_article_suggestion_enabled: bool
    is_verified: bool
    is_deleted: bool
    is_subscribed: bool
    is_blocked: bool
    is_creator: bool
    is_administrator_or_higher: bool

    def __init__(self, data: dict, api):
        super().__init__(data)
        self.api = api
        self.creation_date: datetime = datetime.fromtimestamp(data["creation_date"])
        self.last_update_date: datetime = datetime.fromtimestamp(data["last_update_date"])

    def update_settings(self, title: Optional[str] = None, description: Optional[str] = None, is_commenting_enabled: Optional[bool] = None, is_article_suggestion_enabled: Optional[bool] = None) -> dict:
        """Обновляет настройки канала."""
        payload = {
            "title": title or self.title,
            "description": description or self.description,
            "is_commenting_enabled": is_commenting_enabled or self.is_commenting_enabled,
            "is_article_suggestion_enabled": is_article_suggestion_enabled or self.is_article_suggestion_enabled
        }
        response = self.api._post(f"/channel/edit/{self.id}", payload)
        if response["code"] == 0:
            self.title = payload["title"]
            self.description = payload["description"]
            self.is_commenting_enabled = payload["is_commenting_enabled"]
            self.is_article_suggestion_enabled = payload["is_article_suggestion_enabled"]
        else:
            raise errors.ChannelCreateEditError(response["code"])
        return self


class PayloadBlock(BaseModel):
    id: str
    name: str
    type: str
    data: dict

    def __init__(self, data: dict):
        super().__init__(data)
        self.data = data.get("data", {})


class Payload(BaseModel):
    time: int
    blocks: List[PayloadBlock]
    version: str
    block_count: int

    def __init__(self, data: dict):
        super().__init__(data)
        self.blocks = [PayloadBlock(block) for block in data.get("blocks", [])]


class Article(BaseModel):
    id: int
    channel: Channel
    author: dict
    payload: Payload
    vote: int
    repost_article: Optional[dict]
    comment_count: int
    repost_count: int
    vote_count: int
    is_under_moderation: bool
    is_deleted: bool
    under_moderation_reason: Optional[str]

    def __init__(self, data: dict, api):
        super().__init__(data)
        self.api = api
        self.channel = Channel(data["channel"], api)
        self.payload = Payload(data["payload"])
        self.creation_date: datetime = datetime.fromtimestamp(data["creation_date"])
        self.last_update_date: datetime = datetime.fromtimestamp(data["last_update_date"])