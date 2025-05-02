# Высоконагруженный веб-сервис с nginx

## Описание
Веб-сервис с двумя API-эндпоинтами:
1. GET `/api/dates` - возвращает JSON с 10,000 одинаковыми записями текущей даты
2. POST `/api/names` - возвращает JSON с 10,000 одинаковыми записями имени из POST-параметра

## Установка и запуск

### Зависимости
```bash
pip install -r requirements.txt
```

### Запуск приложения
```bash
# Запуск трех инстансов приложения на разных портах
uvicorn app.main:app --port 8000
uvicorn app.main:app --port 8001
uvicorn app.main:app --port 8002
```

### Запуск nginx
```bash
nginx -c /path/to/ngnix/nginx.conf
```

## Тестирование производительности
Для тестирования производительности можно использовать инструменты:
- Apache Benchmark (ab)
- wrk
- k6

Пример тестирования с Apache Benchmark:
```bash
# Тест без прокси
ab -n 1000 -c 100 http://localhost:8000/api/dates

# Тест с прокси
ab -n 1000 -c 100 http://localhost/api/dates
```

## Структура проекта
- `app/` - исходный код веб-приложения
- `nginx.conf` - конфигурация nginx
- `requirements.txt` - зависимости Python
- `README.md` - документация проекта