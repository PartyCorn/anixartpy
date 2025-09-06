from . import anix_images, models, errors
from .utils import ArticleBuilder, Style
from typing import Optional, Literal, Dict, Any
import os
try:
    import requests
except ImportError:
    os.system("pip install requests")

SERVERS_URL = "https://raw.githubusercontent.com/AnixHelper/pages/refs/heads/main/urls.json"

class AnixartAPI:
    def __init__(self, token: Optional[str] = None, auto_server: bool = True, server_region: Literal['default', 'ru', 'ua'] = 'default', base_url: Optional[str] = None):
        """
        Инициализирует клиент Anixart API.

        Args:
            token (Optional[str]): Токен аутентификации для Anixart API. Если он предоставлен, будет использоваться для аутентифицированных запросов.
            auto_server (bool): Автоматически получать сервер из GitHub
            server_region (str): Регион сервера (default, ru, ua)
            base_url (Optional[str]): Прямой URL API сервера
        """
        if base_url:
            self.base_url = base_url.rstrip('/')
        elif auto_server:
            servers_data = self._fetch_servers_data()
            if server_region not in servers_data:
                available = ", ".join(servers_data.keys())
                raise ValueError(f"Неизвестный регион сервера. Доступные варианты: {available}")
            
            server_config = servers_data[server_region]
            self.base_url = server_config['api_url'].rstrip('/')
            # should_use_mirror_urls можно использовать для дополнительной логики
        else:
            raise ValueError("Необходимо указать base_url или использовать auto_server=True")
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
    
    def _fetch_servers_data(self) -> Dict[str, Any]:
        """Получает данные о серверах из GitHub"""
        try:
            response = requests.get(SERVERS_URL, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Не удалось получить данные о серверах: {e}")
        except ValueError as e:
            raise ValueError(f"Неверный формат JSON данных о серверах: {e}")
    
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
