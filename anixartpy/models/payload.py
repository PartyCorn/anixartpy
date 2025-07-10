from .base import BaseModel
from typing import List


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
        self.data = data
        self.blocks = [PayloadBlock(block) for block in data.get("blocks", [])]