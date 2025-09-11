#!/bin/bash

# Start script for Anime AI Assistant

set -e

echo "🚀 Starting Anime AI Assistant..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run setup.sh first."
    exit 1
fi

# Start all services
docker-compose up -d

echo "✅ All services started!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Ollama:   http://localhost:11434"
echo ""
echo "📋 View logs with: docker-compose logs -f"
echo "🛑 Stop with: docker-compose down"
