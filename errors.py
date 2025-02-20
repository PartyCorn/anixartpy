class AnixartError(Exception):
    """Базовый класс для ошибок Anixart API."""
    ERROR_MESSAGES = {}

    def __init__(self, error_code: int):
        self.error_code = error_code
        self.message = self.ERROR_MESSAGES.get(error_code, "Неизвестная ошибка.")
        super().__init__(self.message)

    def __str__(self):
        return f"[Ошибка {self.error_code}] {self.message}"

class ChannelCreateEditError(AnixartError):
    ERROR_MESSAGES = {
        2: "Недопустимый заголовок.",
        3: "Недопустимое описание.",
        4: "Достигнут лимит каналов.",
        5: "Канал не найден.",
        6: "Вы не владелец канала.",
        7: "Создатель канала забанен.",
    }

class ArticleCreateEditError(AnixartError):
    ERROR_MESSAGES = {
        2: "Недопустимая статья для репоста.",
        3: "Недопустимый контент статьи.",
        4: "Недопустимые теги.",
        5: "Создание статьи временно отключено.",
        6: "Достигнут лимит статей.",
        7: "Канал не найден.",
        8: "Вы не владелец канала.",
        9: "Создатель канала забанен.",
        10: "Канал заблокирован.",
        11: "Статья не найдена.",
        12: "Статья удалена.",
    }
