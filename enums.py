from enum import IntEnum, StrEnum

class ChannelMemberPermission(IntEnum):
    MEMBER = 0
    ADMINISTRATOR = 1 
    OWNER = 2

class BadgeType(IntEnum):
    WEBP = 0
    JSON = 1

class Vote(IntEnum):
    NONE = 0
    DISLIKE = 1
    LIKE = 2

class QuoteAlignment(StrEnum):
    LEFT = "left"
    CENTER = "center"

class CommentSort(IntEnum):
    NEW = 1
    OLD = 2
    POPULAR = 3

class PrivilegeLevel(IntEnum):
    MEMBER = 0
    USER = 1
    EDITOR = 2
    MODERATOR = 3
    ADMINISTRATOR = 4
    HEAD_ADMINISTRATOR = 5
    DEVELOPER = 6

class FriendStatus(IntEnum):
    INCOMING = 0
    OUTGOING = 1
    FRIENDS = 2