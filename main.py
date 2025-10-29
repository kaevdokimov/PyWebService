import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Annotated, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, func, select, table
from sqlalchemy.orm import Session
from starlette.middleware.gzip import GZipMiddleware

from database import get_db, init_db, NewsItem, NewsSource
from enums import ApiSection
from shemas import (
	NewsItemCreate, NewsItemResponse, NewsSourceCreate, NewsSourceResponse, NewsSourceWithCount
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan():
	try:
		init_db()
		logger.info("База данных инициализирована успешно")
		yield
	except Exception as e:
		logger.error(f"Ошибка инициализации базы данных: {e}")
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


### Эндпоинт получения новостей
@app.get("/news", tags=[ApiSection.news], response_model=List[NewsItemResponse])
async def get_news(
		page: Annotated[int, Query(ge=1)] = 1,
		size: Annotated[int, Query(ge=1, le=100)] = 20,
		period: Annotated[Optional[str], Query(description="Filter by time period")] = None,
		db: Session = Depends(get_db)
) -> list[type[NewsItem]]:
	"""
	<h2>Получение новостей</h2>

	<h3>Args:</h3>
		<b>page</b>: Номер страницы (начиная с 1);\t
		<b>size</b>: Размер страницы (1-100);\t
		<b>period</b>: Период фильтрации (today, yesterday, last_7_days, last_week)\t

	<h3>Returns:</h3>
		Список новостей
	"""
	try:
		query = db.query(NewsItem)

		# Фильтрация по периоду
		if period:
			query = apply_date_filter(query, period)

		# Пагинация
		offset = (page - 1) * size
		news_items = query.order_by(NewsItem.published_at.desc()).offset(offset).limit(size).all()

		return news_items
	except Exception as e:
		logger.error(f"Ошибка при получении новостей: {e}")
		raise HTTPException(status_code=500, detail="Ошибка при получении новостей") from e


def apply_date_filter(query, period: str):
	"""Применить фильтрацию по дате к запросу на основе периода"""
	now = datetime.now()

	if period == "today":
		start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
		end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
		query = query.filter(and_(
			NewsItem.published_at >= start_of_day,
			NewsItem.published_at <= end_of_day
		))
	elif period == "yesterday":
		start_of_yesterday = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
		end_of_yesterday = (now - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
		query = query.filter(and_(
			NewsItem.published_at >= start_of_yesterday,
			NewsItem.published_at <= end_of_yesterday
		))
	elif period == "last_7_days":
		seven_days_ago = now - timedelta(days=7)
		query = query.filter(NewsItem.published_at >= seven_days_ago)
	elif period == "last_week":
		# Последняя календарная неделя (с понедельника по воскресенье)
		today = now.date()
		days_since_monday = today.weekday()
		start_of_last_week = today - timedelta(days=days_since_monday + 7)
		end_of_last_week = start_of_last_week + timedelta(days=6)

		start_datetime = datetime.combine(start_of_last_week, datetime.min.time())
		end_datetime = datetime.combine(end_of_last_week, datetime.max.time())

		query = query.filter(and_(
			NewsItem.published_at >= start_datetime,
			NewsItem.published_at <= end_datetime
		))

	return query


### Эндпоинт добавления новости
@app.post("/news", tags=[ApiSection.news], response_model=NewsItemResponse)
async def create_news_item(
		news_item: NewsItemCreate,
		db: Session = Depends(get_db)
) -> NewsItem:
	"""
	<h2>Создание новости</h2>
	
	<h3>Args:</h3>
		<b>news_item</b>: Данные для создания новости\t
		
	<h3>Returns:</h3>
		Созданная новость
	"""
	try:
		db_news_item = NewsItem(**news_item.dict())
		db.add(db_news_item)
		db.commit()
		db.refresh(db_news_item)
		return db_news_item
	except Exception as e:
		logger.error(f"Ошибка создания новости: {e}")
		db.rollback()
		raise HTTPException(status_code=500, detail="Ошибка создания новости") from e


### Эндпоинт получения источников новостей
@app.get("/sources", tags=[ApiSection.sources], response_model=List[NewsSourceWithCount])
async def get_sources_with_counts(
		db: Session = Depends(get_db)
) -> List[dict]:
	"""
	<h2>Получение источников новостей</h2>
	
	<h3>Returns:</h3>
		Список источников с количеством новостей
	"""
	try:
		sources_with_counts = db.query(
			NewsSource,
			select(func.count.select(table(NewsSource.__tablename__, NewsItem.id)).label('news_count'))
		).outerjoin(NewsItem, NewsSource.id == NewsItem.source_id).group_by(NewsSource.id).all()

		result = []
		for source, news_count in sources_with_counts:
			source_dict = {
				"id": source.id,
				"name": source.name,
				"url": source.url,
				"description": source.description,
				"is_active": source.is_active,
				"country": source.country,
				"created_at": source.created_at,
				"last_parsed_at": source.last_parsed_at,
				"updated_at": source.updated_at,
				"news_count": news_count or 0
			}
			result.append(source_dict)

		return result
	except Exception as e:
		logger.error(f"Ошибка при получении источников новостей: {e}")
		raise HTTPException(status_code=500, detail="Ошибка при получении источников новостей") from e


### Эндпоинт добавления источника новостей
@app.post("/sources", tags=[ApiSection.sources], response_model=NewsSourceResponse)
async def create_news_source(
		news_source: NewsSourceCreate,
		db: Session = Depends(get_db)
) -> NewsSource:
	"""
	<h2>Создание источника новостей</h2>
	
	<h3>Args:</h3>
		<b>news_source</b>: Данные для создания источника\t
		
	<h3>Returns:</h3>
		Созданный источник
	"""
	try:
		db_news_source = NewsSource(**news_source.dict())
		db.add(db_news_source)
		db.commit()
		db.refresh(db_news_source)
		return db_news_source
	except Exception as e:
		logger.error(f"Ошибка при добавлении источника новостей: {e}")
		db.rollback()
		raise HTTPException(status_code=500, detail="Ошибка при добавлении источника новостей") from e
