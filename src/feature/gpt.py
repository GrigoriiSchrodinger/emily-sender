import time

from openai import OpenAI

from src.conf import API_KEY, get_list_news_choosing_post, get_promt_choosing_post, MODEL, BASE_URL
from src.logger import logger


class GptAPI:
    def __init__(self, api_key: str = API_KEY, base_url: str = BASE_URL, model: str = MODEL):
        self.client = None
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.initialize_client()

    def initialize_client(self):
        try:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        except Exception as error:
            logger.exception("Произошла ошибка: %s", error)

    def create(self, prompt: str, user_message: str) -> str:
        try:
            start_time = time.time()
            logger.debug(f"Начало GPT запроса: {prompt[:100]}...")

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_message}
                ]
            )

            duration = time.time() - start_time
            logger.info(
                f"GPT запрос выполнен за {duration:.2f}s",
                extra={
                    "duration": duration,
                    "gpt_model": self.model,
                    "response": completion
                }
            )
            return completion.choices[0].message.content
        except Exception as error:
            logger.error(f"GPT ошибка: {error} | Model: {self.model}", exc_info=True)
            return ""


class GptRequest(GptAPI):
    def choosing_post(self, list_news) -> str:
        logger.debug(f"Делаем запрос gpt - выбора поста")
        return self.create(
            prompt=get_promt_choosing_post(),
            user_message=get_list_news_choosing_post().format(list_news=list_news)
        )
