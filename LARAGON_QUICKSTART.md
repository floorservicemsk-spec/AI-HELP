# Быстрый старт для Laragon

## Шаг 1: Установка

1. **Python 3.11+** - скачайте с python.org (отметьте "Add Python to PATH")
2. **Node.js 18+** - скачайте с nodejs.org
3. **Docker Desktop** - скачайте с docker.com

## Шаг 2: Запуск Qdrant

Откройте терминал и выполните:
```bash
docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant
```

## Шаг 3: Запуск проекта

Дважды кликните на файл `start_laragon.bat`

Или вручную:

**Терминал 1:**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Терминал 2:**
```bash
cd frontend
npm run dev
```

## Шаг 4: Откройте приложение

- Фронтенд: http://localhost:3000
- Админка: http://localhost:3000/admin/login (admin/admin123)

## Готово!
