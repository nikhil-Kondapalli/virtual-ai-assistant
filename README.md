# Anime AI Assistant

A monorepo for an anime-style virtualized agent featuring Live2D avatars, real-time chat, and AI-powered responses.

## 🎯 Features

- **Live2D Avatar**: Interactive anime character with expressions and animations
- **Real-time Chat**: WebSocket-based communication with typewriter effects
- **AI Integration**: Open-source LLM support via Ollama (Mistral, Phi3, Qwen, TinyLlama)
- **Text-to-Speech**: Coqui TTS with anime-style voices
- **Scalable Architecture**: Microservices with Redis pub/sub backbone
- **Modern UI**: React + TypeScript + ShadCN components

## 🏗️ Architecture

```

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Gateway       │    │   Workers       │
│   (React)       │◄──►│   (Django)      │◄──►│   (FastAPI)     │
│   - Live2D      │    │   - WebSockets  │    │   - LLM Worker  │
│   - Chat UI     │    │   - Auth        │    │   - TTS Worker  │
│   - Audio       │    │   - Sessions    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │   (Pub/Sub)     │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ai-assistant
cp env.example .env
```

### 2. Start Services

To build the application for first time, run the following command in your terminal:

```bash
docker-compose up --build
```

To restart the build, run the following command in your terminal:

```bash
docker-compose restart
```

To start all services, run the following command in your terminal:

```bash
docker-compose up -d
```

To check logs of the particular service, run the following command in your terminal:

```bash
docker-compose logs <service-name>
```

This command will start all the services defined in the `docker-compose.yml` file in detached mode, meaning they will run in the background.

### 3. Initialize Ollama Models

```bash

# Pull a model (choose one)
docker exec -it ai-assistant-ollama-1 ollama pull mistral:7b
docker exec -it ai-assistant-ollama-1 ollama pull phi3:mini
docker exec -it ai-assistant-ollama-1 ollama pull qwen2.5:7b
docker exec -it ai-assistant-ollama-1 ollama pull tinyllama    # we are using this one
```

### 4. Access the Application

- **Frontend**: <http://localhost:3000>
- **Backend API**: <http://localhost:8000>
- **LLM Worker**: <http://localhost:8001>
- **TTS Worker**: <http://localhost:8002>
- **Ollama**: <http://localhost:11434>

## Docker Commands Explained

The `docker-compose.yml` file defines the following services:

- **`redis`**: A Redis in-memory data store used as a message broker for communication between the gateway and the workers.
  - `image: redis:7-alpine`: Specifies the Redis Docker image to use.
  - `ports: - "6379:6379"`: Maps port 6379 on the host to port 6379 in the container.
  - `volumes: - redis_data:/data`: Creates a named volume `redis_data` to persist Redis data.
  - `command: redis-server --appendonly yes`: Starts the Redis server with the "append only" persistence mode enabled.
- **`gateway`**: The backend gateway responsible for handling WebSocket connections, user authentication, and session management.
  - `build: context: ./backend-gateway`: Builds the Docker image for the gateway service using the `Dockerfile` in the `backend-gateway` directory.
  - `ports: - "8000:8000"`: Maps port 8000 on the host to port 8000 in the container.
  - `environment`: Sets environment variables for the service.
  - `depends_on: - redis`: Specifies that the `gateway` service depends on the `redis` service.
  - `volumes: - ./backend-gateway:/app`: Mounts the `backend-gateway` directory on the host to the `/app` directory in the container for local development.
  - `command: daphne -b 0.0.0.0 -p 8000 backend_gateway.asgi_websocket:application`: Starts the Daphne ASGI server to handle WebSocket connections.
- **`llm-worker`**: A worker service that integrates with Ollama to provide AI-powered responses.
  - `build: context: ./worker-llm`: Builds the Docker image for the `llm-worker` service.
  - `environment`: Sets environment variables for the service, including the Redis and Ollama URLs.
  - `depends_on: - redis - ollama`: Specifies that the `llm-worker` service depends on the `redis` and `ollama` services.
  - `volumes: - ./worker-llm:/app`: Mounts the `worker-llm` directory for local development.
- **`tts-worker`**: A worker service that uses Coqui TTS to generate anime-style voices.
  - `build: context: ./worker-tts`: Builds the Docker image for the `tts-worker` service.
  - `environment`: Sets the Redis URL.
  - `depends_on: - redis`: Specifies that the `tts-worker` service depends on the `redis` service.
  - `volumes: - ./worker-tts:/app - tts_models:/root/.local/share/tts`: Mounts the `worker-tts` directory and a named volume `tts_models` to persist the TTS models.
- **`ollama`**: The Ollama service for running large language models.
  - `build: context: ./ollama`: Builds the Docker image for the `ollama` service.
  - `ports: - "11434:11434"`: Maps port 11434 on the host to port 11434 in the container.
  - `volumes: - ollama_data:/root/.ollama`: Creates a named volume `ollama_data` to persist the Ollama models.
  - `restart: unless-stopped`: Configures the service to restart automatically unless it is stopped manually.
- **`frontend`**: The React frontend for the application.
  - `build: context: ./frontend-anime-agent`: Builds the Docker image for the `frontend` service.
  - `ports: - "3000:3000"`: Maps port 3000 on the host to port 3000 in the container.
  - `environment`: Sets environment variables for the React application.
  - `depends_on: - gateway`: Specifies that the `frontend` service depends on the `gateway` service.
  - `volumes: - ./frontend-anime-agent:/app - /app/node_modules`: Mounts the `frontend-anime-agent` directory for local development, and creates an anonymous volume for `node_modules` to prevent it from being overwritten by the host's `node_modules` directory.

### Volumes

- **`redis_data`**: Persists Redis data.
- **`ollama_data`**: Persists Ollama models.
- **`tts_models`**: Persists Coqui TTS models.

## 📁 Project Structure

```

monorepo/
├── docker-compose.yml          # Service orchestration
├── backend-gateway/            # Django gateway
│   ├── backend_gateway/        # Django project
│   ├── chat/                   # Chat app with WebSockets
│   └── Dockerfile
├── worker-llm/                 # FastAPI LLM worker
│   ├── llm_worker.py          # Ollama integration
│   └── Dockerfile
├── worker-tts/                 # FastAPI TTS worker
│   ├── tts_worker.py          # Coqui TTS integration
│   └── Dockerfile
├── frontend-anime-agent/       # React frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── live2d/           # Live2D integration
│   │   ├── stores/           # Zustand state management
│   │   ├── ws/               # WebSocket client
│   │   └── audio/            # Audio handling
│   └── Dockerfile
├── infra/k8s/                 # Kubernetes configs (optional)
└── ops/                       # Monitoring & observability
    ├── prometheus/
    ├── grafana/
    └── sentry/
```

## 🔧 Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

```bash
# Backend Gateway
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://redis:6379/0

# LLM Worker
OLLAMA_HOST=http://ollama:11434
MODEL_NAME=mistral:7b

# TTS Worker
TTS_MODEL=tts_models/en/ljspeech/tacotron2-DDC

# Frontend
REACT_APP_WS_URL=ws://localhost:8000/ws/
REACT_APP_API_URL=http://localhost:8000/api/
```

### Live2D Models

Place your Live2D models in `frontend-anime-agent/public/models/`:

```
public/models/
├── kira.model3.json
├── kira.moc3
├── kira.physics3.json
└── textures/
    ├── kira.2048.png
    └── ...
```

## 📡 Message Protocol

### WebSocket Events

```typescript
// Session metadata
{ "type": "meta", "id": "sess123", "persona": "kira_v1" }

// LLM token streaming
{ "type": "llm_token", "id": "sess123", "token": "Hello" }

// TTS audio chunks
{ "type": "tts_chunk", "id": "sess123", "seq": 3, "format": "opus", "data": "<base64>" }

// Animation triggers
{ "type": "anim", "id": "sess123", "tag": "smile" }

// Session end
{ "type": "end", "id": "sess123" }
```

### Redis Channels

- **Input**: `session:{id}:in` - Messages from gateway to workers
- **Output**: `session:{id}:out` - Messages from workers to gateway

## 🛠️ Development

### Local Development

```bash
# Backend
cd backend-gateway
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend-anime-agent
npm install
npm start

# Workers
cd worker-llm
pip install -r requirements.txt
uvicorn llm_worker:app --reload

cd worker-tts
pip install -r requirements.txt
uvicorn tts_worker:app --reload
```

### Adding New Features

1. **New Animation**: Add to `Live2DManager.ts` motion mapping
2. **New Voice**: Configure in `tts_worker.py` model loading
3. **New LLM Model**: Update `llm_worker.py` model configuration
4. **New UI Component**: Add to `src/components/`

## 🚀 Deployment

### Production Docker Compose

```yaml
# docker-compose.prod.yml
version: "3.8"
services:
  gateway:
    build: ./backend-gateway
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped

  # ... other services
```

### Kubernetes (Optional)

```bash
kubectl apply -f infra/k8s/
```

## 📊 Monitoring

- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and visualization
- **Sentry**: Error tracking and performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Live2D model not loading**: Check model files in `public/models/`
2. **WebSocket connection failed**: Verify gateway is running on port 8000
3. **TTS not working**: Check Coqui TTS model installation
4. **LLM not responding**: Verify Ollama model is pulled and running

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f gateway
docker-compose logs -f llm-worker
docker-compose logs -f tts-worker
```

## 🔮 Future Enhancements

- [ ] Voice input support
- [ ] Multiple avatar support
- [ ] Emotion detection
- [ ] Custom model training
- [ ] Mobile app
- [ ] VR/AR integration
