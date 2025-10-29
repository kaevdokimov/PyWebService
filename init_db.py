import logging
from datetime import datetime

from database import get_db, init_db, NewsItem, NewsSource

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_database():
	try:
		# Инициализация базы данных
		init_db()
		# Получить сессию базы данных
		db_gen = get_db()
		db = next(db_gen)
		# Проверка существующих данных
		existing_sources = db.query(NewsSource).count()
		existing_news = db.query(NewsItem).count()
		if existing_sources == 0 and existing_news == 0:
			# Демо-данные источников
			sources_data = [
				{
					"name": "РИА Новости",
					"url": "https://ria.ru",
					"description": "Новости России и мира",
					"is_active": True,
					"country": "rus"
				},
				{
					"name": "BBC News",
					"url": "https://bbc.com",
					"description": "World news from the British Broadcasting Corporation",
					"is_active": True,
					"country": "eng"
				},
				{
					"name": "CNN",
					"url": "https://cnn.com",
					"description": "Cable News Network",
					"is_active": True,
					"country": "usa"
				}
			]

			sources = []
			for source_data in sources_data:
				source = NewsSource(**source_data)
				db.add(source)
				sources.append(source)

			db.commit()

			# Демо-данные новостей
			news_data = [
				{
					"title": "Новость 1",
					"description": "Описание новости 1",
					"content": "Полный текст новости 1",
					"link": "https://ria.ru/news1",
					"guid": "news1",
					"published_at": datetime(2025, 10, 26, 10, 0, 0),
					"source_id": sources[0].id
				},
				{
					"title": "News 2",
					"description": "Description of news 2",
					"content": "Full content of news 2",
					"link": "https://bbc.com/news2",
					"guid": "news2",
					"published_at": datetime(2025, 10, 26, 12, 0, 0),
					"source_id": sources[1].id
				},
				{
					"title": "News 3",
					"description": "Description of news 3",
					"content": "Full content of news 3",
					"link": "https://cnn.com/news3",
					"guid": "news3",
					"published_at": datetime(2025, 10, 27, 8, 0, 0),
					"source_id": sources[2].id
				}
			]

			for news_item_data in news_data:
				news_item = NewsItem(**news_item_data)
				db.add(news_item)

			db.commit()
			logger.info("База данных инициализирована с демо-данными!")
		else:
			logger.info("База данных уже содержит данные. Пропуск инициализации.")

	except Exception as e:
		logger.error(f"Error initializing database: {e}")
		raise


if __name__ == "__main__":
	initialize_database()
