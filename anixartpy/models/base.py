class BaseModel:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.__dict__})>"