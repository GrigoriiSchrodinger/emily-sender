from pydantic import BaseModel


class PostBase(BaseModel):
    pass

class GetNewsMaxValueResponse(PostBase):
    channel: str
    content: str
    id_post: int
    outlinks: list[str]

class DeletePostByQueue(PostBase):
    channel: str
    id_post: int
