from typing import Optional

import requests
from pydantic import BaseModel, ValidationError

from src.feature.request.schemas import DeletePostByQueue, GetNewsMaxValueResponse
from src.logger import logger


class RequestHandler:
    def __init__(self, base_url="http://0.0.0.0:8000/news", headers=None, timeout=10):
        """
        Инициализация класса для работы с запросами.

        :param base_url: Базовый URL для запросов
        :param headers: Заголовки для запросов (по умолчанию None)
        :param timeout: Тайм-аут для запросов (по умолчанию 10 секунд)
        """
        self.base_url = base_url
        self.headers = headers if headers is not None else {}
        self.timeout = timeout

    def __get__(
            self, endpoint: str, path_params: Optional[BaseModel] = None, query_params: Optional = None,
            response_model: Optional = None
    ):
        """
        Выполняет GET-запрос к указанному endpoint.

        :param query_params:
        :param path_params:
        :param response_model:
        :param endpoint: Путь к ресурсу относительно base_url
        :return: Ответ сервера в формате JSON (если есть) или текстовый ответ
        """
        # Формируем URL с подстановкой параметров пути

        if path_params:
            endpoint = endpoint.format(**path_params.model_dump())

        url = f"{self.base_url}/{endpoint}"

        try:
            # Преобразуем параметры запроса в словарь
            logger.debug(f"Делаем get запрос - {url}, data - {query_params}")
            query_params_dict = query_params.dict() if query_params else None
            response = requests.get(url, headers=self.headers, params=query_params_dict, timeout=self.timeout)
            response.raise_for_status()

            # Обрабатываем ответ с использованием модели
            data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            logger.debug(f"Ответ - {data}")
            return response.status_code, (response_model.parse_obj(data) if response_model else data)
        except requests.exceptions.RequestException as error:
            logger.exception("Произошла ошибка: %s", error)
            return None, None
        except ValidationError as error:
            logger.exception("Произошла ошибка: %s", error)
            return None, None

    def __post__(self, endpoint: str, data: Optional = None, response_model: Optional = None):
        """
            Выполняет POST-запрос к указанному endpoint.

            :param self:
            :param response_model:
            :param endpoint: Путь к ресурсу относительно base_url
            :param data: Данные для отправки в формате form-encoded (по умолчанию None)
            :return: Ответ сервера в формате JSON (если есть) или текстовый ответ
            """
        url = f"{self.base_url}/{endpoint}"
        try:
            logger.debug(f"Делаем post запрос - {url}, data - {data}")
            data_dict = data.model_dump() if data else None
            response = requests.post(url, headers=self.headers, json=data_dict, timeout=self.timeout)
            response.raise_for_status()

            data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            logger.debug(f"Ответ - {data}")
            return response_model.model_validate(data) if response_model else data
        except requests.exceptions.RequestException as error:
            logger.exception("Произошла ошибка: %s", error)
            return None
        except ValidationError as error:
            logger.exception("Произошла ошибка: %s", error)
            return None

    def __delete__(self, endpoint: str, path_params: Optional[BaseModel] = None, query_params: Optional = None):
        """
        Выполняет DELETE-запрос к указанному endpoint.

        :param endpoint: Путь к ресурсу относительно base_url
        :param path_params: Параметры пути для подстановки в URL
        :param query_params: Параметры запроса
        :return: Ответ сервера в формате JSON (если есть) или текстовый ответ
        """
        if path_params:
            endpoint = endpoint.format(**path_params.model_dump())

        url = f"{self.base_url}/{endpoint}"

        try:
            logger.debug(f"Делаем delete запрос - {url}, data - {query_params}")
            query_params_dict = query_params.dict() if query_params else None
            response = requests.delete(url, headers=self.headers, params=query_params_dict, timeout=self.timeout)
            response.raise_for_status()

            data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            logger.debug(f"Ответ - {data}")
            return data
        except requests.exceptions.RequestException as error:
            logger.exception("Произошла ошибка: %s", error)
            return None

    def set_headers(self, headers):
        """
        Устанавливает или обновляет заголовки для запросов.

        :param self:
        :param headers: Словарь с заголовками
        """
        self.headers.update(headers)

    def set_timeout(self, timeout):
        """
        Устанавливает тайм-аут для запросов.

        :param self:
        :param timeout: Тайм-аут в секундах
        """
        self.timeout = timeout

class RequestDataBase(RequestHandler):
    def get_max_rate_news(self) -> Optional[GetNewsMaxValueResponse]:
        status_code, data = self.__get__(endpoint="rate-max-value")
        if status_code == 203:
            return None
        return data

    def delete_news_by_queue(self, channel: str, id_post: int):
        path_params = DeletePostByQueue(
            channel=channel,
            id_post=id_post
        )
        return self.__delete__(endpoint="delete-news-queue/{channel}/{id_post}", path_params=path_params)