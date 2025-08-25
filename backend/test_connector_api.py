#!/usr/bin/env python3
"""
Test script for the connector API
"""

import requests
import json

def test_connector_api():
    """Test the connector API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing Connector API...")
    
    # Test 1: Get connectors
    try:
        response = requests.get(f"{base_url}/api/connectors/")
        print(f"GET /api/connectors/ - Status: {response.status_code}")
        if response.status_code == 200:
            connectors = response.json()
            print(f"Found {len(connectors)} connectors")
            for connector in connectors:
                print(f"  - {connector.get('name', 'Unknown')} ({connector.get('connector_type', 'Unknown')})")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing GET /api/connectors/: {e}")
    
    # Test 2: Get supported connector types
    try:
        response = requests.get(f"{base_url}/api/connectors/types/supported")
        print(f"\nGET /api/connectors/types/supported - Status: {response.status_code}")
        if response.status_code == 200:
            types = response.json()
            print(f"Supported types: {types}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing GET /api/connectors/types/supported: {e}")
    
    # Test 3: Get demo scenarios
    try:
        response = requests.get(f"{base_url}/api/connectors/scenarios")
        print(f"\nGET /api/connectors/scenarios - Status: {response.status_code}")
        if response.status_code == 200:
            scenarios = response.json()
            print(f"Available scenarios: {len(scenarios)}")
            for scenario in scenarios:
                print(f"  - {scenario.get('name', 'Unknown')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing GET /api/connectors/scenarios: {e}")

if __name__ == "__main__":
    test_connector_api()
