# Bewise

Приложение представляет собой веб сервис, который принимает POST запрос с содержимым вида {"questions_num": integer}
После получения запроса сервис, в свою очередь, запрашивает с публичного API (англоязычные вопросы для викторин) https://jservice.io/api/random?count=1 указанное в полученном запросе количество вопросов.
Полученные ответы сохраняются в базе данных. А именно: 
- id полученный с api, 
- текст вопроса, 
- текст ответа, 
- значение, 
- airdate, 
- когда было создано, 
- когда было обновлено, 
- id категории, 
- id игры. 

В случае, если в БД имеется такой же вопрос, к публичному API с викторинами выполняются дополнительные запросы до тех пор, пока не будет получен уникальный вопрос для викторины.
В app.py я использовал

    unique_questions = []
    
        while len(unique_questions) < questions_num:
    
            response = requests.get(f'https://jservice.io/api/random?count={questions_num - len(unique_questions)}')
        
        
Объясняю, если к примеру пользователь отправил нам questions_num со значением `10`,
то мы отправляем запрос в публичный API, до тех пор пока значение списка уникальных вопросов (unique_questions) не будет равно questions_num,
который нам отправил пользователь, при этом если у нас уже есть к примеру 5 уникальных вопросов в unique_questions,
то мы делая `questions_num - len(unique_questions)` отправляем запрос `https://jservice.io/api/random?count=5`

Использованы docker-compose, SQLAalchemy,  пользовался аннотацией типов.


# Dockerfile
Dockerfile в данном репозитории определяет контейнер для запуска веб-сервиса. Он устанавливает необходимые зависимости, копирует приложение внутрь контейнера и указывает команду для его запуска.

Определение базового образа

`FROM python:3.9-slim`

Установка зависимостей для psycopg

`RUN apt-get update \
    && apt-get install -y postgresql-client libpq-dev gcc`

Создание рабочей директории /app

`WORKDIR /app`

Копирование файла requirements.txt 

`COPY requirements.txt .`

Установка зависимостей, указанных в файле requirements.txt

`RUN pip install --no-cache-dir -r requirements.txt`

Копирование приложения

`COPY . .`

Запуск приложения

`CMD ["python", "app.py"]`


# docker-compose.yml
docker-compose.yml в данном репозитории определяет сервисы web и db. Он указывает на сборку и настройку контейнера для веб-сервиса web, использование образа PostgreSQL для сервиса db, а также настройки портов и переменных окружения для каждого сервиса

Определение версии compose-файла: version: "3"

Определение сервисов:

`web:`
`db:`

Сборка контейнера для сервиса web из текущего каталога (где находится docker-compose.yml) с использованием Dockerfile.

`build: .`

Пробрасывание порта 8080 на локальной машине на порт 8080 внутри контейнера. Это позволяет обращаться к веб-сервису через порт 8080 на хосте.

`ports: - 8080:8080`

Загрузка переменных окружения из файла .env.

`env_file: - ./.env`

Указание, что сервис web зависит от сервиса db и должен быть запущен после него.

`depends_on: - db`

Использование образа postgres:12 для сервиса db. Это означает, что будет развернут контейнер с PostgreSQL версии 12.

`image: postgres:12`

Загрузка переменных окружения из файла .env.db.

`env_file: - ./.env.db`

Монтирование тома postgres_data для сохранения данных PostgreSQL. Данные будут храниться в каталоге /var/lib/postgresql/data внутри контейнера.

`volumes: - postgres_data:/var/lib/postgresql/data`

Пробрасывание порта 5432 на локальной машине на порт 5432 внутри контейнера. Это позволяет подключаться к базе данных PostgreSQL через порт 5432 на хосте.

`ports: - 5432:5432`

Создание именованного тома postgres_data, который будет использоваться для хранения данных PostgreSQL.

`volumes: postgres_data:`


# Запуск проекта
Для запуска проекта нужно переименовать `.env_example` и `.env.db_example`, в `.env` и `.env.db`, заполнив значения переменных, в .env.db указывается пользователь базы данных, пароль пользователя базы данных и имя базы данных, в .env заполняется полный путь к к базе данных
Таблица для базы данных создаётся в app.py

Команда для запуска с билдом

`docker compose up -d --build`
