# Foodgram

**Foodgram** — это веб-приложение для публикации рецептов, добавления их в избранное и список покупок, а также подписки на авторов.

## Стек технологий

* Python 3.13
* Django 5.2
* Django REST Framework
* PostgreSQL
* Docker
* Docker Compose
* Nginx
* Gunicorn
* GitHub Actions

## Запуск с Docker

### 1. Клонирование репозитория

```bash
git clone https://github.com/Hihi567no/foodgram-st
cd foodgram-st
```

### 2. Создание и настройка `.env` файла

Перейдите в директорию `infra/` и создайте файл `.env` со следующим содержимым:

```env
POSTGRES_DB=your_postgres_db
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost
```

### 3. Сборка и запуск контейнеров

```bash
docker-compose up -d --build
```

### 4. Применение миграций и сбор статики

```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --noinput
```

### 5. Создание суперпользователя

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 6. Загрузка данных

Загрузите ингредиенты, пользователей и рецепты:

```bash
docker-compose exec backend python manage.py load_ingredients
docker-compose exec backend python manage.py load_users
docker-compose exec backend python manage.py load_recipes
```

### 7. Доступ к приложению

* Frontend: [http://localhost/](http://localhost/)
* Админка: [http://localhost/admin/](http://localhost/admin/)
* API: [http://localhost/api/](http://localhost/api/)

## Автор

**Схрейдер Александр**

🔗 [GitHub: Ршрш567тщ](https://github.com/Hihi567no)
