from typing import Optional, List, Union
from datetime import datetime
from . import errors, enums, utils


class BaseModel:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.__dict__})>"


class Badge(BaseModel):
    id: Optional[int]
    name: Optional[str]
    type: Optional[enums.BadgeType]
    url: Optional[str]

    def __init__(self, id: Optional[int], name: Optional[str], type: Optional[int], url: Optional[str]):
        super().__init__({"id": id, "name": name, "type": None if not type else enums.BadgeType(type), "url": url})


class ChannelMember(BaseModel):
    id: int
    avatar: str
    login: str
    is_verified: bool
    channel_id: int
    block_reason: Optional[str]
    is_sponsor: bool
    permission: enums.ChannelMemberPermission
    is_blocked: bool
    is_perm_blocked: bool

    def __init__(self, data: dict, api):
        super().__init__(data)
        self.__api = api
        self.badge = Badge(id=None, name=data["badge_name"], type=data["badge_type"], url=data["badge_url"])
        self.permission = enums.ChannelMemberPermission(data["permission"])
        self.block_expire_date = datetime.fromtimestamp(data["block_expire_date"]) if data["block_expire_date"] else None
    
    def block(self, reason: str) -> dict:
        return

    def unblock(self) -> dict:
        return
    
    def set_permission(self, permission: enums.ChannelMemberPermission) -> dict:
        return


class Channel(BaseModel):
    id: int
    title: str
    description: str
    cover: str
    avatar: str
    permission: enums.ChannelMemberPermission
    article_count: int
    subscriber_count: int
    is_blog: bool
    blog_profile_id: Optional[int]
    is_commenting_enabled: bool
    is_article_suggestion_enabled: bool
    is_verified: bool
    is_deleted: bool
    is_subscribed: bool
    is_blocked: bool
    is_perm_blocked: bool
    block_reason: Optional[str]
    is_creator: bool
    is_administrator_or_higher: bool

    def __init__(self, data: dict, api):
        super().__init__(data)
        self.__api = api
        self.permission = enums.ChannelMemberPermission(data["permission"])
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
        response = self.__api._post(f"/channel/edit/{self.id}", payload)
        if response["code"] == 0:
            self.title = payload["title"]
            self.description = payload["description"]
            self.is_commenting_enabled = payload["is_commenting_enabled"]
            self.is_article_suggestion_enabled = payload["is_article_suggestion_enabled"]
        else:
            raise errors.ChannelCreateEditError(response["code"])
        return self
    
    def subscribe(self) -> dict:
        response = self.__api._post(f"/channel/subscribe/{self.id}")
        if response["code"] == 0:
            self.is_subscribed = True
        else:
            raise errors.ChannelSubscribeError(response["code"])
        return self
    
    def unsubscribe(self) -> dict:
        response = self.__api._post(f"/channel/unsubscribe/{self.id}")
        if response["code"] == 0:
            self.is_subscribed = False
        else:
            raise errors.ChannelUnsubscribeError(response["code"])
        return self
    
    def get_members(self, page: int = 0) -> List[ChannelMember]:
        response = self.__api._get(f"/channel/{self.id}/subscriber/all/{page}")
        if response["code"] == 0:
            return list([ChannelMember(member, self.__api) for member in response["content"]])
        else:
            raise errors.AnixartError(response["code"], "Канал не найден.")
    
    def get_administrators(self, page: int = 0) -> List[ChannelMember]:
        return
    
    def get_blocked_members(self, page: int = 0) -> List[ChannelMember]:
        return
    
    def set_avatar(self, file: str) -> dict:
        return
    
    def set_cover(self, file: str) -> dict:
        return


class UserVote(BaseModel):
    id: int
    vote: enums.Vote
    avatar: str
    login: str
    is_online: bool
    is_verified: bool
    is_sponsor: bool

    def __init__(self, data: dict):
        super().__init__(data)
        self.vote = enums.Vote(data["vote"])
        self.badge = Badge(id=data["badge_id"], name=data["badge_name"], type=data["badge_type"], url=data["badge_url"])


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
        self.repost_article = Article(data["repost_article"], self.__api) if data["repost_article"] else {}
        self.vote = enums.Vote(data["vote"])

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

    def delete(self) -> dict:
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

    def get_votes(self, page: int = 0):
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
    
    def get_comments(self, page: int = 0):
        return
