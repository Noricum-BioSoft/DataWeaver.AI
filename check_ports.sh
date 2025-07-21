#!/bin/bash

# Port checking utility for DataWeaver.AI
# Usage: ./check_ports.sh [port1] [port2] ...

check_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "❌ Port $port is in use by PIDs: $pids"
        echo "   To free the port, run: kill -9 $pids"
        return 1
    else
        echo "✅ Port $port is free"
        return 0
    fi
}

free_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "🔄 Freeing port $port by killing PIDs: $pids"
        kill -9 $pids 2>/dev/null
        sleep 1
        
        # Check if port is now free
        if [ -z "$(lsof -ti:$port 2>/dev/null)" ]; then
            echo "✅ Port $port is now free"
            return 0
        else
            echo "❌ Failed to free port $port"
            return 1
        fi
    else
        echo "✅ Port $port is already free"
        return 0
    fi
}

# Default ports for DataWeaver.AI
DEFAULT_PORTS=(8000 3000 5432 6379)

if [ $# -eq 0 ]; then
    echo "🔍 Checking default DataWeaver.AI ports..."
    ports=("${DEFAULT_PORTS[@]}")
else
    echo "🔍 Checking specified ports..."
    ports=("$@")
fi

all_free=true

for port in "${ports[@]}"; do
    if ! check_port $port; then
        all_free=false
    fi
done

echo ""
if [ "$all_free" = true ]; then
    echo "🎉 All ports are free! Ready to start services."
else
    echo "⚠️  Some ports are in use. Use './check_ports.sh free' to automatically free them."
fi

# Special command to free all ports
if [ "$1" = "free" ]; then
    echo ""
    echo "🔄 Freeing all specified ports..."
    for port in "${DEFAULT_PORTS[@]}"; do
        free_port $port
    done
    exit 0
fi 