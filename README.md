# Foodgram
Продуктовый помощник - дипломный проект курса Backend-разработки Яндекс.Практикум. Проект представляет собой онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект реализован на Django и DjangoRestFramework
## Запуск проекта

Склонировать проект:
```bash
git clone git@github.com:Dokimos25/foodgram-project-react.git
```

Сменить рабочую директорию:
```bash
cd foodgram-project-react/infra
```

Заполнить файл `.env`:
```bash
cat <<EOF >> .env

DEBUG=0
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

EOF
```


Запустить проект:
```bash
docker-compose up -d
```

Выполнить миграции и загрузить ингредиенты в базу:
```bash
docker exec -it infra_backend_1 python manage.py migrate
docker exec -it infra_backend_1 python manage.py setupdb
```

Собрать статические файлы:
```bash
docker exec -it infra_backend_1 python manage.py collectstatic --noinput
```

Создать суперпользователя:
```bash
docker exec -it infra_backend_1 python manage.py createsuperuser
```

Далее необходимо в панели администрирования создать несколько тегов.

## Проект доступен по адресам:
[foodprod](http://foodprod.ddns.net/) и [158.160.75.108](http://158.160.75.108/recipes)
## Технологический стек:
• Python • Django • Django REST • Framework • PostgreSQL • Nginx • gunicorn • Docker • Docker-compose • Docker Hub • GitHubActions
## Автор:
[Анна Королькова](https://github.com/Dokimos25)
