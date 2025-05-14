from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PostBase(BaseModel):
    pass

class PostSendNews(PostBase):
    seed: str
    text: str
    created_at: datetime

class PostSendNewsList(PostBase):
    send: list[PostSendNews]

class PostQueue(PostBase):
    seed: str
    text: str
    created_at: datetime

class PostQueueList(PostBase):
    queue: list[PostQueue]

class DetailBySeed(PostBase):
    seed: str

class DetailBySeedResponse(PostBase):
    content: str
    channel: str
    id_post: int
    outlinks: list[str]
    new_content: str | None
    media_resolution: bool

class GetNewsMaxValueResponse(PostBase):
    channel: str
    content: str
    id_post: int
    outlinks: list[str]

class DeletePostByQueue(PostBase):
    channel: str
    id_post: int

class SelectBestNewsList(PostBase):
    seed: str
    text: str

class SelectBestNews(PostBase):
    send_news_list: list[SelectBestNewsList]
    queue_news_list: list[SelectBestNewsList]

class SelectBestNewsResponse(PostBase):
    seed: str


class SendNewsRelationship(PostBase):
    seed: str
    text: str


class SelectRelationship(BaseModel):
    news_list: list[SendNewsRelationship]
    current_news: str


class SelectRelationshipResponse(BaseModel):
    seed: Optional[int]


class ModifiedPost(PostBase):
    channel: str
    id_post: int
    text: str


class ImproveText(BaseModel):
    text: str
    links: list


class ImproveTextResponse(BaseModel):
    text: str


class RelationshipNews(PostBase):
    seed_news: str
    related_new_seed: str


class RelationshipNewsResponse(BaseModel):
    status: str
    seed_news: str
    related_seed: str
    message_id: int
