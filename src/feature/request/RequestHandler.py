from typing import Optional, Any

import requests
from pydantic import BaseModel, ValidationError

from src.feature.request.schemas import DeletePostByQueue, PostSendNewsList, PostQueueList, DetailBySeedResponse, \
    DetailBySeed, SelectBestNews, SelectBestNewsResponse, SelectBestNewsList, SelectRelationship, \
    SelectRelationshipResponse, SendNewsRelationship, ModifiedPost, ImproveText, ImproveTextResponse, RelationshipNews, \
    RelationshipNewsResponse
from src.logger import logger
from src.service_url import get_url_emily_database_handler, get_url_emily_gpt_handler


class RequestHandler:
    def __init__(self, base_url=get_url_emily_database_handler(), headers=None, timeout=10):
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
            logger.debug(f"Начало GET запроса: {endpoint}")
            # Преобразуем параметры запроса в словарь
            logger.debug(f"Делаем get запрос - {url}, data - {query_params}")
            query_params_dict = query_params.dict() if query_params else None
            response = requests.get(url, headers=self.headers, params=query_params_dict, timeout=self.timeout)
            response.raise_for_status()

            # Обрабатываем ответ с использованием модели
            data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            logger.debug(f"Ответ - {data}")
            logger.info(f"Успешный GET: {url} [Status: {response.status_code}]")
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
            logger.debug(f"Начало POST запроса: {endpoint}")
            logger.debug(f"Делаем post запрос - {url}, data - {data}")
            data_dict = data.model_dump() if data else None
            response = requests.post(url, headers=self.headers, json=data_dict, timeout=self.timeout)
            response.raise_for_status()

            data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            logger.debug(f"Ответ - {data}")
            logger.info(f"Успешный POST: {url} [Status: {response.status_code}]")
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
            logger.debug(f"Начало DELETE запроса: {endpoint}")
            logger.debug(f"Делаем delete запрос - {url}, data - {query_params}")
            query_params_dict = query_params.dict() if query_params else None
            response = requests.delete(url, headers=self.headers, params=query_params_dict, timeout=self.timeout)
            response.raise_for_status()

            data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            logger.debug(f"Ответ - {data}")
            logger.info(f"Успешный DELETE: {url} [Status: {response.status_code}]")
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
    def __get_last_send_news__(self) -> [int, PostSendNewsList]:
        return self.__get__(endpoint='send-news/get-news/by/hours', response_model=PostSendNewsList)

    def __get_last_queue__(self) -> [int, PostQueueList]:
        return self.__get__(endpoint='queue/get-news/by/hours', response_model=PostQueueList)

    def __get_detail_by_seed__(self, seed: str) -> tuple[int, str | Any] | tuple[None, None]:
        seed_req = DetailBySeed(
            seed=seed
        )
        return self.__get__(
            endpoint='all-news/detail-by-seed/{seed}',
            path_params=seed_req,
            response_model=DetailBySeedResponse
        )

    def __create_modified_news__(self, data: ModifiedPost):
        return self.__post__(endpoint='modified-text/create', data=data)

    def __create_relationship__(self, data: RelationshipNews) -> RelationshipNewsResponse:
        return self.__post__(endpoint='all-news/create-relationship', data=data)

    def create_relationship(self, seed_news: str, current_news: str):
        data = RelationshipNews(
            seed_news=seed_news,
            related_new_seed=current_news
        )
        return self.__create_relationship__(data=data)

    def create_modified_news(self, channel: str, id_post: int, text: str):
        data = ModifiedPost(
            channel=channel,
            id_post=id_post,
            text=text
        )
        return self.__create_modified_news__(data=data)

    def get_detail_by_seed(self, seed: str) -> DetailBySeedResponse:
        return self.__get_detail_by_seed__(seed=seed)[1]

    def get_last_news_queue(self) -> PostQueueList:
        queue = self.__get_last_queue__()
        return queue[1]

    def get_last_news_send(self) -> PostSendNewsList:
        queue = self.__get_last_send_news__()
        return queue[1]

    def delete_news_by_queue(self, channel: str, id_post: int):
        path_params = DeletePostByQueue(
            channel=channel,
            id_post=id_post
        )
        return self.__delete__(endpoint="queue/delete-news/{channel}/{id_post}", path_params=path_params)

class RequestGptHandler(RequestHandler):
    def __init__(self, base_url=get_url_emily_gpt_handler(), timeout=120):
        super().__init__(base_url=base_url, timeout=timeout)

    def __select_best_news__(self, data: SelectBestNews) -> SelectBestNewsResponse:
        return self.__post__(endpoint='text-handler/select-best-news', data=data)

    def __upgrade_news__(self, data: ImproveText) -> ImproveTextResponse:
        return self.__post__(endpoint='text-handler/improve', data=data)

    def __select_relationship__(self, data: SelectRelationship) -> SelectRelationshipResponse:
        req = self.__post__(endpoint='text-handler/select-relationship', data=data)
        return req

    def check_relationship(self, news_list: list[SendNewsRelationship], current_news: str) -> dict:
        data = SelectRelationship(
            news_list=news_list,
            current_news=current_news
        )
        return self.__select_relationship__(data=data)

    def upgrade_news(self, text: str, links: list) -> ImproveTextResponse:
        data = ImproveText(
            text=text,
            links=links
        )
        return self.__upgrade_news__(data=data)

    def select_best_news(self, send_news_list: list[SelectBestNewsList], queue_news_list: list[SelectBestNewsList]) -> str:
        """
        Ручка возвращает seed лучший новости из списка очереди

        :param send_news_list: Список отправленных новостей.
        :param queue_news_list: Список очереди новостей.
        :return: Ответ seed выбранной новости
        """
        data = SelectBestNews(
            send_news_list=send_news_list,
            queue_news_list=queue_news_list
        )
        return self.__select_best_news__(data=data)["seed"]
