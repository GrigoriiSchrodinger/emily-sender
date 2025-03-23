from src.feature.RedisManager import RedisQueue
from src.feature.request.RequestHandler import RequestDataBase, RequestGptHandler

redis = RedisQueue(port=6379, db=0)
request_db = RequestDataBase()
gpt_handler = RequestGptHandler()