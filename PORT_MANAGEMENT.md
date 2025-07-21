# Port Management for DataWeaver.AI

## Overview

DataWeaver.AI uses several ports for different services. This document explains how to manage ports and avoid conflicts.

## Default Ports

| Service | Port | Description |
|---------|------|-------------|
| Backend API | 8000 | FastAPI server |
| Frontend | 3000 | React development server |
| PostgreSQL | 5432 | Database server |
| Redis | 6379 | Cache/message broker |

## Port Management Tools

### 1. Port Checker Script (`check_ports.sh`)

A dedicated script to check and free ports:

```bash
# Check all default ports
./check_ports.sh

# Check specific ports
./check_ports.sh 8000 3000

# Free all ports automatically
./check_ports.sh free
```

### 2. Enhanced Start Script (`start.sh`)

The main startup script now includes port management:

```bash
# Normal startup (asks before killing processes)
./start.sh

# Force startup (automatically frees ports)
./start.sh force

# Check service status
./start.sh status

# Start individual services
./start.sh backend
./start.sh frontend
```

## Port Conflict Resolution

### Automatic Detection

Both scripts automatically detect when ports are in use:

```bash
❌ Port 8000 is in use by PIDs: 67229 67231
   To free the port, run: kill -9 67229 67231
```

### Manual Port Freeing

If you need to manually free ports:

```bash
# Find processes using a port
lsof -ti:8000

# Kill processes using a port
kill -9 $(lsof -ti:8000)

# Check if port is free
lsof -ti:8000 || echo "Port is free"
```

### Interactive Mode

The start script asks before killing processes:

```bash
[WARNING] Backend is already running on port 8000
Do you want to kill the existing process and start fresh? (y/N):
```

## Best Practices

### 1. Always Check Ports First

Before starting services, check if ports are free:

```bash
./check_ports.sh
```

### 2. Use Force Mode for Clean Starts

When you want a completely fresh start:

```bash
./start.sh force
```

### 3. Monitor Service Status

Regularly check service status:

```bash
./start.sh status
```

### 4. Handle Development Conflicts

During development, you might have multiple instances running:

```bash
# Kill all Node.js processes (frontend)
pkill -f "node.*react-scripts"

# Kill all Python processes (backend)
pkill -f "uvicorn.*main:app"
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Solution: Use force mode
   ./start.sh force
   ```

2. **Process Won't Die**
   ```bash
   # Solution: Force kill
   sudo kill -9 $(lsof -ti:8000)
   ```

3. **Permission Denied**
   ```bash
   # Solution: Check permissions
   chmod +x start.sh check_ports.sh
   ```

### Debugging Commands

```bash
# Check what's using a port
lsof -i :8000

# Check all listening ports
netstat -tulpn | grep LISTEN

# Check process details
ps aux | grep uvicorn
ps aux | grep node
```

## Integration with Development Workflow

### Pre-commit Hook

Add port checking to your development workflow:

```bash
# In your pre-commit hook
./check_ports.sh 8000 3000 || exit 1
```

### CI/CD Integration

For automated testing:

```bash
# In your CI pipeline
./start.sh force
# Run tests
# Cleanup
```

## Configuration

### Custom Ports

To use different ports, modify the start script:

```bash
# In start.sh
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

### Environment Variables

You can also use environment variables:

```bash
export DATAWEAVER_BACKEND_PORT=8001
export DATAWEAVER_FRONTEND_PORT=3001
./start.sh
```

## Summary

- **Always check ports before starting services**
- **Use `./start.sh force` for clean starts**
- **Monitor service status regularly**
- **Use `./check_ports.sh` for detailed port information**
- **Handle conflicts gracefully with interactive prompts**

This port management system ensures smooth startup and prevents conflicts during development and deployment. 