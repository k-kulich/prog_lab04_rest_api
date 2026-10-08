# Tutor API

RESTful API сервис для управления репетиторами, учениками, расписанием занятий,
домашними заданиями и материалами (файлами/ссылками).

## Стек

- Python 3.9.6
- FastAPI 0.115
- SQLAlchemy 2.0 (sync)
- SQLite (по умолчанию)
- Pydantic v2
- pytest + FastAPI TestClient

## Быстрый старт

```bash
git clone <repo> && cd tutor_api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Сервис поднимется на `http://127.0.0.1:8000`. Swagger UI — `/docs`, OpenAPI — `/openapi.json`.

## Модели

- __Tutor__ — репетитор (ФИО, email, предмет, bio)
- __Student__ — ученик (ФИО, email, дата рождения, класс 1..11, ссылка на репетитора)
- __Lesson__ — занятие (тема, предмет, время, длительность, ссылка, статус)
- __Homework__ — домашнее задание (описание, дедлайн, статус, оценка)
- __Attachment__ — материалы: ссылка / файл / учебный материал,
  привязаны либо к занятию, либо к ДЗ

## Эндпоинты

Полный CRUD (GET/POST/PATCH/DELETE) для каждой сущности:

```
GET/POST         /api/tutors
GET/PATCH/DELETE /api/tutors/{id}
GET/POST         /api/students
GET/PATCH/DELETE /api/students/{id}
GET/POST         /api/lessons
GET/PATCH/DELETE /api/lessons/{id}
GET/POST         /api/homework
GET/PATCH/DELETE /api/homework/{id}
GET/POST         /api/attachments
GET/PATCH/DELETE /api/attachments/{id}
```

Плюс вложенные:

```
GET /api/tutors/{id}/students
GET /api/tutors/{id}/lessons
GET /api/students/{id}/lessons
GET /api/students/{id}/homework
GET /api/lessons/{id}/homework
GET /api/lessons/{id}/attachments
GET /api/homework/{id}/attachments
```

## Формат ответов

Список: `{"list": [ ... ]}`

Один объект / создание / обновление:
`{"tutor": { ... }}` (ключ = имя сущности)

Удаление: `202 Accepted`, пустое тело.

Ошибки:

```json
{ "status": 400, "reason": "Field 'fio' is required" }
{ "status": 404, "reason": "Tutor with id=42 not found" }
{ "status": 500, "reason": "<причина>" }
```

## Тело запроса для POST/PATCH

Принимается __плоский__ JSON:

```json
{ "fio": "Иван Петров", "email": "i@x.ru", "subject": "Математика" }
```

и __обернутый__:

```json
{ "tutor": { "fio": "Иван Петров", "email": "i@x.ru", "subject": "Математика" } }
```

## Пример запроса

```bash
curl -X POST http://127.0.0.1:8000/api/tutors \
  -H "Content-Type: application/json" \
  -d '{"fio":"Иван Петров","email":"i@x.ru","subject":"Математика"}'
```

## Тесты

```bash
pytest -v
```

Покрыты:

- CRUD всех пяти сущностей
- Вложенные эндпоинты
- Валидация полей (обязательные, диапазоны, дата, email, literal-статусы)
- Формат ошибок 400/404
- Каскадное удаление (FK)
- Cross-field: attachment ровно с одним владельцем
- Cross-field: student из другого репетитора нельзя привязать к занятию

Результаты:

```zsh
============================================================================ test session starts =============================================================================
platform darwin -- Python 3.9.6, pytest-8.3.2, pluggy-1.6.0
rootdir: /Users/ksenia/Documents/itmo/академ разница/прога/lab0-4
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.12.1
collected 39 items                                                                                                                                                           

tests/test_attachments.py ......                                                                                                                                       [ 15%]
tests/test_homework.py ......                                                                                                                                          [ 30%]
tests/test_lessons.py ......                                                                                                                                           [ 46%]
tests/test_students.py .....                                                                                                                                           [ 58%]
tests/test_tutors.py ........                                                                                                                                          [ 79%]
tests/test_validation.py ........                                                                                                                                      [100%]

============================================================================= 39 passed in 0.36s =============================================================================
```

## Структура

```
app/
├── main.py         — FastAPI + exception handlers
├── config.py       — pydantic-settings
├── database.py     — engine, SessionLocal, Base, get_db
├── models.py       — 5 SQLAlchemy моделей
├── schemas.py      — Pydantic Create/Update/Out
├── exceptions.py   — NotFoundError/BadRequestError + handlers
└── routers/        — по одному модулю на сущность
```
