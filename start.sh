#!/bin/bash
# Quick start for AstrogyIA backend

echo "🚀 Starting AstrogyIA backend..."

# Start database
echo "📦 Starting PostgreSQL..."
docker compose up -d db

# Wait for DB to be ready
echo "⏳ Waiting for database..."
sleep 3

# Check if DB is healthy
docker compose exec db pg_isready -U astrogyia > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database ready"
else
    echo "❌ Database not ready, try: docker compose logs db"
    exit 1
fi

# Start API
echo "🌐 Starting API server..."
uvicorn chart_engine.api.app:app --reload --port 8000
