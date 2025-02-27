from .. import enums
from .base import BaseModel
from .profile import Badge


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