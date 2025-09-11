#!/bin/bash

# Setup script for Anime AI Assistant

set -e

echo "🎌 Setting up Anime AI Assistant..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p frontend-anime-agent/public/models
mkdir -p worker-tts/tts_cache

# Pull Docker images
echo "🐳 Pulling Docker images..."
docker-compose pull

# Build services
echo "🔨 Building services..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d redis ollama

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Pull Ollama models
echo "🤖 Setting up Ollama models..."
echo "Available models:"
echo "1. mistral:7b (recommended)"
echo "2. phi3:mini (lightweight)"
echo "3. qwen2.5:7b (alternative)"

read -p "Enter model name (default: mistral:7b): " model_name
model_name=${model_name:-mistral:7b}

echo "📥 Pulling model: $model_name"
docker exec -it ai-assistant-ollama-1 ollama pull $model_name

# Update .env with selected model
sed -i "s/MODEL_NAME=.*/MODEL_NAME=$model_name/" .env

# Start remaining services
echo "🚀 Starting remaining services..."
docker-compose up -d

echo "✅ Setup complete!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Ollama:   http://localhost:11434"
echo ""
echo "📋 Useful commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop all:     docker-compose down"
echo "   Restart:      docker-compose restart"
echo ""
echo "🎯 Next steps:"
echo "   1. Place your Live2D model files in frontend-anime-agent/public/models/"
echo "   2. Customize the persona in the backend configuration"
echo "   3. Adjust TTS settings in worker-tts/"
echo ""
echo "Happy chatting with your anime assistant! 🎌"
