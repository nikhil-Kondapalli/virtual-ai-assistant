FROM ollama/ollama:latest

# Start Ollama server and pull models
RUN ollama serve & \
    sleep 5 && \
    ollama pull tinyllama && \
    ollama pull nomic-embed-text