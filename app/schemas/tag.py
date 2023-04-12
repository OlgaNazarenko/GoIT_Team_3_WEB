from .core import CoreModel, IDModelMixin, DateTimeModelMixin


class TagBase(CoreModel):
    tag_id: int
    name: str


class TagResponse(DateTimeModelMixin, TagBase, IDModelMixin):

    class Config:
        orm_mode = True
