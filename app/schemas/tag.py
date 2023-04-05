from .core import CoreModel, IDModelMixin, DateTimeModelMixin


class TagBase(CoreModel):
    name: str


class TagResponse(DateTimeModelMixin, TagBase, IDModelMixin):

    class Config:
        orm_mode = True
