# AnixartPy
Оболочка API на Python для Anixart, которая позволяет создавать, редактировать статьи с различными блоками контента и управлять ими.

## Возможности
 - Создание, удаление и редактирование статей
 - Создание статей с различными содержательными блоками: заголовками, абзацами, цитатами, разделителями, списками (упорядоченными и неупорядоченными), мультимедийными материалами (изображениями), вставками (ссылками)

## Пример Использования
```python
from anixartpy import AnixartAPI, ArticleBuilder

# Инициализируйте API с помощью своего токена
api = AnixartAPI(token="your_token_here")

# Создайте конструктор статей
builder = ArticleBuilder(channel_id=123)\
    .add_header("My Article Title")\
    .add_paragraph("This is <u>a paragraph</u> of text.")\
    .add_quote("This is a quote", caption="Author", alignment="center")\
    .add_delimiter()\
    .add_list(["Item 1", "Item 2", "Item 3"], ordered=True)\
    .add_media(["path/to/image.jpg", "https://example.com/image.png", open("path/to/image.jpg", "rb").read()])\
    .add_embed("https://example.com")

# Создайте статью
response = api.create_article(channel_id=123, article_data=article_data)
```