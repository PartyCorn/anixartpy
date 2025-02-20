from . import anix_images, models, errors
from .utils import ArticleBuilder
from typing import Union
import os
try:
    import requests
except ImportError:
    os.system("pip install requests")

class AnixartAPI:
    BASE_URL = "https://api.anixart.tv"

    def __init__(self, token: str):
        self.session = requests.Session()
        self.token = token
        anix_images.TOKEN = token
        self.session.headers.update({
            "User-Agent": "AnixartApp/1.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "API-Version": "v2"
        })
        self.session.params = {"token": token}

    def _get(self, endpoint):
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.get(url)
        return response.json()

    def _post(self, endpoint, data=None):
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.post(url, json=data)
        return response.json()
    
    def get_channel(self, channel_id: int) -> models.Channel:
        data = self._get(f"/channel/{channel_id}")
        if data["code"] == 0:
            return models.Channel(data["channel"], self)
        return None
    
    def create_article(self, channel_id: int, article_data: Union[ArticleBuilder, dict]):
        if isinstance(article_data, ArticleBuilder):
            article_data = article_data.build()
        response = self._post(f"/article/create/{channel_id}", article_data)
        if response["code"] == 0:
            return models.Article(response["article"], self)
        else:
            raise errors.ArticleCreateEditError(response["code"])
    
    def delete_article(self, article_id: int):
        response = self._post(f"/article/delete/{article_id}")
        return response
    
    def edit_article(self, article_id: int, article_data: Union[ArticleBuilder, dict]):
        if isinstance(article_data, ArticleBuilder):
            article_data = article_data.build()
        response = self._post(f"/article/edit/{article_id}", article_data)
        if response["code"] == 0:
            return models.Article(response["article"], self)
        else:
            raise errors.ArticleCreateEditError(response["code"])
