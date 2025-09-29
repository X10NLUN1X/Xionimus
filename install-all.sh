#!/bin/bash

# =============================================================================
# Emergent-Next Automatic Installation Script
# =============================================================================
# This script automatically installs all dependencies and sets up the
# development environment for the Emergent-Next platform
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo ""
    echo -e "${BLUE}==============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}==============================================================================${NC}"
    echo ""
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. This is fine for container environments."
    fi
}

# Check system requirements
check_system_requirements() {
    log_header "CHECKING SYSTEM REQUIREMENTS"
    
    # Check for required commands
    local required_commands=("curl" "wget" "git")
    for cmd in "${required_commands[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            log_success "$cmd is installed"
        else
            log_error "$cmd is not installed. Please install it first."
            exit 1
        fi
    done
}

# Install Node.js and Yarn
install_nodejs_yarn() {
    log_header "INSTALLING NODE.JS AND YARN"
    
    # Check if Node.js is installed
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_info "Node.js is already installed: $NODE_VERSION"
        
        # Check if version is sufficient (>= 18)
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
        if [ "$NODE_MAJOR" -lt 18 ]; then
            log_warning "Node.js version is too old. Installing latest version..."
            install_node=true
        else
            install_node=false
        fi
    else
        log_info "Node.js not found. Installing..."
        install_node=true
    fi
    
    if [ "$install_node" = true ]; then
        # Install Node.js via NodeSource repository
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        apt-get install -y nodejs
        log_success "Node.js installed: $(node --version)"
    fi
    
    # Check if Yarn is installed
    if command -v yarn &> /dev/null; then
        YARN_VERSION=$(yarn --version)
        log_success "Yarn is already installed: $YARN_VERSION"
    else
        log_info "Installing Yarn..."
        npm install -g yarn
        log_success "Yarn installed: $(yarn --version)"
    fi
}

# Install Python dependencies
install_python_dependencies() {
    log_header "INSTALLING PYTHON DEPENDENCIES"
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        log_success "Python3 is installed: $PYTHON_VERSION"
    else
        log_error "Python3 is not installed. Please install Python 3.10 or higher."
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        log_success "pip3 is available"
    else
        log_info "Installing pip3..."
        apt-get update
        apt-get install -y python3-pip
    fi
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip3 install --upgrade pip
    
    # Install backend dependencies
    log_info "Installing Python backend dependencies..."
    cd /app/emergent-next/backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    pip install -r requirements.txt
    
    log_success "Python dependencies installed successfully"
    cd /app
}

# Install MongoDB
install_mongodb() {
    log_header "SETTING UP MONGODB"
    
    # Check if MongoDB is already running
    if systemctl is-active --quiet mongodb || systemctl is-active --quiet mongod; then
        log_success "MongoDB is already running"
        return
    fi
    
    # Check if MongoDB is installed
    if command -v mongod &> /dev/null; then
        log_info "MongoDB is installed, starting service..."
        systemctl start mongodb || systemctl start mongod || true
    else
        log_info "Installing MongoDB..."
        
        # Import MongoDB public key
        wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | apt-key add -
        
        # Add MongoDB repository
        echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
        
        # Update package list
        apt-get update
        
        # Install MongoDB
        apt-get install -y mongodb-org
        
        # Start and enable MongoDB
        systemctl start mongod
        systemctl enable mongod
        
        log_success "MongoDB installed and started"
    fi
}

# Install frontend dependencies
install_frontend_dependencies() {
    log_header "INSTALLING FRONTEND DEPENDENCIES"
    
    cd /app/emergent-next/frontend
    
    # Remove conflicting lock files
    if [ -f "package-lock.json" ]; then
        log_info "Removing package-lock.json to avoid conflicts with yarn..."
        rm package-lock.json
    fi
    
    # Remove node_modules to ensure clean install
    if [ -d "node_modules" ]; then
        log_info "Removing existing node_modules for clean install..."
        rm -rf node_modules
    fi
    
    # Install dependencies with Yarn
    log_info "Installing frontend dependencies with Yarn..."
    yarn install
    
    log_success "Frontend dependencies installed successfully"
    cd /app
}

# Fix CORS configuration
fix_cors_configuration() {
    log_header "FIXING CORS CONFIGURATION"
    
    # Update backend CORS settings
    log_info "Updating backend CORS configuration..."
    
    # Backup original main.py
    cp /app/emergent-next/backend/main.py /app/emergent-next/backend/main.py.backup
    
    # Update CORS settings to include port 3000
    sed -i 's/allow_origins=\[/allow_origins=[\
        "http:\/\/localhost:3000",\
        "http:\/\/127.0.0.1:3000",/' /app/emergent-next/backend/main.py
    
    log_success "CORS configuration updated"
}

# Create startup scripts
create_startup_scripts() {
    log_header "CREATING STARTUP SCRIPTS"
    
    # Create backend startup script
    cat > /app/emergent-next/start-backend.sh << 'EOF'
#!/bin/bash
cd /app/emergent-next/backend
source venv/bin/activate
python main.py
EOF
    chmod +x /app/emergent-next/start-backend.sh
    
    # Create frontend startup script
    cat > /app/emergent-next/start-frontend.sh << 'EOF'
#!/bin/bash
cd /app/emergent-next/frontend
yarn dev
EOF
    chmod +x /app/emergent-next/start-frontend.sh
    
    # Create combined startup script
    cat > /app/emergent-next/start-all.sh << 'EOF'
#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Emergent-Next Development Environment...${NC}"

# Function to kill processes on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Start MongoDB if not running
if ! pgrep -x "mongod" > /dev/null; then
    echo -e "${GREEN}Starting MongoDB...${NC}"
    sudo systemctl start mongod
fi

# Start backend
echo -e "${GREEN}Starting Backend (Port 8002)...${NC}"
cd /app/emergent-next/backend
source venv/bin/activate
python main.py > backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo -e "${GREEN}Starting Frontend (Port 3000)...${NC}"
cd /app/emergent-next/frontend
yarn dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# Display access information
echo ""
echo -e "${GREEN}=== EMERGENT-NEXT STARTED SUCCESSFULLY ===${NC}"
echo -e "${BLUE}Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}Backend:${NC}  http://localhost:8002"
echo -e "${BLUE}API Docs:${NC} http://localhost:8002/docs"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for processes
wait
EOF
    chmod +x /app/emergent-next/start-all.sh
    
    log_success "Startup scripts created"
}

# Verify installation
verify_installation() {
    log_header "VERIFYING INSTALLATION"
    
    # Check Python dependencies
    cd /app/emergent-next/backend
    source venv/bin/activate
    if python -c "import fastapi, uvicorn, motor, pymongo" 2>/dev/null; then
        log_success "Python dependencies verified"
    else
        log_error "Python dependencies verification failed"
    fi
    
    # Check frontend dependencies
    cd /app/emergent-next/frontend
    if [ -d "node_modules" ] && [ -f "node_modules/.yarn-integrity" ]; then
        log_success "Frontend dependencies verified"
    else
        log_error "Frontend dependencies verification failed"
    fi
    
    # Check MongoDB
    if systemctl is-active --quiet mongodb || systemctl is-active --quiet mongod; then
        log_success "MongoDB is running"
    else
        log_warning "MongoDB is not running. Please start it manually."
    fi
    
    cd /app
}

# Create environment files if they don't exist
create_env_files() {
    log_header "CREATING ENVIRONMENT FILES"
    
    # Backend .env
    if [ ! -f "/app/emergent-next/backend/.env" ]; then
        log_info "Creating backend .env file..."
        cat > /app/emergent-next/backend/.env << 'EOF'
# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017/emergent_next

# AI API Keys (configure these for AI features)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
PERPLEXITY_API_KEY=

# Application Settings
DEBUG=true
HOST=0.0.0.0
PORT=8002
LOG_LEVEL=INFO

# Security
SECRET_KEY=emergent-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# File Upload (250MB limit)
MAX_FILE_SIZE=262144000
UPLOAD_DIR=uploads
WORKSPACE_DIR=workspace
EOF
        log_success "Backend .env file created"
    else
        log_info "Backend .env file already exists"
    fi
    
    # Frontend .env
    if [ ! -f "/app/emergent-next/frontend/.env" ]; then
        log_info "Creating frontend .env file..."
        cat > /app/emergent-next/frontend/.env << 'EOF'
VITE_BACKEND_URL=http://localhost:8002
EOF
        log_success "Frontend .env file created"
    else
        log_info "Frontend .env file already exists"
    fi
}

# Main installation function
main() {
    log_header "EMERGENT-NEXT AUTOMATIC INSTALLATION"
    log_info "Starting automatic installation of all dependencies..."
    
    # Update system packages
    log_info "Updating system packages..."
    apt-get update
    
    # Run installation steps
    check_root
    check_system_requirements
    install_nodejs_yarn
    install_python_dependencies
    install_mongodb
    install_frontend_dependencies
    fix_cors_configuration
    create_env_files
    create_startup_scripts
    verify_installation
    
    # Final success message
    log_header "INSTALLATION COMPLETED SUCCESSFULLY!"
    echo ""
    log_success "All dependencies have been installed successfully!"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "1. Configure your AI API keys in: ${YELLOW}/app/emergent-next/backend/.env${NC}"
    echo -e "2. Start the application: ${YELLOW}cd /app/emergent-next && ./start-all.sh${NC}"
    echo -e "3. Access the application at: ${YELLOW}http://localhost:3000${NC}"
    echo ""
    echo -e "${BLUE}Available scripts:${NC}"
    echo -e "- ${YELLOW}./start-all.sh${NC}     - Start both backend and frontend"
    echo -e "- ${YELLOW}./start-backend.sh${NC}  - Start only backend"
    echo -e "- ${YELLOW}./start-frontend.sh${NC} - Start only frontend"
    echo ""
    log_info "Installation log can be found in this terminal output."
}

# Run main function
main "$@"