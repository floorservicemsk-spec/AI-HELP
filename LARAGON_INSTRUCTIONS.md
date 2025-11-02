# Инструкция по запуску на Laragon

## Пошаговая инструкция

### Шаг 1: Установка необходимых компонентов

#### 1.1 Python 3.11+
1. Скачайте Python 3.11+ с https://www.python.org/downloads/
2. При установке **обязательно** отметьте "Add Python to PATH"
3. Проверьте: `python --version`

#### 1.2 Node.js 18+
1. Скачайте Node.js 18+ с https://nodejs.org/
2. Установите с настройками по умолчанию
3. Проверьте: `node --version`

#### 1.3 Docker Desktop
1. Скачайте с https://www.docker.com/products/docker-desktop/
2. Установите и запустите Docker Desktop

### Шаг 2: Запуск Qdrant

Откройте терминал и выполните:
```bash
docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant
```

Проверьте что контейнер запущен:
```bash
docker ps
```

### Шаг 3: Запуск проекта

**Простой способ** - дважды кликните на `start_laragon.bat`

Скрипт автоматически:
- Проверит наличие Python и Node.js
- Создаст виртуальное окружение
- Установит зависимости
- Создаст файлы конфигурации
- Инициализирует базу данных
- Запустит бэкенд и фронтенд

### Шаг 4: Доступ к приложению

- Фронтенд: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Шаг 5: Первый запуск

1. Откройте http://localhost:3000/admin/login
2. Войдите: `admin` / `admin123`
3. Нажмите "Загрузить XML" для загрузки каталога
4. Вернитесь на главную и задайте вопрос

## Troubleshooting

### Порт занят
Измените порт: `uvicorn main:app --reload --port 8001`

### Qdrant не запускается
```bash
docker start qdrant
```

### Ошибки установки
```bash
python -m pip install --upgrade pip
npm cache clean --force
```
