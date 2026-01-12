# Audio Visualizer Docker Image
# Supports GUI via X11 forwarding

FROM python:3.11-slim

LABEL maintainer="Muhammad Ibrahim Kartal <github.com/muhkartal>"
LABEL description="Real-time audio visualizer with spectrum analysis and beat detection"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for audio and graphics
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Audio libraries
    libportaudio2 \
    libsndfile1 \
    libasound2 \
    libasound2-plugins \
    pulseaudio \
    # Graphics/SDL for pygame
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    # X11 for GUI display
    libx11-6 \
    libxext6 \
    libxrender1 \
    # Fonts
    fonts-dejavu-core \
    # FFmpeg for audio format support
    ffmpeg \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd -m -s /bin/bash visualizer \
    && usermod -aG audio,video visualizer

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=visualizer:visualizer . .

# Switch to non-root user
USER visualizer

# Environment variables for audio/display
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV SDL_AUDIODRIVER=pulseaudio
ENV PULSE_SERVER=unix:/run/user/1000/pulse/native

# Expose no ports (GUI application)
# Health check not applicable for GUI apps

# Default command
CMD ["python", "-m", "src.main"]
