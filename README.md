# Платформа для онлайн-опросов и анкетирования

Курсовой проект по дисциплине **«Технология разработки программного обеспечения»**.

**Траектория Б**: Django REST + React SPA

## Стек технологий

### Backend
- Python 3.12
- Django 6
- Django REST Framework
- SimpleJWT
- django-cors-headers
- django-filter
- SQLite

### Frontend
- React 19
- Vite
- React Router DOM
- Axios

## Структура проекта

```text
backend/   # Django REST API
frontend/  # React SPA
```

## Запуск проекта

### 1. Backend

```powershell
# активация виртуального окружения
D:\kursovaya\backend\venv\Scripts\Activate.ps1

# если PowerShell блокирует скрипты
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# переход в backend
cd D:\kursovaya\backend

# применение миграций
python manage.py migrate

# создание суперпользователя (опционально)
python manage.py createsuperuser

# запуск сервера
python manage.py runserver
```

Backend будет доступен по адресу:
- `http://127.0.0.1:8000/`
- Админка: `http://127.0.0.1:8000/admin/`
- API: `http://127.0.0.1:8000/api/`

### 2. Frontend

```powershell
cd D:\kursovaya\frontend
npm install
npm run dev
```

Frontend будет доступен по адресу:
- `http://localhost:3000/`

## Основные API-эндпоинты

### Auth
- `POST /api/auth/register/` — регистрация
- `POST /api/auth/login/` — вход (JWT)
- `POST /api/auth/token/refresh/` — обновление access token
- `GET/PATCH /api/auth/profile/` — профиль пользователя

### Surveys
- `GET /api/surveys/` — список опросов
- `POST /api/surveys/` — создать опрос
- `GET /api/surveys/{id}/` — детали опроса
- `GET /api/surveys/my/` — мои опросы
- `GET /api/surveys/{id}/stats/` — статистика
- `POST /api/surveys/{id}/submit_response/` — пройти опрос
- `POST /api/surveys/{id}/increment_views/` — увеличить просмотры

### Other
- `GET /api/categories/` — категории
  (включая стандартные категории и отдельную категорию `Другое`)
- `GET/POST /api/questions/` — вопросы
- `GET/POST /api/comments/` — комментарии
- `GET /api/responses/` — мои ответы

## Тестирование

### Backend
```powershell
cd D:\kursovaya\backend
D:\kursovaya\backend\venv\Scripts\python.exe manage.py test
```

### Frontend
```powershell
cd D:\kursovaya\frontend
npm run build
```

## Реализованный функционал

- Регистрация и авторизация пользователей через JWT
- Создание и редактирование профиля
- Создание опросов и вопросов
- Поддержка стандартных категорий опросов, включая отдельную категорию `Другое`
- Поддержка типов вопросов: один вариант / несколько вариантов / текст
- Прохождение опросов
- Комментарии к опросам
- Статистика по ответам
- Админ-панель Django

## Разработка по этапам

- **Недели 9-10** — Этап 4: создание и настройка Django проекта
- **Недели 11-12** — Этап 5: модели и админ-панель
- **Недели 13-14** — Этап 6: REST API и JWT
- **Недели 15-16** — Этап 7: React SPA
- **Недели 17-18** — Этап 8: тестирование и документация
