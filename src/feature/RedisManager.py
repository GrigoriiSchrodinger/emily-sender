import redis

from src.logger import logger
from src.service_url import get_url_redis


class RedisQueue:
    def __init__(self, host=get_url_redis(), port=6379, db=0):
        try:
            self.redis_conn = redis.StrictRedis(host=host, port=port, db=db)
            self.redis_conn.ping()  # Проверка подключения
            logger.info(f"Успешное подключение к Redis: {host}:{port} DB:{db}")
        except redis.RedisError as e:
            logger.critical(f"Ошибка подключения к Redis: {e}", exc_info=True)
            raise

    def send_to_queue(self, queue_name, data):
        try:
            self.redis_conn.rpush(queue_name, data)
            logger.debug(f"Отправка в {queue_name}: {data[:200]}...")  # Логируем часть данных
        except Exception as e:
            logger.error(f"Ошибка отправки в очередь {queue_name}: {e}", exc_info=True)
            raise

    def receive_from_queue(self, queue_name, block=True, timeout=None):
        if block:
            return self.redis_conn.blpop(queue_name, timeout=timeout)
        else:
            return self.redis_conn.lpop(queue_name)

    def subscribe_to_channel(self, channel_name, callback):
        try:
            pubsub = self.redis_conn.pubsub()
            pubsub.subscribe(channel_name)
            logger.info(f"Подписка на канал {channel_name} успешна")

            for message in pubsub.listen():
                if message['type'] == 'message':
                    logger.debug(f"Обработка сообщения из {channel_name}: {message['data'][:200]}...")
                    callback(message['data'])
        except Exception as e:
            logger.critical(f"Ошибка в подписке Redis: {e}", exc_info=True)
            raise
