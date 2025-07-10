from . import anix_images, models, errors
from .utils import ArticleBuilder, Style
from typing import Optional
import os
try:
    import requests
except ImportError:
    os.system("pip install requests")

class AnixartAPI:
    SERVERS = {
        'app': "https://api.anixart.app",
        'com': "https://api.anixartapp.com",
        'tv': "https://api.anixart.tv",
        'tv1': "https://api-s2.anixart.tv",
        'tv2': "https://api-s3.anixart.tv",
        'tv3': "https://api-s4.anixart.tv",
    }

    def __init__(self, token: Optional[str] = None, server: str = 'app'):
        """
        Инициализирует клиент Anixart API.

        Args:
            token (Optional[str]): Токен аутентификации для Anixart API. Если он предоставлен, будет использоваться для аутентифицированных запросов.
            server (str): Выбор сервера из доступных вариантов:
                - 'app' (по умолчанию) - основной сервер для России, anixart.app
                - 'com' - anixartapp.com
                - 'tv' - anixart.tv (недоступен в РФ)
                - 'tv1', 'tv2', 'tv3' - альтернативные зеркала
        """
        if server not in self.SERVERS:
            available = ", ".join(self.SERVERS.keys())
            raise ValueError(f"Неизвестный сервер. Доступные варианты: {available}")
        
        self.base_url = self.SERVERS[server]
        anix_images.API_INSTANCE = self
        self.session = requests.Session()
        self.token = token
        self.session.headers.update({
            'User-Agent': f'AnixartApp/9.0 BETA 1-24121614 (Android 12; SDK 31; arm64-v8a; Xiaomi M2102J20SG; ru)',
            'API-Version': 'v2',
            'sign': 'U1R9MFRYVUdOQWcxUFp4OENja1JRb8xjZFdvQVBjWDdYR07BUkgzNllxRWJPOFB3ZkhvdU9JYVJSR9g2UklRcVk1SW3QV8xjMzc2fWYzMmdmZDc2NTloN0g0OGUwN0ZlOGc8N0hjN0U9Y0M3Z1NxLndhbWp2d1NqeC3lcm9iZXZ2aEdsOVAzTnJX2zqZpyRX',
        })
        if token:
            self.session.params = {"token": token}

    def _get(self, endpoint) -> dict:
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url)
        return response.json()

    def _post(self, endpoint, data=None) -> dict:
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data)
        return response.json()
    
    def get_channel(self, channel_id: int) -> models.Channel:
        response = self._get(f"/channel/{channel_id}")
        if response["code"] == 0:
            return models.Channel(response["channel"], self)
        else:
            raise errors.ChannelGetError(response["code"])
    
    def get_article(self, article_id: int) -> models.Article:
        response = self._post(f"/article/{article_id}")
        if response["code"] == 0:
            return models.Article(response["article"], self)
        else:
            raise errors.ArticleGetError(response["code"])
    
    def get_article_suggestion(self, article_id: int) -> models.ArticleSuggestion:
        response = self._post(f"/article/suggestion/{article_id}")
        if response["code"] == 0:
            return models.ArticleSuggestion(response["articleSuggestion"], self)
        else:
            raise errors.ArticleGetError(response["code"])
    
    def get_latest_article_id(self) -> int:
        response = self._get(f"/article/latest")
        if response["code"] == 0:
            return response["articleId"]
        else:
            raise errors.AnixartError(response["code"], "Не удалось получить ID последнего поста.")
    
    def get_latest_article(self) -> models.Article:
        return self.get_article(self.get_latest_article_id())
