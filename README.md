# praktikum_new_diplom

## Запуск проекта

Склонировать проект:
```bash
git clone https://github.com/IT-Academy-2022/praktikum_new_diplom.git
```

Сменить рабочую директорию:
```bash
cd praktikum_new_diplom/infra
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