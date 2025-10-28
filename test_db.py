import logging
from datetime import datetime

from database import get_db, init_db, NewsItem, NewsSource

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_db():
	try:
		# Инициализация базы данных
		init_db()
		
		# Получить сессию базы данных
		db_gen = get_db()
		db = next(db_gen)
		
		# Создание источника новостей
		source = NewsSource(
			name="Тестовый источник",
			url="https://test.com",
			description="Тестовое описание",
			is_active=True,
			country="rus"
		)
		db.add(source)
		db.commit()
		db.refresh(source)
		logger.info(f"Создан источник: {source.name}, id {source.id}")
		
		# Создание новости
		news_item = NewsItem(
			title="Тестовая новость",
			description="Описание тестовой новости",
			content="Полный текст тестовой новости",
			link="https://test.com/news1",
			image_url="https://test.com/image1.jpg",
			guid="test1",
			published_at=datetime(2025, 10, 27, 10, 0, 0),
			source_id=source.id
		)
		db.add(news_item)
		db.commit()
		db.refresh(news_item)
		logger.info(f"Создана новость: {news_item.title}, id {news_item.id}")
		
		sources = db.query(NewsSource).all()
		logger.info(f"Всего источников: {len(sources)}")
		
		news_items = db.query(NewsItem).all()
		logger.info(f"Всего новостей: {len(news_items)}")
		
		# Очистка тестовых данных
		db.delete(news_item)
		db.delete(source)
		db.commit()
		
		logger.info("Тест завершился успешно!")
	
	except Exception as e:
		logger.error(f"Error in database test: {e}")
		raise


if __name__ == "__main__":
	test_db()
