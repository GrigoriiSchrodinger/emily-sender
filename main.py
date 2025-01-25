import json
import random
import time

from src.conf import redis
from src.feature.gpt import GptRequest
from src.feature.request.RequestHandler import RequestDataBase
from src.logger import logger

def random_seconds():
    min_seconds = 30 * 60
    max_seconds = 50 * 60
    return random.randint(min_seconds, max_seconds)

def main():
    request_db = RequestDataBase()
    gpt = GptRequest()

    last_news_queue = request_db.get_last_news_queue()
    last_news_send = request_db.get_last_news_send()

    last_news_send_seeds = {news.seed for news in last_news_send.send}
    last_news_queue_seeds = {news.seed for news in last_news_queue.queue}

    attempts = 0
    while attempts < 3:
        print(last_news_queue)
        post = gpt.choosing_post(send=last_news_send, queue=last_news_queue)
        print(post)

        if not post:
            print("Получен пустой ответ от gpt.choosing_post()")
            attempts += 1
            continue

        try:
            json_post = json.loads(post)
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}")
            attempts += 1
            continue

        seed = json_post.get("seed")

        if seed and seed not in last_news_send_seeds and seed in last_news_queue_seeds:
            detail_by_seed = request_db.get_detail_by_seed(seed)
            print(detail_by_seed)
            detail_by_seed_json = {
                "content": detail_by_seed.content,
                "channel": detail_by_seed.channel,
                "id_post": detail_by_seed.id_post,
                "outlinks": detail_by_seed.outlinks,
                "seed": seed
            }
            redis.send_to_queue(queue_name="text_conversion", data=json.dumps(detail_by_seed_json))
            request_db.delete_news_by_queue(channel=detail_by_seed.channel, id_post=detail_by_seed.id_post)
            break
        attempts += 1
    else:
        print("fail")



if __name__ == '__main__':
    logger.info("Start work")
    while True:
        main()
        time.sleep(random_seconds())