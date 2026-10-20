# Информация о рецептах (Django, XML)

Запуск:

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py runserver

Сайт: http://127.0.0.1:8000/

В папке `examples/` лежат корректный (`test.xml`) и некорректный (`bad.xml`) файлы для проверки загрузки.
XML-файлы сохраняются в папку `recipes_files/` (создаётся автоматически).
