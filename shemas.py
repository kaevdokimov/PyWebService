from typing import Annotated
from pydantic import BaseModel, Field


class UserBase(BaseModel):
	name: Annotated[str, Field(..., title="Имя пользователя", min_length=1, max_length=30)] = Field()
	surname: Annotated[str, Field(..., title="Фамилия пользователя", min_length=1, max_length=30)] = Field()
	age: Annotated[int, Field(..., title="Возраст", ge=1, lt=120)] = Field()


class UserCreateRequest(UserBase):
	pass


class UserResponse(UserBase):
	id: Annotated[int, Field(title="ID пользователя", ge=1)] = Field()

	class Config:
		orm_mode = True


class PostBase(BaseModel):
	title: Annotated[str, Field(title="Заголовок поста", min_length=1, max_length=100)] = Field()
	body: Annotated[str, Field(title="Текст поста", min_length=1, max_length=1000)] = Field()
	author_id: Annotated[int, Field(title="ID автора поста", description="ID автора", ge=1)] = Field()


class PostCreateRequest(PostBase):
	pass


class PostResponse(PostBase):
	id: Annotated[int, Field(title="ID поста", description="ID поста", ge=1)] = Field()

	class Config:
		orm_mode = True
