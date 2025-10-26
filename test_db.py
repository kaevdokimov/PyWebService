from database import get_db, init_db, Post, User


def test_db():
	# Инициализация базы данных
	init_db()

	# Получить сессию базы данных
	db_gen = get_db()
	db = next(db_gen)

	# Создание пользователя
	user = User(name="Имя", surname="Фамилия", age=25)
	db.add(user)
	db.commit()
	db.refresh(user)
	print(f"Создан пользователь: {user.name} {user.surname}, age {user.age}, id {user.id}")

	# Создание поста
	post = Post(title="Название поста", body="Текст поста", author_id=user.id)
	db.add(post)
	db.commit()
	db.refresh(post)
	print(f"Создан пост: {post.title}, id {post.id}")

	users = db.query(User).all()
	print(f"Всего пользователей: {len(users)}")

	posts = db.query(Post).all()
	print(f"Всего постов: {len(posts)}")

	# Очистка тестовых данных
	db.delete(post)
	db.delete(user)
	db.commit()

	print("Тест завершился успешно!")


if __name__ == "__main__":
	test_db()
