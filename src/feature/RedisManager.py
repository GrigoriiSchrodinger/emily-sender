import json

import redis

from src.logger import logger


class RedisQueue:
    def __init__(self, host='localhost', port=6379, db=0):
        """
        Инициализирует подключение к Redis и имя очереди.
        """
        self.redis_conn = redis.Redis(host=host, port=port, db=db)

    def send_to_queue(self, queue_name, data):
        """
        Отправляет данные в очередь
        """
        # try:
        logger.debug(f"Отправляем в очередь - {queue_name} | {json.loads(data)}")
        self.redis_conn.rpush(queue_name, data)
        # except Exception as error:
        #     logger.exception("Произошла ошибка: %s", error)

    def receive_from_queue(self, queue_name, block=True, timeout=None):
        """
        Получает данные из очереди
        Если блокировка включена, будет ждать до появления данных.
        """
        try:
            if block:
                logger.debug(f"Ждем ответа очереди - {queue_name}")
                item = self.redis_conn.blpop(queue_name, timeout=timeout)
            else:
                item = self.redis_conn.lpop(queue_name)

            if item:
                logger.debug(f"Получили из очереди - {json.loads(item[1].decode('utf-8'))}")
                return json.loads(item[1].decode('utf-8'))
            return None
        except Exception as error:
            logger.exception("Произошла ошибка: %s", error)
