
.PHONY: help setup start stop logs build clean test

help: ## Show this help message
	@echo "Virtual AI Assistant - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup of the project
	@echo "🎌 Setting up Virtual AI Assistant..."
	@if [ ! -f .env ]; then cp env.example .env; fi
	@mkdir -p frontend/public/models
	@mkdir -p worker-tts/tts_cache
	@docker-compose build
	@echo "✅ Setup complete! Run 'make start' to begin."

start: ## Start all services
	@echo "🚀 Starting Virtual AI Assistant..."
	@docker-compose up -d
	@echo "✅ Services started! Access at http://localhost:3000"

stop: ## Stop all services
	@echo "🛑 Stopping Virtual AI Assistant..."
	@docker-compose down
	@echo "✅ Services stopped!"

restart: ## Restart all services
	@echo "🔄 Restarting Virtual AI Assistant..."
	@docker-compose restart
	@echo "✅ Services restarted!"

logs: ## View logs from all services
	@echo "📋 Viewing logs (Ctrl+C to exit)..."
	@docker-compose logs -f

build: ## Build all Docker images
	@echo "🔨 Building Docker images..."
	@docker-compose build
	@echo "✅ Build complete!"

clean: ## Clean up Docker resources
	@echo "🧹 Cleaning up Docker resources..."
	@docker-compose down -v
	@docker system prune -f
	@echo "✅ Cleanup complete!"

test: ## Run tests
	@echo "🧪 Running tests..."
	@docker-compose exec gateway python manage.py test
	@echo "✅ Tests complete!"

shell-gateway: ## Open shell in gateway container
	@docker-compose exec gateway bash

shell-llm: ## Open shell in LLM worker container
	@docker-compose exec llm-worker bash

shell-tts: ## Open shell in TTS worker container
	@docker-compose exec tts-worker bash

pull-models: ## Pull Ollama models
	@echo "🤖 Pulling Ollama models..."
	@docker-compose exec ollama ollama pull mistral:7b
	@docker-compose exec ollama ollama pull phi3:mini
	@echo "✅ Models pulled!"

status: ## Show status of all services
	@echo "📊 Service Status:"
	@docker-compose ps
