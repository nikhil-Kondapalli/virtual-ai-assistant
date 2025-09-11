#!/bin/bash

# Stop script for Anime AI Assistant

echo "🛑 Stopping Anime AI Assistant..."

# Stop all services
docker-compose down

echo "✅ All services stopped!"
