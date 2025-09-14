# PowerShell script to start all services
Write-Host "Starting Virtual AI Assistant..." -ForegroundColor Green

# Start Redis and Ollama
Write-Host "Starting Redis and Ollama..." -ForegroundColor Yellow
docker-compose up -d redis ollama

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Pull Ollama model
Write-Host "Pulling Ollama model..." -ForegroundColor Yellow
docker exec ai-assistant-ollama-1 ollama pull tinyllama

# Start Backend Gateway
Write-Host "Starting Backend Gateway..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend-gateway; .\venv\Scripts\Activate.ps1; daphne -b 0.0.0.0 -p 8000 backend_gateway.asgi:application"

# Start LLM Worker
Write-Host "Starting LLM Worker..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd worker-llm; .\venv\Scripts\Activate.ps1; uvicorn llm_worker:app --host 0.0.0.0 --port 8001"

# Start TTS Worker
Write-Host "Starting TTS Worker..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd worker-tts; .\venv\Scripts\Activate.ps1; uvicorn tts_worker:app --host 0.0.0.0 --port 8002"

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"

Write-Host "All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "LLM Worker: http://localhost:8001" -ForegroundColor Cyan
Write-Host "TTS Worker: http://localhost:8002" -ForegroundColor Cyan
Write-Host "Ollama: http://localhost:11434" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
