### Предварительные требования

Перед началом работы убедитесь, что у вас установлены следующие инструменты:

- Python 3.6 или выше
- pip (менеджер пакетов для Python)


### Установка

Выполните следующие шаги для настройки локальной разработки:

1. Клонируйте репозиторий:
https://github.com/OlegforeverUkr/Meduzzen.git

2. Установите виртуальное окружение:

python -m venv .venv

3. Активируйте виртуальное окружение:
   - Для Windows:
     
     .venv/Scripts/activate
   
   - Для macOS и Linux:
     
     source .venv/bin/activate
     

4. Установите зависимости:
   
   pip install -r requirements.txt


### Конфигурация

Создайте файл .env в корне проекта с необходимыми переменными окружения:


RELOAD=True or False to reload server
HOST=Insert your host
PORT=Insert port for app

### Запуск приложения

Чтобы запустить приложение, перейдите в main.py и запустите приложение


## Тестирование

В терминале вашей среды разработки (IDE) выполните команду "pytest"


## Миграции базы данных

Для создания новой миграции выполните следующую команду:

    alembic revision --autogenerate -m "Описание миграции"

Это создаст файл миграции в папке migrations/versions с автоматически 
сгенерированными изменениями на основе ваших моделей SQLAlchemy.

Чтобы применить миграции к базе данных, выполните команду:

    alembic upgrade хэш ревизии
Или 

    alembic upgrade head

Для применения последней ревизии


Чтобы откатить последнюю миграцию, используйте команду:

    alembic downgrade -1

 
Для отката на несколько шагов назад, укажите вместо -1 нужное количество шагов.



Для запуска worker'a Сelery следует ввести следующую команду - 

    celery -A celery_start_processes worker --loglevel=INFO --pool=solo

Для запуска beat'a Сelery следует ввести следующую команду - 

    celery -A celery_start_processes beat --loglevel=INFO

Для запуска flower следует ввести следующую команду - 

    celery -A celery_start_processes flower --port=5555