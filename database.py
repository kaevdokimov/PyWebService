from sqlalchemy import Column, create_engine, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./pywebservice.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, index=True)
	surname = Column(String)
	age = Column(Integer)

	posts = relationship("Post", back_populates="author")


class Post(Base):
	__tablename__ = "posts"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String, index=True)
	body = Column(String)
	author_id = Column(Integer, ForeignKey("users.id"))

	author = relationship("User", back_populates="posts")


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def init_db():
	Base.metadata.create_all(bind=engine)
