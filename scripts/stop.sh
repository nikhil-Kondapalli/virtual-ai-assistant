#!/bin/bash

# Stop script for Virtual AI Assistant

echo "🛑 Stopping Virtual AI Assistant..."

# Stop all services
docker-compose down

echo "✅ All services stopped!"
