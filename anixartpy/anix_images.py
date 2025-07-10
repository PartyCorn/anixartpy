import mimetypes
import os
import imghdr
from uuid import uuid4
from urllib.parse import urlparse
from requests import post, get
from re import findall
import time
from . import errors

BASE_HEADERS = {
    'User-Agent': 'AnixartApp/9.0 BETA 1-24121614 (Android 12; SDK 31; arm64-v8a; Xiaomi M2102J20SG; ru)',
    'API-Version': 'v2',
    'sign': 'U1R9MFRYVUdOQWcxUFp4OENja1JRb8xjZFdvQVBjWDdYR07BUkgzNllxRWJPOFB3ZkhvdU9JYVJSR9g2UklRcVk1SW3QV8xjMzc2fWYzMmdmZDc2NTloN0g0OGUwN0ZlOGc8N0hjN0U9Y0M3Z1NxLndhbWp2d1NqeC3lcm9iZXZ2aEdsOVAzTnJX2zqZpyRX',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': '*/*',
    'Origin': 'https://editor.anixsekai.com/',
    'Referer': 'https://editor.anixsekai.com/?v=2985',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}
API_INSTANCE = None

def get_base_url():
    """Получает базовый URL из API_INSTANCE"""
    if API_INSTANCE is None:
        return "https://api.anixart.app"
    return API_INSTANCE.base_url

def prepare_file_data(file_input):
    """
    Подготавливает данные файла для загрузки.
    file_input может быть:
      - Путём к файлу (строка)
      - Битовым содержимым (bytes)
      - Ссылкой из интернета (строка, начинающаяся с http:// или https://)
    Возвращает кортеж: (file_data, file_name, file_mime)
    """
    if isinstance(file_input, bytes):
        file_data = file_input
        img_type = imghdr.what(None, h=file_data)
        extension = img_type if img_type else 'bin'
        file_name = f"{uuid4().hex}.{extension}"
        file_mime = mimetypes.types_map.get(f".{extension}", "application/octet-stream")
        return file_data, file_name, file_mime

    elif isinstance(file_input, str):
        if file_input.startswith("http://") or file_input.startswith("https://"):
            response = get(file_input)
            if response.status_code != 200:
                raise ValueError(f"Ошибка при получении файла по URL: {file_input}")
            file_data = response.content
            parsed_url = urlparse(file_input)
            file_name = os.path.basename(parsed_url.path)
            if not file_name:
                file_name = f"{uuid4().hex}.bin"
            file_mime = response.headers.get("Content-Type") or mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
            return file_data, file_name, file_mime
        else:
            # Считаем, что это путь к файлу
            if not os.path.exists(file_input):
                raise ValueError(f"Файл не найден: {file_input}")
            with open(file_input, 'rb') as f:
                file_data = f.read()
            file_name = os.path.basename(file_input)
            file_mime = mimetypes.guess_type(file_input)[0] or 'application/octet-stream'
            return file_data, file_name, file_mime

    else:
        raise TypeError("Неподдерживаемый тип данных для загрузки файла.")

def prepare_multipart_body(file_input, boundary, field_name):
    """Формирует тело запроса для загрузки файла."""
    file_data, file_name, file_mime = prepare_file_data(file_input)
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"{field_name}\"; filename=\"{file_name}\"\r\n"
        f"Content-Type: {file_mime}\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()
    return body

def send_file_request(url, file_input, headers, field_name):
    """Отправляет файл на сервер."""
    boundary = f"----WebKitFormBoundary{uuid4().hex}"
    headers['Content-Type'] = f"multipart/form-data; boundary={boundary}"
    body = prepare_multipart_body(file_input, boundary, field_name)
    headers['Content-Length'] = str(len(body))
    response = post(url, headers=headers, data=body, params={'token': API_INSTANCE.token})
    return response.json()

def get_media_upload_token(cid, is_suggestion=False, is_edit_mode=False):
    """Получает media_upload_token с учетом режима работы"""
    url = f'{get_base_url()}/channel/{cid}/editor/available'
    params = {
        'token': API_INSTANCE.token if API_INSTANCE else None,
        'is_suggestion': str(is_suggestion).lower(),
        'is_edit_mode': str(is_edit_mode).lower()
    }
    response = get(url, headers=BASE_HEADERS, params=params).json()
    if response['code'] == 0:
        return response.get('media_upload_token')
    else:
        raise errors.EditorAvailableError(response['code'])

def upload_media_files(cid, files, is_suggestion=False, is_edit_mode=False, delay=0.25):
    """Загружает несколько файлов с задержкой"""
    media_token = get_media_upload_token(cid, is_suggestion, is_edit_mode)
    headers = BASE_HEADERS.copy()
    headers['Authorization'] = f"Bearer {media_token}"
    url = 'https://editor.anixsekai.com/content/upload'
    
    results = []
    for file in files:
        result = send_file_request(url, file, headers, 'file')
        results.append(result)
        if delay > 0:
            time.sleep(delay)
    return results

def upload_embed_content(cid, link, is_suggestion=False, is_edit_mode=False):
    """Загружает вложение с учетом режима работы"""
    media_token = get_media_upload_token(cid, is_suggestion, is_edit_mode)
    is_youtube = findall(
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/\S*(?:(?:\/embed)?\/|watch\?\S*?&?v=)|youtu\.be\/)([a-zA-Z0-9_-]{6,11})((?:[?&][A-Za-z0-9._-]+=[A-Za-z0-9._-]+)*)',
        link
    )
    is_vk = findall(r'(?:https?:\/\/)?(?:www\.)?vk\.com\/video\?z=video([-0-9]+)_([-0-9]+).*', link)
    is_link = findall(r'(?:https|http):\/\/.*', link)
    service = 'youtube' if is_youtube else 'vk' if is_vk else 'link' if is_link else None
    if not service:
        raise ValueError("Неизвестный сервис для внедрения.")
    
    url = f'https://editor.anixsekai.com/embed/{service}?url={link}'
    headers = BASE_HEADERS.copy()
    headers['Authorization'] = f"Bearer {media_token}"
    response = post(url, headers=headers)
    response = response.json()
    response.update({'service': service, 'url': link})
    return response

def upload_cover(cid, file_input):
    """Загружает обложку канала."""
    url = f'https://api.anixart.app/channel/cover/upload/{cid}'
    return send_file_request(url, file_input, BASE_HEADERS.copy(), 'image')

def upload_avatar(cid, file_input, is_blog: bool = False):
    """Загружает аватарку пользователя."""
    url = f'https://api.anixart.app/' + (f'channel/avatar/upload/{cid}' if not is_blog else f'profile/preference/avatar/edit')
    return send_file_request(url, file_input, BASE_HEADERS.copy(), 'image')