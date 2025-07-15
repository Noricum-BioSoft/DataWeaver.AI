#!/bin/bash

# DataWeaver.AI Startup Script
# This script starts all services required for DataWeaver.AI

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
DATABASE_PORT=5432
REDIS_PORT=6379

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "$service is already running on port $port"
        return 0
    else
        return 1
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    local max_attempts=30
    local attempt=1

    print_status "Waiting for $service to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z $host $port 2>/dev/null; then
            print_success "$service is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    print_error "$service failed to start after $max_attempts attempts"
    return 1
}

# Function to start PostgreSQL
start_postgresql() {
    print_status "Starting PostgreSQL..."
    
    # Check if PostgreSQL is already running
    if check_port $DATABASE_PORT "PostgreSQL"; then
        return 0
    fi
    
    # Try to start PostgreSQL using different methods
    if command -v brew &> /dev/null; then
        # macOS with Homebrew
        brew services start postgresql@14 2>/dev/null || brew services start postgresql 2>/dev/null
    elif command -v systemctl &> /dev/null; then
        # Linux with systemd
        sudo systemctl start postgresql 2>/dev/null || sudo systemctl start postgresql@14 2>/dev/null
    elif command -v service &> /dev/null; then
        # Linux with service
        sudo service postgresql start 2>/dev/null
    else
        print_warning "Could not start PostgreSQL automatically. Please start it manually."
        return 1
    fi
    
    wait_for_service localhost $DATABASE_PORT "PostgreSQL"
}

# Function to start Redis
start_redis() {
    print_status "Starting Redis..."
    
    # Check if Redis is already running
    if check_port $REDIS_PORT "Redis"; then
        return 0
    fi
    
    # Try to start Redis using different methods
    if command -v brew &> /dev/null; then
        # macOS with Homebrew
        brew services start redis 2>/dev/null
    elif command -v systemctl &> /dev/null; then
        # Linux with systemd
        sudo systemctl start redis 2>/dev/null || sudo systemctl start redis-server 2>/dev/null
    elif command -v service &> /dev/null; then
        # Linux with service
        sudo service redis start 2>/dev/null || sudo service redis-server start 2>/dev/null
    else
        print_warning "Could not start Redis automatically. Please start it manually."
        return 1
    fi
    
    wait_for_service localhost $REDIS_PORT "Redis"
}

# Function to setup Python environment
setup_python_env() {
    print_status "Setting up Python environment..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/upgrade pip
    pip install --upgrade pip
    
    # Install backend dependencies
    print_status "Installing backend dependencies..."
    cd backend
    pip install -r requirements.txt
    cd ..
}

# Function to setup Node.js environment
setup_node_env() {
    print_status "Setting up Node.js environment..."
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    else
        print_status "Frontend dependencies already installed"
    fi
    
    cd ..
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    cd backend
    
    # Activate virtual environment
    source ../venv/bin/activate
    
    # Check if alembic is available
    if command -v alembic &> /dev/null || [ -f "alembic.ini" ]; then
        # Run migrations
        alembic upgrade head 2>/dev/null || print_warning "Could not run migrations. Database might not be ready."
    else
        print_warning "Alembic not found. Skipping migrations."
    fi
    
    cd ..
}

# Function to start backend server
start_backend() {
    print_status "Starting backend server..."
    
    # Check if backend is already running
    if check_port $BACKEND_PORT "Backend"; then
        print_warning "Backend is already running on port $BACKEND_PORT"
        return 0
    fi
    
    cd backend
    
    # Activate virtual environment
    source ../venv/bin/activate
    
    # Start the server in background
    print_status "Starting FastAPI server on port $BACKEND_PORT..."
    uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
    BACKEND_PID=$!
    
    cd ..
    
    # Wait for backend to be ready
    wait_for_service localhost $BACKEND_PORT "Backend API"
    
    print_success "Backend server started with PID $BACKEND_PID"
}

# Function to start frontend server
start_frontend() {
    print_status "Starting frontend server..."
    
    # Check if frontend is already running
    if check_port $FRONTEND_PORT "Frontend"; then
        print_warning "Frontend is already running on port $FRONTEND_PORT"
        return 0
    fi
    
    cd frontend
    
    # Start the development server in background
    print_status "Starting React development server on port $FRONTEND_PORT..."
    npm start &
    FRONTEND_PID=$!
    
    cd ..
    
    # Wait for frontend to be ready
    wait_for_service localhost $FRONTEND_PORT "Frontend"
    
    print_success "Frontend server started with PID $FRONTEND_PID"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    # Create storage directory
    mkdir -p backend/storage
    
    # Create logs directory
    mkdir -p logs
    
    print_success "Directories created"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed"
        exit 1
    fi
    
    print_success "All prerequisites are satisfied"
}

# Function to show status
show_status() {
    echo ""
    echo "🎯 DataWeaver.AI Services Status:"
    echo "=================================="
    
    # Check backend
    if check_port $BACKEND_PORT "Backend"; then
        echo -e "✅ Backend API: http://localhost:$BACKEND_PORT"
    else
        echo -e "❌ Backend API: Not running"
    fi
    
    # Check frontend
    if check_port $FRONTEND_PORT "Frontend"; then
        echo -e "✅ Frontend: http://localhost:$FRONTEND_PORT"
    else
        echo -e "❌ Frontend: Not running"
    fi
    
    # Check database
    if check_port $DATABASE_PORT "PostgreSQL"; then
        echo -e "✅ PostgreSQL: localhost:$DATABASE_PORT"
    else
        echo -e "❌ PostgreSQL: Not running"
    fi
    
    # Check Redis
    if check_port $REDIS_PORT "Redis"; then
        echo -e "✅ Redis: localhost:$REDIS_PORT"
    else
        echo -e "❌ Redis: Not running"
    fi
    
    echo ""
}

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down services..."
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    print_success "Cleanup complete"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Main execution
main() {
    echo "🚀 Starting DataWeaver.AI..."
    echo "=============================="
    
    # Check prerequisites
    check_prerequisites
    
    # Create necessary directories
    create_directories
    
    # Setup environments
    setup_python_env
    setup_node_env
    
    # Start services
    start_postgresql
    start_redis
    
    # Run migrations
    run_migrations
    
    # Start application servers
    start_backend
    start_frontend
    
    # Show final status
    show_status
    
    echo ""
    echo "🎉 DataWeaver.AI is now running!"
    echo "=================================="
    echo "📱 Frontend: http://localhost:$FRONTEND_PORT"
    echo "🔧 Backend API: http://localhost:$BACKEND_PORT"
    echo "📊 API Documentation: http://localhost:$BACKEND_PORT/docs"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo ""
    
    # Keep script running
    wait
}

# Handle command line arguments
case "${1:-}" in
    "status")
        show_status
        exit 0
        ;;
    "backend")
        check_prerequisites
        setup_python_env
        start_backend
        wait
        ;;
    "frontend")
        check_prerequisites
        setup_node_env
        start_frontend
        wait
        ;;
    "db")
        start_postgresql
        ;;
    "redis")
        start_redis
        ;;
    "help"|"-h"|"--help")
        echo "DataWeaver.AI Startup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Start all services"
        echo "  status     Show service status"
        echo "  backend    Start only backend"
        echo "  frontend   Start only frontend"
        echo "  db         Start only PostgreSQL"
        echo "  redis      Start only Redis"
        echo "  help       Show this help"
        echo ""
        exit 0
        ;;
    *)
        main
        ;;
esac 