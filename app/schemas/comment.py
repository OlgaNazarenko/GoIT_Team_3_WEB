from pydantic import BaseModel, validator, constr


class CommentBase(BaseModel):
    user_id: int
    image_id: int
    data: constr(min_length=10, max_length=350)

    @validator('data')
    def text_must_not_be_empty(cls, value):
        if not value or not value.strip():
            raise ValueError('Text must not be empty')
        return value


class CommentUpdate(CommentBase):
    done: bool


class CommentResponse(CommentBase):
    id: int = 1
    user_id: int = 1
    image_id: int = 1
    data: constr(min_length = 10, max_length = 350) = "This is a comment"

    class Config:
        orm_mode = True
