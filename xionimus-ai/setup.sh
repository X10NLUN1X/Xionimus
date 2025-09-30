#!/bin/bash

#############################################
# Xionimus AI - One-Click Setup Script
# Version: 1.0.0
# Description: Automated setup for Xionimus AI
#############################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print formatted messages
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   Xionimus AI - Setup Script v1.0.0   ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}➜${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Main setup function
main() {
    print_header
    
    OS=$(detect_os)
    print_step "Detected OS: $OS"
    echo ""
    
    # Step 1: Check prerequisites
    print_step "Step 1/6: Checking prerequisites..."
    
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        echo "Visit: https://nodejs.org/"
        exit 1
    fi
    NODE_VERSION=$(node -v)
    print_success "Node.js $NODE_VERSION installed"
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version)
    print_success "$PYTHON_VERSION installed"
    
    if ! command_exists yarn; then
        print_warning "Yarn not found. Installing..."
        npm install -g yarn
    fi
    print_success "Yarn installed"
    
    echo ""
    
    # Step 2: Install backend dependencies
    print_step "Step 2/6: Installing backend dependencies..."
    cd backend
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
    pip install -r requirements.txt --quiet
    print_success "Backend dependencies installed"
    cd ..
    echo ""
    
    # Step 3: Install frontend dependencies
    print_step "Step 3/6: Installing frontend dependencies..."
    cd frontend
    yarn install --silent
    print_success "Frontend dependencies installed"
    cd ..
    echo ""
    
    # Step 4: Setup database
    print_step "Step 4/6: Setting up SQLite database..."
    mkdir -p ~/.xionimus_ai
    print_success "Database directory created at ~/.xionimus_ai"
    echo ""
    
    # Step 5: Configure environment
    print_step "Step 5/6: Checking environment configuration..."
    
    if [ ! -f "backend/.env" ]; then
        print_warning ".env file not found. Using defaults."
        cat > backend/.env << EOF
# Xionimus AI Configuration
DATABASE_URL=~/.xionimus_ai/xionimus.db
UPLOAD_DIR=~/.xionimus_ai/uploads

# AI Provider API Keys (Optional - configure in Settings UI)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
PERPLEXITY_API_KEY=

# Server Configuration
BACKEND_PORT=8001
FRONTEND_PORT=3000
EOF
        print_success "Created default .env file"
    else
        print_success "Environment configuration found"
    fi
    echo ""
    
    # Step 6: Display completion message
    print_step "Step 6/6: Setup complete!"
    echo ""
    print_success "Xionimus AI is ready to run!"
    echo ""
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${GREEN}To start the application:${NC}"
    echo ""
    echo -e "  ${YELLOW}Backend:${NC}  cd backend && source venv/bin/activate && python main.py"
    echo -e "  ${YELLOW}Frontend:${NC} cd frontend && yarn dev"
    echo ""
    echo -e "  ${YELLOW}Or use:${NC} ./start-dev.sh (if available)"
    echo ""
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}Configure AI Provider API keys:${NC}"
    echo -e "  • Open http://localhost:3000"
    echo -e "  • Navigate to Settings"
    echo -e "  • Add your OpenAI, Anthropic, or Perplexity API keys"
    echo ""
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo ""
    print_success "Happy coding with Xionimus AI! 🚀"
    echo ""
}

# Run main function
main
