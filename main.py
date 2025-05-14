import datetime
import json
import random
import threading

import pytz

from src.feature.check_news_relationship import check_news_relationship
from src.logger import logger
from src.service import redis, request_db, gpt_handler


def random_seconds():
    min_seconds = 30 * 60
    max_seconds = 50 * 60
    return random.randint(min_seconds, max_seconds)

def main():
    try:
        logger.info("Начало обработки main()")
        last_news_queue = request_db.get_last_news_queue()
        last_news_send = request_db.get_last_news_send()
        logger.debug(f"Получено из очереди ожидания: {len(last_news_queue.queue)}")
        logger.debug(f"Получено из отправленных: {len(last_news_send.send)}")

        last_news_send = [{"seed": news.seed, "text": news.text} for news in last_news_send.send]
        last_news_queue = [{"seed": news.seed, "text": news.text} for news in last_news_queue.queue]
        if last_news_queue:
            seed = gpt_handler.select_best_news(send_news_list=last_news_send, queue_news_list=last_news_queue)
            logger.debug(f"Обработка seed: {seed}")
            detail_by_seed = request_db.get_detail_by_seed(seed)
            logger.debug(f"Детали для seed: {detail_by_seed}")
            new_post = gpt_handler.upgrade_news(text=detail_by_seed.content, links=detail_by_seed.outlinks)["text"]
            check_news_relationship(current_news=detail_by_seed.content, seed=seed)
            request_db.create_modified_news(
                channel=detail_by_seed.channel,
                id_post=detail_by_seed.id_post, text=new_post
            )
            redis.send_to_queue(queue_name="ForModer", data=json.dumps({"seed": seed}))
            request_db.delete_news_by_queue(channel=detail_by_seed.channel, id_post=detail_by_seed.id_post)
            logger.debug(f"Удален пост: {detail_by_seed.channel}/{detail_by_seed.id_post}")
        else:
            logger.debug(f"Очередь новостей пуста")
    except Exception as error:
        logger.error(f"Ошибка - {error}")


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
