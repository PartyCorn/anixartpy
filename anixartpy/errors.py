class AnixartError(Exception):
    """Базовый класс для ошибок Anixart API."""
    ERROR_MESSAGES = {}

    def __init__(self, error_code: int, message: str = ''):
        self.error_code = error_code
        self.message = message or self.ERROR_MESSAGES.get(error_code, "Неизвестная ошибка.")
        super().__init__(self.message)

    def __str__(self):
        return f"[Ошибка {self.error_code}] {self.message}"

class DefaultError(AnixartError):
    ERROR_MESSAGES = {
        1: "Неизвестная ошибка.",
        401: "Не авторизован.",
        402: "Заблокирован.",
        403: "Заблокирован навсегда.",
    }

class ChannelCreateEditError(AnixartError):
    ERROR_MESSAGES = {
        2: "Недопустимый заголовок.",
        3: "Недопустимое описание.",
        4: "Достигнут лимит каналов.",
        5: "Канал не найден.",
        6: "Вы не владелец канала.",
        7: "Создатель канала забанен.",
    }

class EditorAvailableError(AnixartError):
    ERROR_MESSAGES = {
        2: "Редактор временно недоступен.",
        3: "Достигнут лимит статей.",
        4: "Канал не найден.",
        5: "Вы не владелец канала.",
        6: "Создатель канала забанен.",
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

class ArticleSuggestionPublishError(AnixartError):
    ERROR_MESSAGES = {
        2: "Предложенная запись не найдена.",
        3: "Канал не найден.",
        4: "Вы не владелец канала.",
        5: "Недопустимый контент предложенной записи.",
        6: "Недопустимые теги.",
        7: "Создатель канала забанен."
    }

class ArticleSuggestionDeleteError(AnixartError):
    ERROR_MESSAGES = {
        2: "Предложенная запись не найдена.",
        3: "Вы не владелец предложенной записи."
    }

class ArticleGetError(AnixartError):
    ERROR_MESSAGES = {
        2: "Статья не найдена.",
        3: "Статья удалена.",
    }

class ChannelGetError(AnixartError):
    ERROR_MESSAGES = {
        2: "Канал не найден."
    }

class ChannelSubscribeError(AnixartError):
    ERROR_MESSAGES = {
        2: "Подписка уже существует.",
        3: "Достигнут лимит подписок.",
    }

class ChannelUnsubscribeError(AnixartError):
    ERROR_MESSAGES = {
        2: "Подписки не существует.",
    }

class ChannelUploadCoverAvatarError(AnixartError):
    ERROR_MESSAGES = {
        2: "Канал не найден.",
        3: "Вы не владелец канала."
    }

class ChannelBlockError(AnixartError):
    ERROR_MESSAGES = {
        2: "Канал не найден.",
        3: "Вы не владелец канала.",
        4: "Блокировка не обнаружена."
    }

class ChannelPermissionManageError(AnixartError):
    ERROR_MESSAGES = {
        2: "Недействительное значение привилегии.",
        3: "Целевой профиль не найден.",
        4: "Канал не найден.",
        5: "Вы не владелец канала."
    }