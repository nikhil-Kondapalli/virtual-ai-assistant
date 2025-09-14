# Stage 1: Builder
# This stage installs all build dependencies and downloads the models.
FROM python:3.11 as builder

# Install system dependencies needed for building wheels
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set up a virtual environment in a standard location
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy and install requirements into the virtual environment
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download/pre-cache the TTS model within the builder stage.
# This runs the TTS library we just installed and makes it download the model
# to the default cache location (/root/.local/share/tts).
RUN python -c "from TTS.api import TTS; TTS(model_name='tts_models/en/ljspeech/speedy-speech', gpu=False)"


# Stage 2: Final Image
# This stage starts from a slim image and copies only the necessary artifacts.
FROM python:3.11-slim

# Install only the necessary RUNTIME system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Copy the downloaded TTS model from the builder stage's cache.
COPY --from=builder /root/.local/share/tts /root/.local/share/tts

# Activate the virtual environment
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# Copy the application code
COPY . .

EXPOSE 8002

# Use the non-reloading command for production images
CMD ["uvicorn", "tts_worker:app", "--host", "0.0.0.0", "--port", "8002"]