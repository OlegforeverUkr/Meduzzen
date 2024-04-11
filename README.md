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
