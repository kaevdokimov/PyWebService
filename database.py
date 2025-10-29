import logging

from sqlalchemy import Boolean, Column, create_engine, DateTime, ForeignKey, func, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Update the database URL for PostgreSQL with psycopg3
# You'll need to set the proper connection string for your PostgreSQL instance
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5434/postgres"

# Create engine with connection pooling and retry settings
engine = create_engine(
	SQLALCHEMY_DATABASE_URL,
	pool_pre_ping=True,  # Verify connections before use
	pool_recycle=300,  # Recycle connections every 5 minutes
	echo=True  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class NewsSource(Base):
	__tablename__ = "news_sources"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String(255), nullable=False)
	url = Column(String(500), nullable=False)
	description = Column(Text)
	is_active = Column(Boolean, nullable=False)
	created_at = Column(DateTime, nullable=False, default=func.now)
	last_parsed_at = Column(DateTime, nullable=True)
	updated_at = Column(DateTime, nullable=True)
	country = Column(String(10), nullable=False, default='rus')
	# Связь с новостями
	news_items = relationship("NewsItem", back_populates="source")


class NewsItem(Base):
	__tablename__ = "news_items"

	id = Column(Integer, primary_key=True, index=True)
	source_id = Column(Integer, ForeignKey("news_sources.id"), nullable=False)
	title = Column(String(500), nullable=False)
	description = Column(Text)
	content = Column(Text)
	link = Column(String(1000))
	image_url = Column(String(500))
	guid = Column(String(500), nullable=False)
	published_at = Column(DateTime, nullable=False)
	created_at = Column(DateTime, nullable=False, default=func.now)
	updated_at = Column(DateTime, nullable=True)

	# Связь с источником новостей
	source = relationship("NewsSource", back_populates="news_items")


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def init_db():
	try:
		Base.metadata.create_all(bind=engine)
		logger.info("База данных инициализирована успешно")
	except Exception as e:
		logger.error(f"Ошибка инициализации базы данных: {e}")
		raise
