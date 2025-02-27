# AnixartPy
Оболочка API на Python для Anixart.

## Возможности
 - Создание, удаление, оценивание и редактирование статей

## Пример Использования
```python
from anixartpy import AnixartAPI, ArticleBuilder, Style, enums

# Инициализируйте API с помощью своего токена
api = AnixartAPI(token="your_token_here")

# Создайте конструктор статей
builder = ArticleBuilder(channel_id=123)\
    .add_header("Заголовок статьи")\
    .add_paragraph(f"Это {Style.underline('обычного')} текста.")\
    .add_quote("Это цитата", caption="Автор", alignment=enums.QuoteAlignment.CENTER)\
    .add_delimiter()\
    .add_list(["Элемент списка 1", "Элемент списка 2", "Элемент списка 3"], ordered=True)\
    .add_media(["path/to/image.jpg", "https://example.com/image.png", open("path/to/image.jpg", "rb").read()])\
    .add_embed("https://example.com")

# Создайте статью
article = api.create_article(channel_id=123, article_data=article_data)
```