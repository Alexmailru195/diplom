Проект diplom — это Django-приложение, предназначенное для управления интернет-магазином. В нём реализованы функции:

Добавление и управление товаром 

Перемещение товара между точками

Списание товара

Отслеживание истории изменений остатков

Уведомления о низком уровне запасов

Проект написан с использованием фреймворка Django и может работать с базой данных SQL Server или PostgreSQL.

1. Клонировать репозиторий

git clone https://github.com/Alexmailru195/diplom.git 

cd diplom

2. Создать и активировать виртуальное окружение

Windows:

python -m venv venv

.\venv\Scripts\activate

Linux/macOS:

python3 -m venv venv

source venv/bin/activate

3. Установить зависимости

pip install -r requirements.txt

4. Настроить подключение к базе данных

В файле env отредактируйте параметры подключения к вашей БД.

5. Выполнить создания миграции

python manage.py makemigrations

6. Выполнить миграции

python manage.py migrate

7. Запустить Redis

redis-server

8. Создать суперпользователя

python manage.py createsuperuser

9. Запустить сервер

python manage.py runserver

Тестирование

Тесты находятся в tests.py. Для запуска всех тестов выполните:

python manage.py test

Примечания

Проект содержит полноценный набор моделей, форм, вьюшек и тестов.

Поддерживается работа с SQL Server.

Все действия с инвентарём логируются в истории.

Контакты

Если у вас есть вопросы или предложения по улучшению проекта, пишите мне:

Email: alexmailru195@example.com

MIT License

Copyright (c) 2025 Alexmailru195