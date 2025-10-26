from database import get_db, init_db, Post, User


def initialize_database():
	# Инициализация базы данных
	init_db()

	# Получить сессию базы данных
	db_gen = get_db()
	db = next(db_gen)

	# Проверка существующих данных
	existing_users = db.query(User).count()
	existing_posts = db.query(Post).count()

	if existing_users == 0 and existing_posts == 0:
		# Демо-данные пользователей
		users_data = [
			{"name": "Ivan", "surname": "Ivanov", "age": 17},
			{"name": "Petr", "surname": "Petrov", "age": 27},
			{"name": "Sidor", "surname": "Sidorov", "age": 47}
		]

		users = []
		for user_data in users_data:
			user = User(**user_data)
			db.add(user)
			users.append(user)

		db.commit()

		# Демо-данные постов
		posts_data = [
			{"title": "Post 1", "body": "1. Lorem ipsum dolor sit amet", "author_id": users[0].id},
			{"title": "Post 2", "body": "2. Lorem ipsum dolor sit amet", "author_id": users[1].id},
			{"title": "Post 3", "body": "3. Lorem ipsum dolor sit amet", "author_id": users[2].id}
		]

		for post_data in posts_data:
			post = Post(**post_data)
			db.add(post)

		db.commit()
		print("База данных инициализирована с демо-данными!")
	else:
		print("База данных уже содержит данные. Пропуск инициализации.")


if __name__ == "__main__":
	initialize_database()
