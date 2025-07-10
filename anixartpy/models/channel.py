from datetime import datetime
from typing import Optional, Union, Iterator, TYPE_CHECKING
from .. import enums, errors, anix_images, utils
from .base import BaseModel
from .profile import Badge

if TYPE_CHECKING:
    from .article import Article
    from .articleSuggestion import ArticleSuggestion


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
        self.permission_creation_date = datetime.fromtimestamp(data["permission_creation_date"]) if data["permission_creation_date"] else None
        try:
            self.block_expire_date = datetime.fromtimestamp(data["block_expire_date"]) if data["block_expire_date"] else None
        except Exception:
            self.block_expire_date = data["block_expire_date"]
    
    def block(self, reason: str, expire_date: Union[datetime, int] = None, show_reason: bool = True) -> "ChannelMember":
        response = self.__api._post(f"/channel/{self.channel_id}/block/manage", {"target_profile_id": self.id, "is_blocked": True, "reason": reason, "expire_date": expire_date, "is_reason_showing_enabled": show_reason, "is_perm_blocked": expire_date == None})
        if response["code"] == 0:
            self.is_blocked = True
            self.block_reason = reason
            self.block_expire_date = expire_date
        else:
            raise errors.ChannelBlockError(response["code"])
        return self

    def unblock(self) -> "ChannelMember":
        response = self.__api._post(f"/channel/{self.channel_id}/block/manage", {"target_profile_id": self.id, "is_blocked": False, "is_perm_blocked": False})
        if response["code"] == 0:
            self.is_blocked = False
            self.is_perm_blocked = False
            self.block_reason = None
            self.block_expire_date = None
        else:
            raise errors.ChannelBlockError(response["code"])
        return self
    
    def set_permission(self, permission: Optional[Union[enums.ChannelMemberPermission, int]]) -> "ChannelMember":
        if permission == enums.ChannelMemberPermission.MEMBER:
            permission = None
        response = self.__api._post(f"/channel/{self.channel_id}/permission/manage", {"target_profile_id": self.id, "permission": permission})
        if response["code"] == 0:
            self.permission = enums.ChannelMemberPermission(permission or 0)
            self.permission_creation_date = datetime.now() if permission else None
            if permission == enums.ChannelMemberPermission.ADMINISTRATOR:
                self.is_blocked = False
                self.is_perm_blocked = False
                self.block_reason = None
                self.block_expire_date = None
        else:
            raise errors.ChannelPermissionManageError(response["code"])
        return self


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
    
    def create_article(self, article_data: Union[utils.ArticleBuilder, dict], repost_article_id: Optional[int] = None):
        from .article import Article
        if isinstance(article_data, utils.ArticleBuilder):
            article_data = article_data.build(channel_id=self.id)
        if repost_article_id is not None:
            article_data["repost_article_id"] = repost_article_id
        response = self.__api._post(f"/article/create/{self.id}", article_data)
        if response["code"] == 0:
            return Article(response["article"], self)
        else:
            raise errors.ArticleCreateEditError(response["code"])
    
    def suggest_article(self, article_data: Union[utils.ArticleBuilder, dict]):
        from .articleSuggestion import ArticleSuggestion
        if isinstance(article_data, utils.ArticleBuilder):
            article_data = article_data.build(channel_id=self.id, is_suggestion=True)
        response = self.__api._post(f"/article/suggestion/create/{self.id}", article_data)
        if response["code"] == 0:
            return ArticleSuggestion(response["article"], self)
        else:
            raise errors.ArticleCreateEditError(response["code"])
    
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
    
    def _fetch_suggestions_page(self, page: int) -> tuple[list["ArticleSuggestion"], int]:
        from .articleSuggestion import ArticleSuggestion
        response = self.__api._post(f"/article/suggestion/all/{page}", {"channel_id": self.id})
        if response["code"] == 0:
            items = [ArticleSuggestion(suggestion, self.__api) for suggestion in response["content"]]
            return items, response["total_page_count"]
        raise errors.AnixartError(response["code"], "Ошибка загрузки предложенных записей канала")

    def get_suggestions(self, page: Union[int, range, None] = None) -> Union[list["ArticleSuggestion"], Iterator["ArticleSuggestion"]]:
        return utils.paginate(lambda pg: self._fetch_suggestions_page(pg), page)
    
    def _fetch_members_page(self, page: int) -> tuple[list[ChannelMember], int]:
        response = self.__api._get(f"/channel/{self.id}/subscriber/all/{page}")
        if response["code"] == 0:
            items = [ChannelMember(member, self.__api) for member in response["content"]]
            return items, response["total_page_count"]
        raise errors.AnixartError(response["code"], "Ошибка загрузки участников канала")

    def get_members(self, page: Union[int, range, None] = None) -> Union[list[ChannelMember], Iterator[ChannelMember]]:
        return utils.paginate(lambda pg: self._fetch_members_page(pg), page)

    def _fetch_administrators_page(self, permission: Union[enums.ChannelMemberPermission, int], page: int) -> tuple[list[ChannelMember], int]:
        response = self.__api._post(f"/channel/{self.id}/permission/all/{page}", {"permission": permission})
        if response["code"] == 0:
            items = [ChannelMember(member, self.__api) for member in response["content"]]
            return items, response["total_page_count"]
        raise errors.AnixartError(response["code"], "Ошибка загрузки администраторов")

    def get_administrators(self, 
                        permission: Union[enums.ChannelMemberPermission, int] = enums.ChannelMemberPermission.ADMINISTRATOR,
                        page: Union[int, range, None] = None) -> Union[list[ChannelMember], Iterator[ChannelMember]]:
        return utils.paginate(lambda pg: self._fetch_administrators_page(permission, pg), page)

    def _fetch_blocked_members_page(self, page: int) -> tuple[list[ChannelMember], int]:
        response = self.__api._get(f"/channel/{self.id}/block/all/{page}")
        if response["code"] == 0:
            items = [ChannelMember(member, self.__api) for member in response["content"]]
            return items, response["total_page_count"]
        raise errors.AnixartError(response["code"], "Ошибка загрузки заблокированных пользователей")

    def get_blocked_members(self, page: Union[int, range, None] = None) -> Union[list[ChannelMember], Iterator[ChannelMember]]:
        return utils.paginate(lambda pg: self._fetch_blocked_members_page(pg), page)
    
    def _fetch_articles_page(self, date_filter: Union[enums.DateFilter, int], page: int) -> tuple[list["Article"], int]:
        from .article import Article
        response = self.__api._post(f"/article/all/{page}", {"channel_id": self.id, "date": date_filter})
        if response["code"] == 0:
            items = [Article(article, self.__api) for article in response["content"]]
            return items, response["total_page_count"]
        raise errors.AnixartError(response["code"], "Ошибка загрузки статей канала")

    def get_articles(self, date_filter: Union[enums.DateFilter, int] = enums.DateFilter.NONE, page: Union[int, range, None] = None) -> Union[list["Article"], Iterator["Article"]]:
        return utils.paginate(lambda pg: self._fetch_articles_page(date_filter, pg), page)
    
    def set_avatar(self, file: str) -> "Channel":
        response = anix_images.upload_avatar(self.id, file, self.is_blog)
        print(response)
        if response["code"] == 0:
            self.avatar = response["url"] if not self.is_blog else response["avatar"]
        else:
            raise errors.ChannelUploadCoverAvatarError(response["code"])
        return self
    
    def set_cover(self, file: str) -> dict:
        response = anix_images.upload_cover(self.id, file)
        if response["code"] == 0:
            self.cover = response["url"]
        else:
            raise errors.ChannelUploadCoverAvatarError(response["code"])
        return self