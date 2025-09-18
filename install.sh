#!/bin/bash

# XIONIMUS AI - Automatisches Installationsskript
# Dystopian Cyberpunk AI System v2.0

set -e

# Farben für Terminal-Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Banner
print_banner() {
    echo -e "${GREEN}"
    echo "██╗  ██╗██╗ ██████╗ ███╗   ██╗██╗███╗   ███╗██╗   ██╗███████╗     █████╗ ██╗"
    echo "╚██╗██╔╝██║██╔═══██╗████╗  ██║██║████╗ ████║██║   ██║██╔════╝    ██╔══██╗██║"
    echo " ╚███╔╝ ██║██║   ██║██╔██╗ ██║██║██╔████╔██║██║   ██║███████╗    ███████║██║"
    echo " ██╔██╗ ██║██║   ██║██║╚██╗██║██║██║╚██╔╝██║██║   ██║╚════██║    ██╔══██║██║"
    echo "██╔╝ ██╗██║╚██████╔╝██║ ╚████║██║██║ ╚═╝ ██║╚██████╔╝███████║    ██║  ██║██║"
    echo "╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝    ╚═╝  ╚═╝╚═╝"
    echo -e "${NC}"
    echo -e "${RED}> DYSTOPIAN_AI_SYSTEM_v2.0${NC}"
    echo -e "${YELLOW}> Automatisches Installationsskript${NC}"
    echo -e "${PURPLE}> WARNING: Unauthorized access detected. Proceed with caution.${NC}"
    echo ""
}

# Logging Funktion
log() {
    echo -e "${GREEN}[XIONIMUS_AI]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# System-Check
check_system() {
    log "Überprüfe System-Voraussetzungen..."
    
    # Check if running on Linux/macOS
    if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "darwin"* ]]; then
        error "Dieses Skript unterstützt nur Linux und macOS"
        exit 1
    fi
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker ist nicht installiert. Bitte installieren Sie Docker first."
        echo "Installation: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check if docker-compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose ist nicht installiert."
        echo "Installation: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        warning "Node.js ist nicht installiert. Verwende Docker-Setup..."
        USE_DOCKER=true
    else
        NODE_VERSION=$(node --version | cut -d 'v' -f 2 | cut -d '.' -f 1)
        if [ "$NODE_VERSION" -lt 18 ]; then
            warning "Node.js Version ist zu alt ($NODE_VERSION). Empfohlen: 18+. Verwende Docker-Setup..."
            USE_DOCKER=true
        fi
    fi
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        warning "Python3 ist nicht installiert. Verwende Docker-Setup..."
        USE_DOCKER=true
    else
        PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
        if [[ $(echo "$PYTHON_VERSION < 3.9" | bc -l) -eq 1 ]]; then
            warning "Python Version ist zu alt ($PYTHON_VERSION). Empfohlen: 3.9+. Verwende Docker-Setup..."
            USE_DOCKER=true
        fi
    fi
    
    log "System-Check abgeschlossen"
}

# Create necessary directories
create_directories() {
    log "Erstelle notwendige Verzeichnisse..."
    
    mkdir -p data/mongodb
    mkdir -p logs
    mkdir -p uploads
    mkdir -p sessions
    mkdir -p backups
    
    log "Verzeichnisse erstellt"
}

# Setup Environment Files
setup_env_files() {
    log "Konfiguriere Umgebungsvariablen..."
    
    # Backend .env
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << EOF
MONGO_URL="mongodb://mongodb:27017"
DB_NAME="xionimus_ai"
CORS_ORIGINS="*"

# Optional: API-Schlüssel (können auch später in der UI hinzugefügt werden)
# PERPLEXITY_API_KEY=your_perplexity_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
# GITHUB_TOKEN=your_github_token_here
EOF
        log "Backend .env Datei erstellt"
    else
        log "Backend .env bereits vorhanden"
    fi
    
    # Frontend .env
    if [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_HOST=localhost
WDS_SOCKET_PORT=3000
GENERATE_SOURCEMAP=false
EOF
        log "Frontend .env Datei erstellt"
    else
        log "Frontend .env bereits vorhanden"
    fi
}

# Create Docker Compose file
create_docker_compose() {
    log "Erstelle Docker Compose Konfiguration..."
    
    cat > docker-compose.yml << EOF
version: '3.8'

services:
  mongodb:
    image: mongo:7
    container_name: xionimus_mongodb
    restart: unless-stopped
    ports:
      - "27017:27017"
    volumes:
      - ./data/mongodb:/data/db
    environment:
      MONGO_INITDB_DATABASE: xionimus_ai

  backend:
    build: ./backend
    container_name: xionimus_backend
    restart: unless-stopped
    ports:
      - "8001:8001"
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
      - ./sessions:/app/sessions
      - ./logs:/app/logs
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - DB_NAME=xionimus_ai
    depends_on:
      - mongodb
    command: uvicorn server:app --host 0.0.0.0 --port 8001 --reload

  frontend:
    build: ./frontend
    container_name: xionimus_frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001
      - WDS_SOCKET_HOST=localhost
      - WDS_SOCKET_PORT=3000
    depends_on:
      - backend
    command: yarn start

volumes:
  mongodb_data:
  node_modules:
EOF
    
    log "Docker Compose Datei erstellt"
}

# Create Dockerfiles
create_dockerfiles() {
    log "Erstelle Dockerfiles..."
    
    # Backend Dockerfile
    cat > backend/Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/sessions /app/logs

EXPOSE 8001

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
EOF
    
    # Frontend Dockerfile
    cat > frontend/Dockerfile << EOF
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile --network-timeout 100000

# Copy application code
COPY . .

EXPOSE 3000

CMD ["yarn", "start"]
EOF
    
    log "Dockerfiles erstellt"
}

# Create .dockerignore files
create_dockerignore() {
    log "Erstelle .dockerignore Dateien..."
    
    # Backend .dockerignore
    cat > backend/.dockerignore << EOF
__pycache__
*.pyc
*.pyo
*.pyd
.git
.gitignore
README.md
.env
.venv
env/
venv/
EOF
    
    # Frontend .dockerignore
    cat > frontend/.dockerignore << EOF
node_modules
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.git
.gitignore
README.md
.env.local
.env.development.local
.env.test.local
.env.production.local
build
EOF
    
    log ".dockerignore Dateien erstellt"
}

# Install without Docker (if possible)
install_native() {
    log "Starte native Installation..."
    
    # Install backend dependencies
    if [ -f backend/requirements.txt ]; then
        log "Installiere Python-Abhängigkeiten..."
        cd backend
        pip3 install -r requirements.txt
        cd ..
    fi
    
    # Install frontend dependencies
    if [ -f frontend/package.json ]; then
        log "Installiere Node.js-Abhängigkeiten..."
        cd frontend
        if command -v yarn &> /dev/null; then
            yarn install
        else
            npm install
        fi
        cd ..
    fi
    
    log "Native Installation abgeschlossen"
}

# Start services with Docker
start_docker_services() {
    log "Starte Services mit Docker..."
    
    # Build and start services
    docker-compose build --no-cache
    docker-compose up -d
    
    log "Docker-Services gestartet"
}

# Start services natively
start_native_services() {
    log "Starte Services nativ..."
    
    # Start MongoDB (if not running)
    if ! pgrep -x "mongod" > /dev/null; then
        warning "MongoDB ist nicht gestartet. Bitte starten Sie MongoDB manuell."
        warning "Empfehlung: Verwenden Sie 'docker run -d -p 27017:27017 mongo:7'"
    fi
    
    # Start backend
    cd backend
    python3 -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Wait a bit for backend to start
    sleep 3
    
    # Start frontend
    cd frontend
    if command -v yarn &> /dev/null; then
        yarn start &
    else
        npm start &
    fi
    FRONTEND_PID=$!
    cd ..
    
    log "Native Services gestartet"
    log "Backend PID: $BACKEND_PID"
    log "Frontend PID: $FRONTEND_PID"
}

# Health check
health_check() {
    log "Führe Gesundheitscheck durch..."
    
    # Wait for services to start
    sleep 10
    
    # Check backend
    if curl -s http://localhost:8001/api/health > /dev/null; then
        log "✓ Backend ist erreichbar"
    else
        error "✗ Backend ist nicht erreichbar"
        return 1
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null; then
        log "✓ Frontend ist erreichbar"
    else
        warning "✗ Frontend ist nicht erreichbar (kann noch laden...)"
    fi
    
    log "Gesundheitscheck abgeschlossen"
}

# Create startup script
create_startup_script() {
    log "Erstelle Startup-Skript..."
    
    cat > start.sh << 'EOF'
#!/bin/bash

echo "Starting XIONIMUS AI..."

if [ -f docker-compose.yml ]; then
    echo "Using Docker setup..."
    docker-compose up -d
else
    echo "Using native setup..."
    # Start MongoDB
    if ! pgrep -x "mongod" > /dev/null; then
        echo "Starting MongoDB with Docker..."
        docker run -d -p 27017:27017 --name xionimus_mongo mongo:7
    fi
    
    # Start backend
    cd backend
    python3 -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
    cd ..
    
    # Start frontend
    cd frontend
    if command -v yarn &> /dev/null; then
        yarn start &
    else
        npm start &
    fi
    cd ..
fi

echo "XIONIMUS AI is starting..."
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3000"
echo ""
echo "Wait 30 seconds then open: http://localhost:3000"
EOF
    
    chmod +x start.sh
    log "Startup-Skript erstellt (start.sh)"
}

# Create stop script
create_stop_script() {
    log "Erstelle Stop-Skript..."
    
    cat > stop.sh << 'EOF'
#!/bin/bash

echo "Stopping XIONIMUS AI..."

if [ -f docker-compose.yml ]; then
    echo "Stopping Docker services..."
    docker-compose down
else
    echo "Stopping native services..."
    pkill -f "uvicorn server:app"
    pkill -f "yarn start"
    pkill -f "npm start"
    docker stop xionimus_mongo 2>/dev/null || true
    docker rm xionimus_mongo 2>/dev/null || true
fi

echo "XIONIMUS AI stopped."
EOF
    
    chmod +x stop.sh
    log "Stop-Skript erstellt (stop.sh)"
}

# Print final instructions
print_instructions() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    INSTALLATION COMPLETED!                  ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}> SYSTEM READY. NEURAL NETWORK ONLINE.${NC}"
    echo ""
    echo -e "${YELLOW}Nächste Schritte:${NC}"
    echo -e "1. ${GREEN}Warten Sie 30 Sekunden${NC} bis alle Services gestartet sind"
    echo -e "2. ${GREEN}Öffnen Sie http://localhost:3000${NC} in Ihrem Browser"
    echo -e "3. ${GREEN}Klicken Sie auf das ⚙️ Settings-Icon${NC} um API-Schlüssel zu konfigurieren"
    echo -e "4. ${GREEN}Fügen Sie Ihre API-Schlüssel hinzu:${NC}"
    echo -e "   • Perplexity API: https://www.perplexity.ai/settings/api"
    echo -e "   • Anthropic Claude: https://console.anthropic.com/"
    echo ""
    echo -e "${YELLOW}Verfügbare Befehle:${NC}"
    echo -e "• ${GREEN}./start.sh${NC}  - System starten"
    echo -e "• ${GREEN}./stop.sh${NC}   - System stoppen"
    echo -e "• ${GREEN}docker-compose logs -f${NC} - Logs anzeigen"
    echo ""
    echo -e "${YELLOW}Features:${NC}"
    echo -e "• ${CYAN}8 Spezialisierte AI-Agenten${NC}"
    echo -e "• ${CYAN}GitHub-Integration${NC}"
    echo -e "• ${CYAN}File Upload/Management${NC}"
    echo -e "• ${CYAN}Session Fork/Backup System${NC}"
    echo -e "• ${CYAN}Dystopisches Cyberpunk Design${NC}"
    echo ""
    echo -e "${RED}[WARNING] Autonomous AI active - monitoring recommended${NC}"
    echo ""
}

# Main installation function
main() {
    print_banner
    
    # Ask user for installation type
    echo -e "${YELLOW}Welche Installation möchten Sie?${NC}"
    echo "1) Docker (Empfohlen - Einfach und zuverlässig)"
    echo "2) Native (Erweitert - Benötigt Python 3.9+ und Node.js 18+)"
    echo "3) Auto-Detection (Automatische Auswahl basierend auf System)"
    echo ""
    read -p "Ihre Wahl (1-3): " INSTALL_TYPE
    
    case $INSTALL_TYPE in
        1)
            log "Docker-Installation gewählt"
            USE_DOCKER=true
            ;;
        2)
            log "Native Installation gewählt"
            USE_DOCKER=false
            ;;
        3)
            log "Auto-Detection gewählt"
            check_system
            ;;
        *)
            log "Ungültige Auswahl. Verwende Docker (Standard)"
            USE_DOCKER=true
            ;;
    esac
    
    # Run installation steps
    create_directories
    setup_env_files
    create_startup_script
    create_stop_script
    
    if [ "$USE_DOCKER" = true ]; then
        create_docker_compose
        create_dockerfiles
        create_dockerignore
        start_docker_services
    else
        install_native
        start_native_services
    fi
    
    # Health check
    health_check
    
    # Print final instructions
    print_instructions
}

# Run main function
main "$@"