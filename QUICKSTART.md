# Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed
- At least 8GB RAM available
- GPU with ?24GB VRAM (optional, for GPT-OSS-20B) or use CPU fallback

## Setup

1. **Clone and navigate to project**
```bash
cd /workspace
```

2. **Start all services**
```bash
docker-compose up -d
```

3. **Initialize database (first time only)**
```bash
docker-compose exec backend python -c "from database import init_db; init_db()"
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

## Admin Panel

1. Go to http://localhost:3000/admin/login
2. Login with:
   - Username: `admin`
   - Password: `admin123`

3. **Load initial data:**
   - Click "????????? XML" to load the product catalog
   - Or upload files (PDF, DOCX, TXT, Markdown)

## First Chat

1. Go to http://localhost:3000
2. Ask a question about products or company
3. Note: You need to load data first via admin panel!

## Troubleshooting

### Backend won't start
- Check logs: `docker-compose logs backend`
- Ensure PostgreSQL and Qdrant are healthy: `docker-compose ps`

### Model loading errors
- The app uses GPT-2 as fallback (CPU-friendly)
- For GPT-OSS-20B, update `MODEL_NAME` in `backend/.env`

### Qdrant connection errors
- Wait for Qdrant to fully start: `docker-compose logs qdrant`
- Check Qdrant health: `curl http://localhost:6333/health`

### Frontend build errors
- Clear cache: `docker-compose exec frontend rm -rf .next node_modules`
- Rebuild: `docker-compose up -d --build frontend`

## Development Mode

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Production Deployment

1. Update `.env` files with production values
2. Change `SECRET_KEY` in `backend/.env`
3. Update `NEXT_PUBLIC_API_URL` in frontend
4. Build: `docker-compose -f docker-compose.prod.yml up -d` (create prod config)

## Notes

- Default model is GPT-2 (smaller, faster)
- For better quality, use GPT-OSS-20B but requires GPU
- XML catalog URL is configurable via `XML_CATALOG_URL` env var
- All chats are logged in PostgreSQL
