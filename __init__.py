from . import anix_images
import os
try:
    import requests
except ImportError:
    os.system("pip install requests")
import time
import uuid

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
    
    def create_article(self, channel_id: int, article_data: dict):
        url = f"{self.BASE_URL}/article/create/{channel_id}"
        response = self.session.post(url, json=article_data)
        return response.json()
    
    def delete_article(self, article_id: int):
        url = f"{self.BASE_URL}/article/delete/{article_id}"
        response = self.session.post(url)
        return response.json()
    
    def edit_article(self, article_id: int, article_data: dict):
        url = f"{self.BASE_URL}/article/edit/{article_id}"
        response = self.session.post(url, json=article_data)
        return response.json()

class ArticleBuilder:
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.payload = {
            "time": int(time.time() * 1000),
            "blocks": [],
            "version": "2.29.0-rc.1",
            "block_count": 0
        }
    
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
        return self._add_block("list", "list", {"items": items, "style": "ordered" if ordered else "unordered", "item_count": len(items)})
    
    def add_media(self, files: str | list[str]):
        # TODO: take bytes and ioreadder from link
        media = []
        if type(files) != list:
            files = [files]
        for file in files:
            image = anix_images.upload_image(self.channel_id, file)
            if image.get('success') != 1:
                print('IMAGE ERROR')
            media.append(image["file"])
        return self._add_block("media", "media", {"items": media, "item_count": len(media)})
    
    def add_embed(self, link: str):
        embed = anix_images.upload_embed(self.channel_id, link)
        if embed.get('success') != 1:
            print('EMBED ERROR')
        return self._add_block("embed", "embed", {k: v for k, v in embed.items() if k != "success"})
    
    def build(self):
        return {"payload": self.payload}
