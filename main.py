from typing import Dict, List, Optional, Annotated

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Path, Query, Body
from starlette.middleware.gzip import GZipMiddleware

from enums import ApiSection
from shemas import PostResponse, PostCreateRequest, UserResponse, UserCreateRequest

app = FastAPI()

origins = [
	"http://localhost:8080",
	"http://127.0.0.1:8080"
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=500, compresslevel=7)


@app.get("/")
async def home() -> Dict[str, str]:
	return {"Hello": "World"}


posts = [
	{"id": 1, "title": "Post 1", "body": "1. Lorem ipsum dolor sit amet", "author_id": 1},
	{"id": 2, "title": "Post 2", "body": "2. Lorem ipsum dolor sit amet", "author_id": 2},
	{"id": 3, "title": "Post 3", "body": "3. Lorem ipsum dolor sit amet", "author_id": 3},
]

users = [
	{"id": 1, "name": "Ivan", "surname": "Ivanov", "age": 17},
	{"id": 2, "name": "Petr", "surname": "Petrov", "age": 27},
	{"id": 3, "name": "Sidor", "surname": "Sidorov", "age": 47},
]


### Posts action
@app.get("/posts", tags=[ApiSection.posts], response_model=List[PostResponse])
async def get_posts() -> List[PostResponse]:
	return [PostResponse(**post) for post in posts]


@app.get("/posts/{id}", tags=[ApiSection.posts], response_model=PostResponse)
async def get_post(id: Annotated[int, Path(..., title="ID поста", ge=1, lt=100)]) -> PostResponse:
	for post in posts:
		if post["id"] == id:
			return PostResponse(**post)

	raise HTTPException(status_code=404, detail="Post not found")


@app.post("/posts", tags=[ApiSection.posts], response_model=PostResponse)
async def create_post(post_create_request: Annotated[PostCreateRequest,
Body(..., example={"title": "Заголовок поста", "body": "Текст поста"})]) -> PostResponse:
	# Находим максимальный id
	max_id = max((post["id"] for post in posts), default=0)

	# Создаем объект Post с новым id
	new_post = PostResponse(
		id=max_id + 1,
		title=post_create_request.title,
		body=post_create_request.body
	)

	posts.append(new_post.model_dump())
	return new_post


@app.get("/search", tags=[ApiSection.posts], response_model=PostResponse)
async def search(post_id: Annotated[
	Optional[int],
	Query(title="ID поста для поиска", description="ID поста для поиска", ge=1, lt=100)
]
                 ) -> PostResponse:
	if post_id:
		for post in posts:
			if post["id"] == post_id:
				return PostResponse(**post)

	raise HTTPException(status_code=404, detail="Post not found")


### Users action
@app.get("/users", tags=[ApiSection.users], response_model=List[UserResponse])
async def get_users() -> List[UserResponse]:
	return [UserResponse(**user) for user in users]


@app.get("/users/{id}", tags=[ApiSection.users], response_model=UserResponse)
async def get_user(id: Annotated[int, Path(..., title="ID пользователя", ge=1, lt=100)]) -> UserResponse:
	for user in users:
		if user["id"] == id:
			return UserResponse(**user)

	raise HTTPException(status_code=404, detail="User not found")


@app.post("/users", tags=[ApiSection.users], response_model=UserResponse)
async def create_user(user_create_response: Annotated[
	UserCreateRequest, Body(..., example={"name": "Ivan", "surname": "Ivanov", "age": 17})]) -> UserResponse:
	# Находим максимальный id
	max_id = max((user["id"] for user in users), default=0)

	# Создаем объект User с новым id
	new_user = UserResponse(
		id=max_id + 1,
		name=user_create_response.name,
		surname=user_create_response.surname,
		age=user_create_response.age
	)

	users.append(new_user.model_dump())
	return new_user
