#!/bin/bash

# ============================================================================
# Docker Setup Script for Question App
# ============================================================================
# This script automates the initial Docker setup process
# Usage: ./docker-setup.sh
# ============================================================================

set -e  # Exit on any error

echo "🐳 Question App - Docker Setup"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker is installed: $(docker --version)"
echo "✅ Docker Compose is installed: $(docker-compose --version)"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.docker.template .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your credentials:"
    echo "   - Azure OpenAI credentials"
    echo "   - Canvas LMS credentials"
    echo ""
    echo "   Run: nano .env"
    echo ""
    read -p "Press Enter after you've configured .env, or Ctrl+C to exit..."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🔨 Building Docker images..."
echo "This may take a few minutes on first run..."
echo ""

# Build images
docker-compose build

echo ""
echo "✅ Docker images built successfully!"
echo ""
echo "🚀 Starting services..."
echo ""

# Start services
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Access your application:"
echo "   - Application: http://localhost:8080"
echo "   - ChromaDB:    http://localhost:8000"
echo "   - Ollama:      http://localhost:11434"
echo ""
echo "📝 Useful commands:"
echo "   - View logs:        docker-compose logs -f"
echo "   - Stop services:    docker-compose down"
echo "   - Restart:          docker-compose restart"
echo ""
echo "🎉 Happy coding!"
