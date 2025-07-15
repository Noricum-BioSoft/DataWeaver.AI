#!/bin/bash

# DataWeaver.AI Setup Script
echo "🚀 Setting up DataWeaver.AI..."

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL is not installed. Please install PostgreSQL and create a database named 'dataweaver'."
    echo "   You can also use Docker: docker run --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=dataweaver -p 5432:5432 -d postgres"
fi

# Create virtual environment for backend
echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# Create storage directory
echo "📁 Creating storage directory..."
mkdir -p storage

# Set up database (if PostgreSQL is available)
if command -v psql &> /dev/null; then
    echo "🗄️  Setting up database..."
    # Check if database exists
    if psql -h localhost -U postgres -lqt | cut -d \| -f 1 | grep -qw dataweaver; then
        echo "✅ Database 'dataweaver' already exists"
    else
        echo "📝 Creating database 'dataweaver'..."
        createdb -h localhost -U postgres dataweaver
    fi
    
    # Run database migrations
    echo "🔄 Running database migrations..."
    alembic upgrade head
else
    echo "⚠️  Skipping database setup. Please set up PostgreSQL manually."
fi

cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install

# Create environment files
echo "⚙️  Creating environment files..."

# Backend .env
cat > ../backend/.env << EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/dataweaver
STORAGE_PATH=storage
LOG_LEVEL=INFO
EOF

# Frontend .env
cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000/api/v1
EOF

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Start the backend server:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload"
echo ""
echo "2. Start the frontend development server:"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. Open your browser to http://localhost:3000"
echo ""
echo "📚 For more information, see docs/ARCHITECTURE.md"
echo ""
echo "🔧 Configuration:"
echo "- Backend API: http://localhost:8000"
echo "- Frontend: http://localhost:3000"
echo "- Database: PostgreSQL on localhost:5432"
echo "- Storage: ./backend/storage/" 