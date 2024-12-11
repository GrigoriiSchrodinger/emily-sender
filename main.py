import json
import random
import time

from src.conf import redis
from src.feature.gpt import GptRequest
from src.feature.request.RequestHandler import RequestDataBase
from src.logger import logger

def random_seconds():
    min_seconds = 40 * 60
    max_seconds = 60 * 60
    return random.randint(min_seconds, max_seconds)

def main():
    request_db = RequestDataBase()
    gpt = GptRequest()

    last_news_queue = request_db.get_last_news_queue()
    last_news_send = request_db.get_last_news_send()

    attempts = 0
    while attempts < 3:
        post = gpt.choosing_post(send=last_news_send, queue=last_news_queue)
        print(post)
        json_post = json.loads(post)
        seed = json_post.get("seed")
        if seed and all(seed != news.seed for news in last_news_send.send):
            detail_by_seed = request_db.get_detail_by_seed(seed)
            detail_by_seed_json = {
                "content": detail_by_seed.content,
                "channel": detail_by_seed.channel,
                "id_post": detail_by_seed.id_post,
                "outlinks": detail_by_seed.outlinks
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