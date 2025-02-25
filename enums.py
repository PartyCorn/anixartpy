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