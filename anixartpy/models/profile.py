from typing import Optional, List
from .. import enums
from .base import BaseModel
from datetime import datetime, timedelta


class Badge(BaseModel):
    id: Optional[int]
    name: Optional[str]
    type: Optional[enums.BadgeType]
    url: Optional[str]

    def __init__(self, id: Optional[int], name: Optional[str], type: Optional[int], url: Optional[str]):
        super().__init__({"id": id, "name": name, "type": enums.BadgeType(type) if type else None, "url": url})


class Role(BaseModel):
    id: int
    name: str
    color: str

    def __init__(self, data: dict):
        super().__init__(data)


class Socials(BaseModel):
    def __init__(self, vk: Optional[str], telegram: Optional[str], instagram: Optional[str], tiktok: Optional[str], discord: Optional[str]):
        super().__init__({"vk": vk, "telegram": telegram, "instagram": instagram, "tiktok": tiktok, "discord": discord})


class Stats(BaseModel):
    def __init__(self, watching_count: int, plan_count: int, completed_count: int, hold_on_count: int, dropped_count: int, favorite_count: int, watched_episode_count: int, watched_time: timedelta):
        super().__init__({"watching_count": watching_count, "plan_count": plan_count, "completed_count": completed_count, "hold_on_count": hold_on_count, "dropped_count": dropped_count, "favorite_count": favorite_count, "watched_episode_count": watched_episode_count, "watched_time": watched_time})


class Counters(BaseModel):
    def __init__(self, comment_count: int, collection_count: int, video_count: int, friend_count: int, subscription_count: int):
        super().__init__({"comment_count": comment_count, "collection_count": collection_count, "video_count": video_count, "friend_count": friend_count, "subscription_count": subscription_count})


class Notifications(BaseModel):
    def __init__(self, release: bool, episode: bool, first_episode: bool, related_release: bool, report_process: bool, comment: bool, collection_comment: bool, article_comment: bool):
        super().__init__({"release": release, "episode": episode, "first_episode": first_episode, "related_release": related_release, "report_process": report_process, "comment": comment, "collection_comment": collection_comment, "article_comment": article_comment})


class WatchDynamic(BaseModel):
    id: int
    day: int
    count: int

    def __init__(self, data: dict):
        super().__init__(data)
        self.timestamp = datetime.fromtimestamp(data["timestamp"]) if data.get("timestamp") else None


class Profile(BaseModel):
    id: int
    login: str
    avatar: str
    status: str
    history: list
    votes: list
    ban_reason: Optional[str]
    is_private: bool
    is_sponsor: bool
    is_banned: bool
    is_perm_banned: bool
    is_bookmarks_transferred: bool
    is_sponsor_transferred: bool
    is_vk_bound: bool
    is_google_bound: bool
    is_verified: bool
    rating_score: int
    is_blocked: bool
    is_me_blocked: bool
    is_stats_hidden: bool
    is_counts_hidden: bool
    is_social_hidden: bool
    is_friend_requests_disallowed: bool
    is_online: bool
    
    def __init__(self, data: dict, api, is_my_profile: bool = False):
        super().__init__(data)
        self.__api = api
        self.badge = Badge(id=data["badge"]["id"], name=data["badge"]["name"], type=data["badge"]["type"], url=data["badge"]["image_url"])
        self.roles: List[Role] = [Role(role) for role in data["roles"]]
        self.last_activity_time = datetime.fromtimestamp(data["last_activity_time"]) if data.get("last_activity_time") else None
        self.register_date = datetime.fromtimestamp(data["register_date"]) if data.get("register_date") else None
        self.socials = Socials(vk=data["vk_page"], telegram=data["tg_page"], instagram=data["inst_page"], tiktok=data["tt_page"], discord=data["discord_page"])
        self.ban_expires = datetime.fromtimestamp(data["ban_expires"]) if data.get("ban_expires") else None
        self.privilege_level = enums.PrivilegeLevel(data["privilege_level"])
        self.stats = Stats(watching_count=data["watching_count"], plan_count=data["plan_count"], completed_count=data["completed_count"], hold_on_count=data["hold_on_count"], dropped_count=data["dropped_count"], favorite_count=data["favorite_count"], watched_episode_count=data["watched_episode_count"], watched_time=timedelta(seconds=data["watched_time"]))
        self.counters = Counters(comment_count=data["comment_count"], collection_count=data["collection_count"], video_count=data["video_count"], friend_count=data["friend_count"], subscription_count=data["subscription_count"])
        self.notifications = Notifications(release=data["is_release_type_notifications_enabled"], episode=data["is_episode_notifications_enabled"], first_episode=data["is_first_episode_notification_enabled"], related_release=data["is_related_release_notifications_enabled"], report_process=data["is_report_process_notifications_enabled"], comment=data["is_comment_notifications_enabled"], collection_comment=data["is_my_collection_comment_notifications_enabled"], article_comment=data["is_my_article_comment_notifications_enabled"])
        self.watch_dynamics: List[WatchDynamic] = [WatchDynamic(d) for d in data["watch_dynamics"]]
        self.friend_status = enums.FriendStatus(data["friend_status"]) if data.get("friend_status") else None
        self.sponsorship_expires = datetime.fromtimestamp(data["sponsorshipExpires"]) if data.get("sponsorshipExpires") else None
        self.is_my_profile = is_my_profile
    
    @staticmethod
    def check_banned(self) -> bool:
        return self.is_perm_banned or self.is_banned
    
    # get login history, change login, change avatar, change status, get badges, set badge, report, block, change private, get socials, change counters visibility, set up norifications, send friendship request, ignore this request
    # history, votes, view by roles
