from contextlib import asynccontextmanager
from typing import Annotated, Dict, List, Optional

from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.middleware.gzip import GZipMiddleware

from database import get_db, init_db, Post, User
from enums import ApiSection
from shemas import PostCreateRequest, PostResponse, UserCreateRequest, UserResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
	try:
		init_db()
		yield
	except Exception as e:
		print(f"Ошибка инициализации базы данных: {e}")
		raise


app = FastAPI(lifespan=lifespan)

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
	return {"Привет": "Мир"}


### Posts action
@app.get("/posts", tags=[ApiSection.posts], response_model=List[PostResponse])
async def get_posts(db: Session = Depends(get_db)) -> list[type[Post]]:
	posts = db.query(Post).all()
	return posts


@app.get("/posts/{post_id}", tags=[ApiSection.posts], response_model=PostResponse)
async def get_post(
		post_id: Annotated[int, Path(..., title="ID поста", ge=1, lt=100)],
		db: Session = Depends(get_db)
) -> type[Post]:
	post = db.query(Post).filter(Post.id == post_id).first()
	if post is None:
		raise HTTPException(status_code=404, detail="Пост не найден")
	return post


@app.post("/posts", tags=[ApiSection.posts], response_model=PostResponse)
async def create_post(
		post_create_request: Annotated[
			PostCreateRequest,
			Body(..., example={"title": "Название поста", "body": "Текст поста"})
		],
		db: Session = Depends(get_db)
) -> Post:
	db_post = Post(
		title=post_create_request.title,
		body=post_create_request.body,
		author_id=post_create_request.author_id
	)

	db.add(db_post)
	db.commit()
	db.refresh(db_post)
	return db_post


@app.get("/search", tags=[ApiSection.posts], response_model=PostResponse)
async def search(
		post_id: Annotated[
			Optional[int],
			Query(title="ID поста для поиска", description="ID поста для поиска", ge=1, lt=100)
		],
		db: Session = Depends(get_db)
) -> type[Post]:
	if post_id:
		post = db.query(Post).filter(Post.id == post_id).first()
		if post is None:
			raise HTTPException(status_code=404, detail="Пост не найден")
		return post

	raise HTTPException(status_code=404, detail="Пост не найден")


### Users action
@app.get("/users", tags=[ApiSection.users], response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)) -> list[type[User]]:
	users = db.query(User).all()
	return users


@app.get("/users/{user_id}", tags=[ApiSection.users], response_model=UserResponse)
async def get_user(
		user_id: Annotated[
			int,
			Path(..., title="ID пользователя", ge=1, lt=100)
		],
		db: Session = Depends(get_db)
) -> type[User]:
	user = db.query(User).filter(User.id == user_id).first()
	if user is None:
		raise HTTPException(status_code=404, detail="Пользователь не найден")
	return user


@app.post("/users", tags=[ApiSection.users], response_model=UserResponse)
async def create_user(
		user_create_response: Annotated[
			UserCreateRequest,
			Body(..., example={"name": "Ivan", "surname": "Ivanov", "age": 17})
		],
		db: Session = Depends(get_db)
) -> User:
	db_user = User(
		name=user_create_response.name,
		surname=user_create_response.surname,
		age=user_create_response.age
	)

	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user
