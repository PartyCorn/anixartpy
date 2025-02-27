from . import anix_images, models, errors
from .utils import ArticleBuilder, Style
from typing import Union, Optional
import os
try:
    import requests
except ImportError:
    os.system("pip install requests")

__author__ = "PartyCorn"
__version__ = "0.3.0"

class AnixartAPI:
    BASE_URL = "https://api.anixart.tv"

    def __init__(self, token: str):
        self.session = requests.Session()
        self.token = token
        anix_images.TOKEN = token
        self.session.headers.update({
            'User-Agent': f'AnixartPy/{__version__} by PartyCorn-private (Android 12; SDK 31; arm64-v8a; iPhone 20 Pro Max; ru)',
            'API-Version': 'v2',
            'sign': 'U1R9MFRYVUdOQWcxUFp4OENja1JRb8xjZFdvQVBjWDdYR07BUkgzNllxRWJPOFB3ZkhvdU9JYVJSR9g2UklRcVk1SW3QV8xjMzc2fWYzMmdmZDc2NTloN0g0OGUwN0ZlOGc8N0hjN0U9Y0M3Z1NxLndhbWp2d1NqeC3lcm9iZXZ2aEdsOVAzTnJX2zqZpyRX',
        })
        self.session.params = {"token": token}

    def _get(self, endpoint) -> dict:
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.get(url)
        return response.json()

    def _post(self, endpoint, data=None) -> dict:
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.post(url, json=data)
        return response.json()
    
    def get_channel(self, channel_id: int) -> models.Channel:
        response = self._get(f"/channel/{channel_id}")
        if response["code"] == 0:
            return models.Channel(response["channel"], self)
        else:
            raise errors.ChannelGetError(response["code"])
    
    def create_article(self, channel_id: int, article_data: Union[ArticleBuilder, dict], repost_article_id: Optional[int] = None) -> models.Article:
        if isinstance(article_data, ArticleBuilder):
            article_data = article_data.build()
        if repost_article_id is not None:
            article_data["repost_article_id"] = repost_article_id
        response = self._post(f"/article/create/{channel_id}", article_data)
        if response["code"] == 0:
            return models.Article(response["article"], self)
        else:
            raise errors.ArticleCreateEditError(response["code"])
    
    def get_article(self, article_id: int) -> models.Article:
        response = self._post(f"/article/{article_id}")
        if response["code"] == 0:
            return models.Article(response["article"], self)
        else:
            raise errors.ArticleGetError(response["code"])
