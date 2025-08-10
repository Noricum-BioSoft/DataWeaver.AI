#!/usr/bin/env python3
"""
DataWeaver.AI Unified Startup Script
This script provides a unified way to start DataWeaver.AI across all platforms.
"""

import os
import sys
import subprocess
import time
import signal
import platform
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import argparse

# Configuration
DEFAULT_CONFIG = {
    "backend": {
        "port": 8000,
        "host": "localhost",
        "reload": True
    },
    "frontend": {
        "port": 3000,
        "host": "localhost"
    },
    "database": {
        "port": 5432,
        "host": "localhost",
        "name": "dataweaver",
        "user": "postgres",
        "password": "password"
    }
}

class DataWeaverStartup:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.processes: List[subprocess.Popen] = []
        self.project_root = Path(__file__).parent
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return DEFAULT_CONFIG
    
    def _check_port(self, port: int, host: str = "localhost") -> bool:
        """Check if a port is available."""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                return result != 0
        except Exception:
            return False
    
    def _wait_for_service(self, port: int, host: str = "localhost", timeout: int = 30) -> bool:
        """Wait for a service to be ready on a port."""
        import socket
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    if s.connect_ex((host, port)) == 0:
                        return True
            except Exception:
                pass
            time.sleep(1)
        return False
    
    def _kill_process_on_port(self, port: int) -> bool:
        """Kill process using a specific port."""
        system = platform.system().lower()
        
        try:
            if system == "windows":
                # Windows
                result = subprocess.run(
                    ["netstat", "-ano"], 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                for line in result.stdout.split('\n'):
                    if f":{port}" in line and "LISTENING" in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            subprocess.run(["taskkill", "/PID", pid, "/F"], check=True)
                            return True
            else:
                # Unix-like systems
                result = subprocess.run(
                    ["lsof", "-ti", f":{port}"], 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        subprocess.run(["kill", "-9", pid], check=True)
                    return True
        except subprocess.CalledProcessError:
            pass
        return False
    
    def _setup_environment(self) -> bool:
        """Set up environment variables and check prerequisites."""
        print("🔧 Setting up environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            return False
        
        # Check Node.js
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Node.js is required but not installed")
            return False
        
        # Check npm
        try:
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ npm is required but not installed")
            return False
        
        # Create necessary directories
        (self.project_root / "backend" / "storage").mkdir(parents=True, exist_ok=True)
        (self.project_root / "logs").mkdir(exist_ok=True)
        
        print("✅ Environment setup complete")
        return True
    
    def _install_dependencies(self) -> bool:
        """Install Python and Node.js dependencies."""
        print("📦 Installing dependencies...")
        
        try:
            # Install Python dependencies
            backend_dir = self.project_root / "backend"
            if (backend_dir / "requirements.txt").exists():
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", 
                    str(backend_dir / "requirements.txt")
                ], check=True, cwd=backend_dir)
            
            # Install Node.js dependencies
            frontend_dir = self.project_root / "frontend"
            if (frontend_dir / "package.json").exists():
                subprocess.run(["npm", "install"], check=True, cwd=frontend_dir)
            
            print("✅ Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def _setup_database(self) -> bool:
        """Set up database and run migrations."""
        print("🗄️ Setting up database...")
        
        try:
            backend_dir = self.project_root / "backend"
            
            # Check if alembic is available
            if (backend_dir / "alembic.ini").exists():
                subprocess.run([
                    sys.executable, "-m", "alembic", "upgrade", "head"
                ], check=True, cwd=backend_dir)
                print("✅ Database migrations applied")
            else:
                print("⚠️ No database migrations found, skipping")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to setup database: {e}")
            return False
    
    def _start_backend(self) -> Optional[subprocess.Popen]:
        """Start the backend server."""
        print("🚀 Starting backend server...")
        
        backend_port = self.config["backend"]["port"]
        backend_host = self.config["backend"]["host"]
        
        # Check if port is available
        if not self._check_port(backend_port, backend_host):
            print(f"⚠️ Port {backend_port} is in use, attempting to free it...")
            if not self._kill_process_on_port(backend_port):
                print(f"❌ Could not free port {backend_port}")
                return None
        
        try:
            backend_dir = self.project_root / "backend"
            cmd = [
                sys.executable, "-m", "uvicorn", "main:app",
                "--host", backend_host,
                "--port", str(backend_port)
            ]
            
            if self.config["backend"]["reload"]:
                cmd.append("--reload")
            
            process = subprocess.Popen(
                cmd,
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Wait for backend to start
            if self._wait_for_service(backend_port, backend_host):
                print(f"✅ Backend server started on http://{backend_host}:{backend_port}")
                return process
            else:
                print("❌ Backend server failed to start")
                process.terminate()
                return None
                
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return None
    
    def _start_frontend(self) -> Optional[subprocess.Popen]:
        """Start the frontend development server."""
        print("🌐 Starting frontend server...")
        
        frontend_port = self.config["frontend"]["port"]
        frontend_host = self.config["frontend"]["host"]
        
        # Check if port is available
        if not self._check_port(frontend_port, frontend_host):
            print(f"⚠️ Port {frontend_port} is in use, attempting to free it...")
            if not self._kill_process_on_port(frontend_port):
                print(f"❌ Could not free port {frontend_port}")
                return None
        
        try:
            frontend_dir = self.project_root / "frontend"
            process = subprocess.Popen(
                ["npm", "start"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Wait for frontend to start
            if self._wait_for_service(frontend_port, frontend_host):
                print(f"✅ Frontend server started on http://{frontend_host}:{frontend_port}")
                return process
            else:
                print("❌ Frontend server failed to start")
                process.terminate()
                return None
                
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return None
    
    def start(self, install_deps: bool = False, setup_db: bool = False) -> bool:
        """Start DataWeaver.AI services."""
        print("🎯 Starting DataWeaver.AI...")
        
        # Setup environment
        if not self._setup_environment():
            return False
        
        # Install dependencies if requested
        if install_deps and not self._install_dependencies():
            return False
        
        # Setup database if requested
        if setup_db and not self._setup_database():
            return False
        
        # Start backend
        backend_process = self._start_backend()
        if not backend_process:
            return False
        self.processes.append(backend_process)
        
        # Start frontend
        frontend_process = self._start_frontend()
        if not frontend_process:
            self.stop()
            return False
        self.processes.append(frontend_process)
        
        print("\n🎉 DataWeaver.AI is now running!")
        print(f"📊 Backend API: http://{self.config['backend']['host']}:{self.config['backend']['port']}")
        print(f"🌐 Frontend: http://{self.config['frontend']['host']}:{self.config['frontend']['port']}")
        print("\nPress Ctrl+C to stop all services")
        
        return True
    
    def stop(self):
        """Stop all running services."""
        print("\n🛑 Stopping DataWeaver.AI services...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception:
                pass
        
        self.processes.clear()
        print("✅ All services stopped")

def signal_handler(signum, frame):
    """Handle interrupt signals."""
    print("\n🛑 Received interrupt signal")
    if hasattr(signal_handler, 'startup'):
        signal_handler.startup.stop()
    sys.exit(0)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="DataWeaver.AI Startup Script")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies")
    parser.add_argument("--setup-db", action="store_true", help="Setup database and run migrations")
    parser.add_argument("--version", action="version", version="DataWeaver.AI v1.0.0")
    
    args = parser.parse_args()
    
    # Create startup instance
    startup = DataWeaverStartup(args.config)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal_handler.startup = startup
    
    try:
        # Start services
        if startup.start(args.install_deps, args.setup_db):
            # Keep running until interrupted
            while True:
                time.sleep(1)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    finally:
        startup.stop()

if __name__ == "__main__":
    main()
