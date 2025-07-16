#!/usr/bin/env python3
"""
Integration test runner for DataWeaver.AI
Runs comprehensive system integration tests with PostgreSQL
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def setup_test_environment():
    """Setup test environment variables"""
    # Set PostgreSQL test configuration
    os.environ["USE_POSTGRES"] = "true"
    os.environ["TEST_DATABASE_URL"] = os.getenv(
        "TEST_DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/datweaver_test"
    )
    
    # Set other test environment variables
    os.environ["TESTING"] = "true"
    os.environ["ENVIRONMENT"] = "test"

def check_postgres_connection():
    """Check if PostgreSQL is available"""
    try:
        import psycopg2
        database_url = os.getenv("TEST_DATABASE_URL")
        if database_url and database_url.startswith("postgresql://"):
            # Extract connection parameters
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],  # Remove leading slash
                user=parsed.username,
                password=parsed.password
            )
            conn.close()
            print("✓ PostgreSQL connection successful")
            return True
        else:
            print("✗ Invalid PostgreSQL URL format")
            return False
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        return False

def run_tests(test_pattern=None, verbose=False, force_sqlite=False):
    """Run integration tests"""
    if not force_sqlite:
        setup_test_environment()
        
        if not check_postgres_connection():
            print("PostgreSQL not available. Falling back to SQLite for integration tests.")
            force_sqlite = True
    
    if force_sqlite:
        # Use SQLite for integration tests
        os.environ["USE_POSTGRES"] = "false"
        os.environ["TEST_DATABASE_URL"] = "sqlite:///./test.db"
        os.environ["TESTING"] = "true"
        print("✓ Using SQLite for integration tests")
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if test_pattern:
        cmd.append(test_pattern)
    else:
        cmd.append("tests/test_system_integration.py")
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    print(f"Running integration tests with command: {' '.join(cmd)}")
    
    # Run tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode == 0

def run_unit_tests():
    """Run unit tests with SQLite"""
    os.environ["USE_POSTGRES"] = "false"
    os.environ["TEST_DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["TESTING"] = "true"
    
    cmd = [
        "python", "-m", "pytest",
        "tests/test_api_endpoints.py",
        "tests/test_bio_matcher.py", 
        "tests/test_models.py",
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ]
    
    print("Running unit tests with SQLite...")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode == 0

def run_all_tests():
    """Run all tests (unit + integration)"""
    print("=" * 60)
    print("RUNNING ALL TESTS")
    print("=" * 60)
    
    # Run unit tests first
    print("\n1. Running unit tests...")
    unit_success = run_unit_tests()
    
    print("\n" + "=" * 60)
    
    # Run integration tests
    print("\n2. Running integration tests...")
    integration_success = run_tests() # Changed from run_integration_tests() to run_tests()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Unit tests: {'✓ PASSED' if unit_success else '✗ FAILED'}")
    print(f"Integration tests: {'✓ PASSED' if integration_success else '✗ FAILED'}")
    
    return unit_success and integration_success

def main():
    parser = argparse.ArgumentParser(description="Run DataWeaver.AI tests")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "all"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--pattern", 
        help="Specific test pattern to run (e.g., 'test_upload')"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--sqlite", 
        action="store_true",
        help="Force SQLite for integration tests"
    )
    
    args = parser.parse_args()
    
    if args.type == "unit":
        success = run_unit_tests()
    elif args.type == "integration":
        success = run_tests(args.pattern, args.verbose, args.sqlite)
    else:  # all
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 