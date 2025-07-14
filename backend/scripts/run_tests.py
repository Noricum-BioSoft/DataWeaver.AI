#!/usr/bin/env python3
"""
Test runner script for DataWeaver.AI backend
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print(f"Error: {e}")
        if e.stdout:
            print("Stdout:")
            print(e.stdout)
        if e.stderr:
            print("Stderr:")
            print(e.stderr)
        return False


def main():
    """Main test runner"""
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    print("🧪 DataWeaver.AI Test Suite")
    print("=" * 60)
    
    # Install test dependencies
    print("\n📦 Installing test dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"], 
                      "Installing test dependencies"):
        return False
    
    # Run unit tests
    print("\n🔬 Running unit tests...")
    if not run_command([sys.executable, "-m", "pytest", "tests/test_bio_matcher.py", "-v"], 
                      "Unit tests for bio matcher"):
        return False
    
    # Run model tests
    print("\n🏗️ Running model tests...")
    if not run_command([sys.executable, "-m", "pytest", "tests/test_models.py", "-v"], 
                      "Model tests"):
        return False
    
    # Run API tests
    print("\n🌐 Running API tests...")
    if not run_command([sys.executable, "-m", "pytest", "tests/test_api_endpoints.py", "-v"], 
                      "API endpoint tests"):
        return False
    
    # Run integration tests
    print("\n🔗 Running integration tests...")
    if not run_command([sys.executable, "-m", "pytest", "tests/test_integration.py", "-v"], 
                      "Integration tests"):
        return False
    
    # Run all tests with coverage
    print("\n📊 Running all tests with coverage...")
    if not run_command([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "--cov=app", 
        "--cov=models", 
        "--cov=services",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v"
    ], "All tests with coverage"):
        return False
    
    print("\n🎉 All tests completed successfully!")
    print("\n📈 Coverage report generated in htmlcov/index.html")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 