import datetime
import json
import random
import threading

import pytz

from src.logger import logger
from src.service import redis, request_db, gpt_handler


def random_seconds():
    min_seconds = 30 * 60
    max_seconds = 50 * 60
    return random.randint(min_seconds, max_seconds)


def format_news(data_send: dict, data_queue: dict) -> tuple[str, str]:
    """
    Форматирует список отправленных новостей в текстовый вид
    """
    def format_entry(index: int, item, time_label: str) -> str:
        # Используем прямое обращение к атрибутам объекта
        created_at = item.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"{index}) seed - '{item.seed}'\n"
            f"текст  - \"{item.text}\"\n"
            f"{time_label} - \"{created_at}\"\n"
        )

    # Обрабатываем объекты из send и queue
    result_send = '\n'.join([
        format_entry(i, item, "Время отправки новости")
        for i, item in enumerate(getattr(data_send, 'send', []), 1)
    ])

    result_queue = '\n'.join([
        format_entry(i, item, "Время создания новости")
        for i, item in enumerate(getattr(data_queue, 'queue', []), 1)
    ])
    return result_send, result_queue


def main():
    logger.info("Начало обработки main()")
    last_news_queue = request_db.get_last_news_queue()
    last_news_send = request_db.get_last_news_send()
    logger.debug(f"Получено из очереди ожидания: {len(last_news_queue.queue)}")
    logger.debug(f"Получено из отправленных: {len(last_news_send.send)}")

    send_news_list, queue_news_list  = format_news(data_send=last_news_send, data_queue=last_news_queue)
    last_news_send_seeds = {news.seed for news in last_news_send.send}
    last_news_queue_seeds = {news.seed for news in last_news_queue.queue}

    attempts = 0
    if last_news_queue:
        while attempts < 3:
            logger.debug(f"Попытка #{attempts + 1} выбора поста")
            # post = gpt.choosing_post(list_news=list_news)
            post = gpt_handler.select_best_news(send_news_list=send_news_list, queue_news_list=queue_news_list)

            if not post:
                logger.warning("GPT не вернул пост")
                attempts += 1
                continue
            json_post = {"seed": post}
            seed = json_post.get("seed")
            logger.debug(f"Обработка seed: {seed}")

            if seed and seed not in last_news_send_seeds and seed in last_news_queue_seeds:
                logger.info(f"Найден подходящий seed: {seed}")
                detail_by_seed = request_db.get_detail_by_seed(seed)
                logger.debug(f"Детали для seed: {detail_by_seed}")

                detail_by_seed_json = {
                    "content": detail_by_seed.content,
                    "channel": detail_by_seed.channel,
                    "id_post": detail_by_seed.id_post,
                    "outlinks": detail_by_seed.outlinks,
                    "seed": seed
                }
                redis.send_to_queue(queue_name="text_conversion", data=json.dumps(detail_by_seed_json))
                logger.info(f"Отправлено в очередь text_conversion: {detail_by_seed_json}")

                request_db.delete_news_by_queue(channel=detail_by_seed.channel, id_post=detail_by_seed.id_post)
                logger.debug(f"Удален пост: {detail_by_seed.channel}/{detail_by_seed.id_post}")
                break
            attempts += 1
        else:
            logger.error("Все попытки завершились неудачно")


def run_main(timer_event):
    while True:
        if not timer_event.wait(timeout=random_seconds()):
            moscow_time = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
            current_hour = moscow_time.hour
            if current_hour >= 8 or current_hour <= 1:
                main()
            else:
                logger.debug(f"Московское время {moscow_time.strftime('%H:%M')} вне рабочего диапазона")


def message_callback(data):
    logger.info(f"Получено сообщение из очереди: {data.decode()}")
    try:
        main()
    except Exception as e:
        logger.critical(f"Критическая ошибка в callback: {e}", exc_info=True)
    finally:
        timer_event.set()
        timer_event.clear()


if __name__ == '__main__':
    logger.info("Start work")
    timer_event = threading.Event()

    timer_thread = threading.Thread(target=run_main, args=(timer_event,))
    queue_thread = threading.Thread(target=redis.subscribe_to_channel, args=('replay', message_callback))

    timer_thread.start()
    queue_thread.start()

    timer_thread.join()
    queue_thread.join()
