import time
import uuid
from . import anix_images

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

    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.payload = {
            "time": int(time.time() * 1000),
            "blocks": [],
            "version": self.EDITOR_VERSION,
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
        return self._add_block("list", "list", {"items": items, "style": ("un", "")[ordered] + "ordered", "item_count": len(items)})
    
    def add_media(self, files: str | list[str]):
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
