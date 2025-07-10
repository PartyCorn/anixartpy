import time
import uuid
from . import anix_images
from typing import Union, Optional, Iterator, Callable, Any, List


class Style:
    @staticmethod
    def bold(text: str) -> str:
        return f"<b>{text}</b>"

    @staticmethod
    def underline(text: str) -> str:
        return f"<u>{text}</u>"

    @staticmethod
    def italic(text: str) -> str:
        return f"<i>{text}</i>"

    @staticmethod
    def strike(text: str) -> str:
        return f"<s>{text}</s>"

    @staticmethod
    def link(text: str, url: str) -> str:
        return f'<a href="{url}">{text}</a>'


class ArticleBuilder:
    EDITOR_VERSION = "2.26.5"

    def __init__(self, channel_id: Optional[int] = None, request_delay: float = 0.25):
        self.channel_id = channel_id
        self.request_delay = request_delay
        self.payload = {
            "time": int(time.time() * 1000),
            "blocks": [],
            "version": self.EDITOR_VERSION,
            "block_count": 0
        }
        self._media_files = []
        self._embed_links = []
    
    def _add_block(self, name, block_type, data):
        block = {"id": str(uuid.uuid4())[:12], "name": name, "type": block_type, "data": data}
        self.payload["blocks"].append(block)
        self.payload["block_count"] += 1
        return self
    
    def add_header(self, text: str, level: int = 3):
        return self._add_block("header", "header", {"text": text, "level": level, "text_length": len(text)})
    
    def add_paragraph(self, text: str):
        return self._add_block("paragraph", "paragraph", {"text": text, "text_length": len(text)})
    
    def add_quote(self, text: str, caption: str | None = None, alignment: str = "left"):
        return self._add_block("quote", "quote", {"text": text, "caption": caption, "alignment": alignment, "text_length": len(text), "caption_length": len(caption or "")})
    
    def add_delimiter(self):
        return self._add_block("delimiter", "delimiter", {})
    
    def add_list(self, items: list, ordered: bool = False):
        return self._add_block("list", "list", {"items": items, "style": ("un", "")[ordered] + "ordered", "item_count": len(items)})
    
    def add_media(self, files: Union[str, List[str]]):
        if isinstance(files, str):
            files = [files]
        self._media_files.extend(files)
        return self._add_block("media", "media", {"items": [{"url": f"pending_{i}"} for i in range(len(self._media_files))], "item_count": len(self._media_files)})
    
    def add_embed(self, link: str):
        self._embed_links.append(link)
        return self._add_block("embed", "embed", {"service": "pending", "url": link})
    
    def _upload_media(self, is_suggestion: bool = False, is_edit_mode: bool = False):
        """Загружает все отложенные медиафайлы"""
        if (self._media_files or self._embed_links) and not self.channel_id:
            raise ValueError("ArticleBuilder(channel_id) обязателен для загрузки медиа и вложений")

        media_results = []
        if self._media_files:
            media_results = anix_images.upload_media_files(
                self.channel_id,
                self._media_files,
                is_suggestion,
                is_edit_mode,
                self.request_delay
            )
        
        embed_results = []
        if self._embed_links:
            for link in self._embed_links:
                result = anix_images.upload_embed_content(
                    self.channel_id,
                    link,
                    is_suggestion,
                    is_edit_mode
                )
                embed_results.append(result)
                if self.request_delay > 0:
                    time.sleep(self.request_delay)
        
        return media_results, embed_results
    
    def build(self, channel_id: Optional[int] = None, is_suggestion=False, is_edit_mode=False):
        """Собирает финальный payload с загрузкой медиа и вложений"""
        self.channel_id = channel_id
        media_results, embed_results = self._upload_media(is_suggestion, is_edit_mode)
        
        embed_index = 0
        for block in self.payload["blocks"]:
            if block["type"] == "media":
                block["data"]["items"] = [r["file"] for r in media_results]
            elif block["type"] == "embed":
                block["data"].update(embed_results[embed_index])
                embed_index += 1
        
        return {"payload": self.payload}


class Paginator:
    """Универсальный пагинатор для любых объектов."""
    
    def __init__(
        self,
        fetch_func: Callable[[int], Any],
        start_page: int = 0,
        end_page: Optional[int] = None
    ):
        self.fetch_func = fetch_func
        self.start_page = start_page
        self.end_page = end_page
        self._current_page = start_page - 1  # Для __next__
        self._total_pages = None
        self._buffer = []
        self._buffer_index = 0

    def __iter__(self) -> Iterator[Any]:
        return self

    def __next__(self) -> Any:
        while True:
            # Если в буфере есть элементы — возвращаем их
            if self._buffer_index < len(self._buffer):
                item = self._buffer[self._buffer_index]
                self._buffer_index += 1
                return item

            # Переход к следующей странице
            self._current_page += 1

            # Проверка на выход за границы
            if self._total_pages is not None and self._current_page >= self._total_pages:
                raise StopIteration
            if self.end_page is not None and self._current_page > self.end_page:
                raise StopIteration

            # Загрузка данных
            try:
                items, total_pages = self.fetch_func(self._current_page)
            except Exception as e:
                raise StopIteration from e

            # Обновление общего числа страниц (если ещё не известно)
            if self._total_pages is None:
                self._total_pages = total_pages
                # Корректируем end_page, если он не задан или превышает общее кол-во
                if self.end_page is None:
                    self.end_page = self._total_pages - 1
                else:
                    self.end_page = min(self.end_page, self._total_pages - 1)

            # Если страница пуста или вышли за границы — завершаем итерацию
            if not items:
                raise StopIteration

            # Обновляем буфер
            self._buffer = items
            self._buffer_index = 0


def paginate(
    fetch_func: Callable[[int], tuple[list[Any], int]],
    page: Union[int, range, None] = None
) -> Union[list[Any], Paginator]:
    """Универсальная функция для пагинации.
    
    Args:
        fetch_func: Функция, которая принимает номер страницы и возвращает (items, total_pages).
        page: 
            - int: загрузить только эту страницу.
            - range: загрузить страницы из диапазона.
            - None: загрузить все страницы (от 0 до последней).
    
    Returns:
        - Если page=int → возвращает список элементов.
        - Если page=range или None → возвращает Paginator (итерируемый объект).
    """
    if isinstance(page, int):
        items, _ = fetch_func(page)
        return items
    else:
        start = 0 if page is None else (page.start if isinstance(page, range) else 0)
        end = None if page is None else (page.stop - 1 if isinstance(page, range) else None)
        return Paginator(fetch_func, start_page=start, end_page=end)