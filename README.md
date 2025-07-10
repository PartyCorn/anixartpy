# AnixartPy
Python-оболочка для работы с API Anixart (версия 9.0+)

[![PyPI](https://img.shields.io/pypi/v/anixartpy)](https://pypi.org/project/anixartpy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> [!WARNING]  
> Проект разработан в ознакомительных целях.  
> Аутентификационные роуты скрыты - работа возможна только с пользовательским токеном.

## 🔥 Возможности
 - Создание, удаление, оценивание и редактирование статей
 - Управление своими каналами и их участниками
 - Работа с предложенными записями в каналах

## 📦 Установка
```bash
pip install anixartpy
```

## 🚀 Быстрый старт
```python
from anixartpy import AnixartAPI, ArticleBuilder, Style, enums

# Инициализируйте API с помощью своего токена (None, чтобы получать данные в качестве гостя)
api = AnixartAPI(token="your_token_here")

# Создайте конструктор статей
article_data = ArticleBuilder(request_delay=0.25)\  # Промежуток времени между запросами на загрузку медиа и вложений
    .add_header("Заголовок статьи")\
    .add_paragraph(f"Это {Style.underline('подчёркнутый')} текст.")\
    .add_quote("Это цитата", caption="Автор", alignment=enums.QuoteAlignment.CENTER)\
    .add_delimiter()\
    .add_list(["Элемент списка 1", "Элемент списка 2", "Элемент списка 3"], ordered=True)\
    .add_media(["path/to/image.jpg", "https://example.com/image.png", open("path/to/image.jpg", "rb").read()])\
    .add_embed("https://example.com")

# Создайте статью
article = api.get_channel(123).create_article(article_data)

# Получите комментарии к этой записи
for comment in api.get_article(article.id).get_comments(enums.Sorting.NEW, page=None):
    # page: None - все страницы с нуля, range(0, 5) - с 0 до 4 страницы включительно, 0 - только 1 страницу
    print(comment.profile.login, comment.message, sep=' - ')
```