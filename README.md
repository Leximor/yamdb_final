#Проект YaMDb 

_Проект собирает отзывы (Review) пользователей на произведения (Titles). 
Произведения делятся на категории: «Книги», «Фильмы», «Музыка». 
Список категорий (Category) может быть расширен администратором (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»)._

## Используемые технологии(стэк):
 - [Python](https://www.python.org/)
 - [Django (DRF, ORM)](https://docs.djangoproject.com/en/4.0/releases/2.2.20/)
 - [Postgresql](https://www.postgresql.org/)
 - [Docker](https://docs.docker.com/)
 - [Nginx](https://nginx.org/ru/)



## Шаблон наполнения env-файла:

DB_ENGINE= # указываем, что работаем с postgresql

DB_NAME= # имя базы данных

POSTGRES_USER= # логин для подключения к базе данных

POSTGRES_PASSWORD= # пароль для подключения к БД (установите свой)

DB_HOST= # название сервиса (контейнера)

DB_PORT= # порт для подключения к БД 

SECRET_KEY= #Секретный ключ

## Как запустить проект:

>Клонировать репозиторий через командную строку:
```
gi clone https://github.com/Leximor/infra_sp2_api_yamdb.git
```

>```Установить Docker```

>Запустить из каталога локального репозитория docker-compose:

```
docker-compose up
```

>Выполнить миграции:
```
docker-compose exec web python manage.py migrate
```
>Cоздать суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```
>Скопировать статику:
```
docker-compose exec web python manage.py collectstatic --no-input
```

### Для остановки контейнера:
``` 
docker container stop <CONTAINER ID> 
```
### Для запуска контейнера:
```
docker container start <CONTAINER ID>
```
## Авторы: 
[Алексей](https://github.com/leximor)

[Андрей](https://github.com/andreysdrv)

![example workflow](https://github.com/github/docs/actions/workflows/yamdb_workflow.yml/badge.svg)