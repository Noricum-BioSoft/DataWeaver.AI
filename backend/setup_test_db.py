#!/usr/bin/env python3
"""
Test database setup script for DataWeaver.AI
Manages PostgreSQL test database creation and cleanup
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def setup_postgres_docker():
    """Setup PostgreSQL using Docker Compose"""
    compose_file = Path(__file__).parent / "docker-compose.test.yml"
    
    if not compose_file.exists():
        print("✗ Docker Compose file not found")
        return False
    
    print("Starting PostgreSQL test database with Docker...")
    
    try:
        # Start the PostgreSQL container
        result = subprocess.run([
            "docker-compose", "-f", str(compose_file), "up", "-d"
        ], cwd=Path(__file__).parent)
        
        if result.returncode != 0:
            print("✗ Failed to start PostgreSQL container")
            return False
        
        # Wait for PostgreSQL to be ready
        print("Waiting for PostgreSQL to be ready...")
        import time
        import psycopg2
        
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    port=5433,
                    database="datweaver_test",
                    user="postgres",
                    password="postgres"
                )
                conn.close()
                print("✓ PostgreSQL is ready")
                return True
            except Exception as e:
                if attempt < max_attempts - 1:
                    print(f"Waiting for PostgreSQL... ({attempt + 1}/{max_attempts})")
                    time.sleep(2)
                else:
                    print(f"✗ PostgreSQL failed to start: {e}")
                    return False
        
    except Exception as e:
        print(f"✗ Error setting up PostgreSQL: {e}")
        return False

def teardown_postgres_docker():
    """Stop and remove PostgreSQL Docker container"""
    compose_file = Path(__file__).parent / "docker-compose.test.yml"
    
    print("Stopping PostgreSQL test database...")
    
    try:
        result = subprocess.run([
            "docker-compose", "-f", str(compose_file), "down", "-v"
        ], cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✓ PostgreSQL container stopped and removed")
            return True
        else:
            print("✗ Failed to stop PostgreSQL container")
            return False
            
    except Exception as e:
        print(f"✗ Error stopping PostgreSQL: {e}")
        return False

def check_postgres_connection():
    """Check if PostgreSQL is accessible"""
    try:
        import psycopg2
        
        # Try different ports (5432 for local, 5433 for Docker)
        for port in [5432, 5433]:
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    port=port,
                    database="datweaver_test",
                    user="postgres",
                    password="postgres"
                )
                conn.close()
                print(f"✓ PostgreSQL accessible on port {port}")
                return True, port
            except Exception:
                continue
        
        print("✗ PostgreSQL not accessible on any port")
        return False, None
        
    except ImportError:
        print("✗ psycopg2 not installed")
        return False, None

def run_migrations():
    """Run database migrations"""
    print("Running database migrations...")
    
    try:
        # Set environment for test database
        os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/datweaver_test")
        
        result = subprocess.run([
            "alembic", "upgrade", "head"
        ], cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✓ Database migrations completed")
            return True
        else:
            print("✗ Database migrations failed")
            return False
            
    except Exception as e:
        print(f"✗ Error running migrations: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Setup test database for DataWeaver.AI")
    parser.add_argument(
        "action",
        choices=["setup", "teardown", "check", "migrate"],
        help="Action to perform"
    )
    parser.add_argument(
        "--docker", 
        action="store_true",
        help="Use Docker for PostgreSQL setup"
    )
    
    args = parser.parse_args()
    
    if args.action == "setup":
        if args.docker:
            success = setup_postgres_docker()
        else:
            print("Please ensure PostgreSQL is running locally on port 5432")
            success = check_postgres_connection()[0]
        
        if success:
            print("✓ Test database setup complete")
            print("You can now run integration tests with:")
            print("  python run_integration_tests.py --type integration")
        else:
            print("✗ Test database setup failed")
            sys.exit(1)
    
    elif args.action == "teardown":
        if args.docker:
            success = teardown_postgres_docker()
        else:
            print("Please stop PostgreSQL manually")
            success = True
        
        if success:
            print("✓ Test database teardown complete")
        else:
            print("✗ Test database teardown failed")
            sys.exit(1)
    
    elif args.action == "check":
        accessible, port = check_postgres_connection()
        if accessible:
            print(f"✓ PostgreSQL is accessible on port {port}")
            # Set environment variable for tests
            os.environ["TEST_DATABASE_URL"] = f"postgresql://postgres:postgres@localhost:{port}/datweaver_test"
        else:
            print("✗ PostgreSQL is not accessible")
            sys.exit(1)
    
    elif args.action == "migrate":
        success = run_migrations()
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main() 