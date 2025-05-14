from src.service import request_db, gpt_handler


def check_news_relationship(current_news: str, seed: str):
    last_news_send = request_db.get_last_news_send()
    news_list = [{"seed": news.seed, "text": news.text} for news in last_news_send.send]
    seed_from_list = gpt_handler.check_relationship(news_list=news_list, current_news=current_news)
    if seed_from_list["seed"]:
        request_db.create_relationship(current_news=seed_from_list["seed"], seed_news=seed)
