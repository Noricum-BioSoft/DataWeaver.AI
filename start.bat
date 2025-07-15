@echo off
REM DataWeaver.AI Startup Script for Windows
REM This script starts all services required for DataWeaver.AI

setlocal enabledelayedexpansion

REM Configuration
set BACKEND_PORT=8000
set FRONTEND_PORT=3000
set DATABASE_PORT=5432
set REDIS_PORT=6379

REM Function to print colored output
:print_status
echo [INFO] %~1
goto :eof

:print_success
echo [SUCCESS] %~1
goto :eof

:print_warning
echo [WARNING] %~1
goto :eof

:print_error
echo [ERROR] %~1
goto :eof

REM Function to check if a port is in use
:check_port
netstat -an | find ":%1 " | find "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_warning "%~2 is already running on port %1"
    exit /b 0
) else (
    exit /b 1
)

REM Function to wait for a service to be ready
:wait_for_service
set /a attempt=1
set max_attempts=30

call :print_status "Waiting for %~3 to be ready..."

:wait_loop
netstat -an | find ":%1 " | find "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "%~3 is ready!"
    exit /b 0
)

if %attempt% geq %max_attempts% (
    call :print_error "%~3 failed to start after %max_attempts% attempts"
    exit /b 1
)

set /a attempt+=1
timeout /t 1 /nobreak >nul
goto wait_loop

REM Function to start PostgreSQL
:start_postgresql
call :print_status "Starting PostgreSQL..."

call :check_port %DATABASE_PORT% "PostgreSQL"
if %errorlevel% equ 0 goto :eof

REM Try to start PostgreSQL using different methods
where pg_ctl >nul 2>&1
if %errorlevel% equ 0 (
    pg_ctl start -D "C:\Program Files\PostgreSQL\14\data" >nul 2>&1
    if %errorlevel% equ 0 (
        call :wait_for_service %DATABASE_PORT% localhost "PostgreSQL"
        goto :eof
    )
)

call :print_warning "Could not start PostgreSQL automatically. Please start it manually."
exit /b 1

REM Function to start Redis
:start_redis
call :print_status "Starting Redis..."

call :check_port %REDIS_PORT% "Redis"
if %errorlevel% equ 0 goto :eof

REM Try to start Redis
where redis-server >nul 2>&1
if %errorlevel% equ 0 (
    start /b redis-server >nul 2>&1
    call :wait_for_service %REDIS_PORT% localhost "Redis"
    goto :eof
)

call :print_warning "Could not start Redis automatically. Please start it manually."
exit /b 1

REM Function to setup Python environment
:setup_python_env
call :print_status "Setting up Python environment..."

if not exist "venv" (
    call :print_status "Creating virtual environment..."
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/upgrade pip
python -m pip install --upgrade pip

REM Install backend dependencies
call :print_status "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

goto :eof

REM Function to setup Node.js environment
:setup_node_env
call :print_status "Setting up Node.js environment..."

cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    call :print_status "Installing frontend dependencies..."
    npm install
) else (
    call :print_status "Frontend dependencies already installed"
)

cd ..

goto :eof

REM Function to run database migrations
:run_migrations
call :print_status "Running database migrations..."

cd backend

REM Activate virtual environment
call ..\venv\Scripts\activate.bat

REM Check if alembic is available
where alembic >nul 2>&1
if %errorlevel% equ 0 (
    alembic upgrade head >nul 2>&1
    if not %errorlevel% equ 0 (
        call :print_warning "Could not run migrations. Database might not be ready."
    )
) else (
    call :print_warning "Alembic not found. Skipping migrations."
)

cd ..

goto :eof

REM Function to start backend server
:start_backend
call :print_status "Starting backend server..."

call :check_port %BACKEND_PORT% "Backend"
if %errorlevel% equ 0 (
    call :print_warning "Backend is already running on port %BACKEND_PORT%"
    goto :eof
)

cd backend

REM Activate virtual environment
call ..\venv\Scripts\activate.bat

REM Start the server in background
call :print_status "Starting FastAPI server on port %BACKEND_PORT%..."
start /b uvicorn main:app --host 0.0.0.0 --port %BACKEND_PORT% --reload

cd ..

REM Wait for backend to be ready
call :wait_for_service %BACKEND_PORT% localhost "Backend API"

call :print_success "Backend server started"

goto :eof

REM Function to start frontend server
:start_frontend
call :print_status "Starting frontend server..."

call :check_port %FRONTEND_PORT% "Frontend"
if %errorlevel% equ 0 (
    call :print_warning "Frontend is already running on port %FRONTEND_PORT%"
    goto :eof
)

cd frontend

REM Start the development server in background
call :print_status "Starting React development server on port %FRONTEND_PORT%..."
start /b npm start

cd ..

REM Wait for frontend to be ready
call :wait_for_service %FRONTEND_PORT% localhost "Frontend"

call :print_success "Frontend server started"

goto :eof

REM Function to create necessary directories
:create_directories
call :print_status "Creating necessary directories..."

REM Create storage directory
if not exist "backend\storage" mkdir backend\storage

REM Create logs directory
if not exist "logs" mkdir logs

call :print_success "Directories created"

goto :eof

REM Function to check prerequisites
:check_prerequisites
call :print_status "Checking prerequisites..."

REM Check Python
where python >nul 2>&1
if not %errorlevel% equ 0 (
    call :print_error "Python is required but not installed"
    exit /b 1
)

REM Check Node.js
where node >nul 2>&1
if not %errorlevel% equ 0 (
    call :print_error "Node.js is required but not installed"
    exit /b 1
)

REM Check npm
where npm >nul 2>&1
if not %errorlevel% equ 0 (
    call :print_error "npm is required but not installed"
    exit /b 1
)

call :print_success "All prerequisites are satisfied"

goto :eof

REM Function to show status
:show_status
echo.
echo 🎯 DataWeaver.AI Services Status:
echo ==================================

REM Check backend
call :check_port %BACKEND_PORT% "Backend"
if %errorlevel% equ 0 (
    echo ✅ Backend API: http://localhost:%BACKEND_PORT%
) else (
    echo ❌ Backend API: Not running
)

REM Check frontend
call :check_port %FRONTEND_PORT% "Frontend"
if %errorlevel% equ 0 (
    echo ✅ Frontend: http://localhost:%FRONTEND_PORT%
) else (
    echo ❌ Frontend: Not running
)

REM Check database
call :check_port %DATABASE_PORT% "PostgreSQL"
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL: localhost:%DATABASE_PORT%
) else (
    echo ❌ PostgreSQL: Not running
)

REM Check Redis
call :check_port %REDIS_PORT% "Redis"
if %errorlevel% equ 0 (
    echo ✅ Redis: localhost:%REDIS_PORT%
) else (
    echo ❌ Redis: Not running
)

echo.

goto :eof

REM Main execution
:main
echo 🚀 Starting DataWeaver.AI...
echo ==============================

REM Check prerequisites
call :check_prerequisites
if %errorlevel% neq 0 exit /b 1

REM Create necessary directories
call :create_directories

REM Setup environments
call :setup_python_env
call :setup_node_env

REM Start services
call :start_postgresql
call :start_redis

REM Run migrations
call :run_migrations

REM Start application servers
call :start_backend
call :start_frontend

REM Show final status
call :show_status

echo.
echo 🎉 DataWeaver.AI is now running!
echo ==================================
echo 📱 Frontend: http://localhost:%FRONTEND_PORT%
echo 🔧 Backend API: http://localhost:%BACKEND_PORT%
echo 📊 API Documentation: http://localhost:%BACKEND_PORT%/docs
echo.
echo Press Ctrl+C to stop all services
echo.

REM Keep script running
pause

goto :eof

REM Handle command line arguments
if "%1"=="status" (
    call :show_status
    exit /b 0
)

if "%1"=="backend" (
    call :check_prerequisites
    call :setup_python_env
    call :start_backend
    pause
    exit /b 0
)

if "%1"=="frontend" (
    call :check_prerequisites
    call :setup_node_env
    call :start_frontend
    pause
    exit /b 0
)

if "%1"=="db" (
    call :start_postgresql
    exit /b 0
)

if "%1"=="redis" (
    call :start_redis
    exit /b 0
)

if "%1"=="help" (
    echo DataWeaver.AI Startup Script
    echo.
    echo Usage: %0 [command]
    echo.
    echo Commands:
    echo   (no args)  Start all services
    echo   status     Show service status
    echo   backend    Start only backend
    echo   frontend   Start only frontend
    echo   db         Start only PostgreSQL
    echo   redis      Start only Redis
    echo   help       Show this help
    echo.
    exit /b 0
)

if "%1"=="-h" (
    goto help
)

if "%1"=="--help" (
    goto help
)

REM Default: start all services
call :main 