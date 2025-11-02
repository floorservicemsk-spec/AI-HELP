# RAG Chatbot - AI-помощник для компании

Веб-приложение (PWA) с AI-чатботом для получения информации о компании и товарах.

## Архитектура

- **Фронтенд**: Next.js + React + Tailwind CSS + PWA
- **Бэкенд**: FastAPI + Python
- **RAG**: SentenceTransformer + Qdrant
- **LLM**: GPT-OSS-20B (Hugging Face) / GPT-2 (fallback)
- **База данных**: PostgreSQL + Qdrant

## Быстрый старт

### Требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)
- Node.js 18+ (для локальной разработки)

### Запуск с Docker Compose

```bash
# Клонировать репозиторий
git clone <repository-url>
cd <repository-name>

# Запустить все сервисы
docker-compose up -d

# Инициализировать базу данных (в первом запуске)
docker-compose exec backend python -c "from database import init_db; init_db()"

# Открыть в браузере
# Фронтенд: http://localhost:3000
# Бэкенд API: http://localhost:8000
# Qdrant UI: http://localhost:6333/dashboard
```

### Локальная разработка

#### Бэкенд

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Создать .env файл из .env.example
cp .env.example .env

# Запустить сервер
uvicorn main:app --reload
```

#### Фронтенд

```bash
cd frontend
npm install

# Создать .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Запустить сервер разработки
npm run dev
```

## Использование

### Пользовательский интерфейс

1. Откройте http://localhost:3000
2. Задайте вопрос о компании или товарах
3. Получите ответ на основе данных из базы знаний

### Админ-панель

1. Откройте http://localhost:3000/admin/login
2. Войдите с учетными данными (по умолчанию: admin / admin123)
3. Загрузите XML каталог или файлы
4. Просмотрите статистику использования

## API Endpoints

### Пользовательские

- `POST /api/chat` - Отправка вопроса в чат

### Административные (требуют авторизации)

- `POST /api/auth/login` - Авторизация
- `POST /api/admin/ingest/xml` - Загрузка XML
- `POST /api/admin/ingest/file` - Загрузка файла
- `GET /api/admin/stats` - Статистика
- `POST /api/admin/reindex` - Переиндексация

## Конфигурация

Настройки можно изменить в файлах:

- `backend/.env` - настройки бэкенда
- `docker-compose.yml` - настройки Docker
- `frontend/.env.local` - настройки фронтенда

## Структура проекта

```
.
├── backend/           # FastAPI бэкенд
│   ├── api/          # API роутеры
│   ├── services/     # Сервисы (RAG, LLM, Ingestion)
│   ├── database.py   # Модели БД
│   └── main.py       # Точка входа
├── frontend/         # Next.js фронтенд
│   ├── pages/        # Страницы
│   ├── store/        # State management
│   └── lib/          # Утилиты
└── docker-compose.yml # Docker конфигурация
```

## Примечания

- По умолчанию используется GPT-2 как fallback модель. Для использования GPT-OSS-20B измените `MODEL_NAME` в `.env`
- Убедитесь, что у вас достаточно GPU памяти (≥24GB) для GPT-OSS-20B
- XML каталог автоматически загружается при первом запуске (если настроено)

## Лицензия

MIT
