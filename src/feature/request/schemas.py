from datetime import datetime

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
