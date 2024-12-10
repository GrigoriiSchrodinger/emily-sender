import json
import time

from src.conf import redis
from src.feature.request.RequestHandler import RequestDataBase
from src.logger import logger

def main():
    request_db = RequestDataBase()
    news_max_rate = request_db.get_max_rate_news()
    print(news_max_rate)
    if news_max_rate:
        redis.send_to_queue(queue_name="text_conversion", data=json.dumps(news_max_rate))
        request_db.delete_news_by_queue(channel=news_max_rate.get("channel"), id_post=news_max_rate.get("id_post"))

if __name__ == '__main__':
    logger.info("Start work")
    while True:
        main()
        time.sleep(1800)