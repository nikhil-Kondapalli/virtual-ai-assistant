@echo off
echo Starting Anime AI Assistant...

echo Starting Redis and Ollama...
docker-compose up -d redis ollama

echo Waiting for services to start...
timeout /t 10 /nobreak

echo Pulling Ollama model...
docker exec ai-assistant-ollama-1 ollama pull tinyllama

echo Starting Backend Gateway...
start "Backend Gateway" cmd /k "cd backend-gateway && .\venv\Scripts\activate && python manage.py runserver 0.0.0.0:8000"

echo Starting LLM Worker...
start "LLM Worker" cmd /k "cd worker-llm && .\venv\Scripts\activate && uvicorn llm_worker:app --host 0.0.0.0 --port 8001"

echo Starting TTS Worker...
start "TTS Worker" cmd /k "cd worker-tts && .\venv\Scripts\activate && uvicorn tts_worker:app --host 0.0.0.0 --port 8002"

echo Starting Frontend...
start "Frontend" cmd /k "cd frontend-anime-agent && npm start"

echo All services started!
echo.
echo Access the application at: http://localhost:3000
echo Backend API: http://localhost:8000
echo LLM Worker: http://localhost:8001
echo TTS Worker: http://localhost:8002
echo Ollama: http://localhost:11434
echo.
pause
