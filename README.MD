# graphql
Тестовый проект с использованием web-socket обновлений

Суть проекта: пользователь может просматривать новости, если новость срочная, приходит уведомление. 
Пользователь может оставлять комментарии под новостью, другие пользователи могут отслеживать это в лайв режиме. 


## Разворачиваем проект локально
Проект использует python версии 3.9
 - Создаем виртуальное окружение
   ##### virtualenv --python=python3.9 venv
 - Устанавливаем необходимые для работы проекта библиотеки из файла зависимостей
   ##### pip install -r requirements.txt
 - Установить базу данных postgresql
 - В корне проекта создать файл .env 
 - Файл содержит данные необходимые для подключения к БД, имя БД, имя пользователя, пароль, хост, порт
   
```
DATABASE_NAME= db_name
DATABASE_USER= db_user
DATABASE_PASSWORD= db_password
DATABASE_HOST= localhost
DATABASE_PORT = 5432
```
 - Для создания структур в БД, необходимо запустить миграции с помощью команды
   ##### python manage.py migrate
 - Чтобы создать суперпользователя для использования админ панели выполняем команду:
   ##### python manage.py createsuperuser
 - Чтобы запустить проект не локальном сервере выполняем команду:
   ##### python manage.py runserver
 - По адресу http://127.0.0.1:8000/try находится интерактивный интерфейс запросов GraphiQL
 - По адресу http://127.0.0.1:8000/admin входим в админ панель



# Логика с запросами

Регистрация пользователя 
```
mutation Register{
  register(password:"password", username: "new_user"){
    user{
      username
      password
    }
  }
}

```
Ответ: 
```
{
  "data": {
    "register": {
      "user": {
        "username": "new_user",
        "password": "password",
      }
    }
  }
}
```
Создание токена: 
```
mutation TokenAuth{
  tokenAuth(
    username: "new_user", 
    password:"password"
  )
  {
   token
  }
}
```
Ответ:
```
{
  "data": {
    "tokenAuth": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImVzZmEiLCJleHAiOjE2MzIxNDgyNzEsIm9yaWdJYXQiOjE2MzIxNDc5NzF9.tFf5Ig1sr1fovAv11yJZyPQg4pJM-WyVby-O6MfdnEc"
    }
  }
}
```
Верификация токена: 
```
mutation VerifyToken{
  verifyToken(token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImVzZmEiLCJleHAiOjE2MzIxNDgyNzEsIm9yaWdJYXQiOjE2MzIxNDc5NzF9.tFf5Ig1sr1fovAv11yJZyPQg4pJM-WyVby-O6MfdnEc"
  )
  {
   payload
  }
}
```
Ответ:
```
{
  "data": {
    "verifyToken": {
      "payload": {
        "username": "new_user",
        "exp": 1631726550,
        "origIat": 1631726250
      }
    }
  }
}
```
Пользователь обладающий стафф правами добавляет новости, breaking:true если новость срочная: 
```
mutation AddNews($image: Upload) {
  add_news(
    text: "some text"
    title: "News title"
    breaking: true
    image: $image
  ) {
    message
    success
  }
}
```
Ответ: 
```
{
  "data": {
    "add_news": {
      "message": "News added",
      "success": true
    }
  }
}
```
Пользователь может подписаться на срочные новости
```
subscription NewsSubscription {
  breaking_news {
    news_id
    news_title
  }
}

```
В случае если появляется новая новость с пометкой срочно, ему приходит обновление
Ответ:
```
 {
  "data": {
    "breaking_news": {
      "news_id": 33,
      "news_title": "News title"
    }
  }
} 
```
Пользователь может просматривать новости:
```
query News{
  news{
    text
    title
    image
    breaking
    created_at
  }
}
```
Ответ: 
```
{
  "data": {
    "news": [
      {
        "text": "some text",
        "title": "News title",
        "image": "",
        "breaking": true,
        "created_at": "2021-10-15T12:17:40.793198+00:00"
      },
      {
        "text": "some text",
        "title": "happy bd Akim",
        "image": "",
        "breaking": true,
        "created_at": "2021-10-15T07:14:12.288731+00:00"
      },
      {
        "text": "some text",
        "title": "sfsdf",
        "image": "",
        "breaking": true,
        "created_at": "2021-10-14T14:56:35.904607+00:00"
      },
      {
        "text": "some text",
        "title": "new news",
        "image": "news/2021/10/13/Без_имени.png",
        "breaking": false,
        "created_at": "2021-10-13T14:18:58.185193+00:00"
      },
      
```
Пользователь может просмотреть одну новость с комментариями под ней
```
query News{
  news_one(id:31){
    id
    text
    title
    image
    breaking
    created_at
    comments{
      text
      user{
        username
      }
      created_at
    }
  }
}
```
Ответ:
```
{
  "data": {
    "news_one": {
      "id": "31",
      "text": "some text",
      "title": "happy birth day",
      "image": "",
      "breaking": true,
      "created_at": "2021-10-15T10:05:41.664690+00:00",
      "comments": [
        {
          "text": "Комментарий к новости",
          "user": {
            "username": "new_user"
          },
          "created_at": "2021-10-15T12:32:04.675057+00:00"
        }
      ]
    }
  }
}
```

Пользователь может добавить комментарий к новости 
```
mutation AddComents{
  add_comment(news_id:31, text: "Комментарий к новости"){
    message
    success
  }
}
```
Ответ:
```
{
  "data": {
    "add_comment": {
      "message": "comment added",
      "success": true
    }
  }
}
```

Пользователь может подписаться на обновления комментариев конкретной новости:
```
subscription Comment{
  comment_subscription(news_id: 31){
    username
    comment_text
    news_id
  }
}

```
Тогда при добавлении комментария к отслеживаемой новости приходит обновление
Ответ:
```
{
  "data": {
    "comment_subscription": {
      "username": "new_user",
      "comment_text": "Новый комментарий новости",
      "news_id": 31
    }
  }
} 
```