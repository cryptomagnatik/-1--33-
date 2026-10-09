# Каталог книг

PHP API з Composer та консольний Python-клієнт.
Дані зберігаються в `data/books.json`, без БД.

## Запуск

У першому терміналі:
```bash
composer install
composer start
```

У другому:
```bash
python client.py
```

Клієнт отримує дані через HTTP: http://127.0.0.1:8000/api.php