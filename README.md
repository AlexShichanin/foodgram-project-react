# Продуктовый помощник - [Foodgram](https://foodhelper.hopto.org/)

- admin
- admin@mail.ru
- 1234

## Описание проекта

**Cервиса позволяет:**

- Создать рецепты
- Добавить рецепты в избранное и список покупок
- Подписаться на пользователей сервиса
- Скачать свой список покупок с ингредиентами


**Стех технологий:**

- Python 3.10+
- Django 3.2+
- Docker
- Nginx
- NodeJS


## Запуск проекта на локальной машине

1. Клонировать репозиторий:

```
https://github.com/AlexShichanin/foodgram-project-react.git
```

---

2. В директории `infra` создать файл `.env`:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=Секретный ключ Django
```

---

3. Создать и запустить контейнер, из директории `infra` выполнить команду:

```
docker compose up -d --build
```

---

* Проект будет доступен по адресу: http://localhost/
* Документация доступна по адресу: http://localhost/api/docs/
