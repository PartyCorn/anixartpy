from datetime import datetime
from typing import Optional, List
from .. import enums, errors, anix_images
from .base import BaseModel
from .profile import Badge


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
        self.creation_date: datetime = datetime.fromtimestamp(data["creation_date"]) if data.get("creation_date") else None
        self.last_update_date: datetime = datetime.fromtimestamp(data["last_update_date"]) if data.get("last_update_date") else None

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
    
    def set_avatar(self, file: str) -> "Channel":
        response = anix_images.upload_avatar(self.id, file)
        if response["code"] == 0:
            self.avatar = response["url"]
        else:
            raise errors.ChannelUploadCoverAvatarError(response["code"])
        return self
    
    def set_cover(self, file: str) -> dict:
        response = anix_images.upload_cover(self.id, file)
        if response["code"] == 0:
            self.cover = response["url"]
        else:
            raise errors.ChannelUploadCoverAvatarError(response["code"])