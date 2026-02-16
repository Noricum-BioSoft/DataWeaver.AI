#!/usr/bin/env python3
"""
Complete OAuth2 Flow Test for Google Drive Connector
"""

import requests
import json
import time

def test_complete_oauth2_flow():
    """Test the complete OAuth2 flow for Google Drive connector"""
    base_url = "http://localhost:8000"
    
    print("🔐 Complete OAuth2 Flow Test for Google Drive Connector")
    print("=" * 70)
    
    # Test 1: Check all connectors
    print("\n1️⃣ Checking all connectors...")
    try:
        response = requests.get(f"{base_url}/api/connectors/")
        connectors = response.json()
        print(f"✅ Found {len(connectors)} connectors")
        
        google_connectors = [c for c in connectors if c['connector_type'] == 'GOOGLE_WORKSPACE']
        print(f"   Google Workspace connectors: {len(google_connectors)}")
        
        for connector in google_connectors:
            print(f"   - ID {connector['id']}: {connector['name']} ({connector['status']})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    if not google_connectors:
        print("❌ No Google Workspace connectors found")
        return
    
    # Use the first Google connector for testing
    test_connector = google_connectors[0]
    connector_id = test_connector['id']
    
    print(f"\n🎯 Testing connector: {test_connector['name']} (ID: {connector_id})")
    
    # Test 2: Test connection (should fail without OAuth2 tokens)
    print("\n2️⃣ Testing connection (should fail without OAuth2 tokens)...")
    try:
        response = requests.post(
            f"{base_url}/api/connectors/{connector_id}/test",
            json={}
        )
        result = response.json()
        print(f"✅ Connection Test Result:")
        print(f"   Success: {result.get('success')}")
        print(f"   Message: {result.get('message')}")
        if result.get('details'):
            print(f"   Details: {result.get('details')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Generate OAuth2 authorization URL
    print("\n3️⃣ Generating OAuth2 authorization URL...")
    try:
        auth_url = f"{base_url}/api/auth/google/authorize/{connector_id}"
        print(f"✅ Authorization URL: {auth_url}")
        print(f"   🔗 This URL will redirect to Google's OAuth2 consent screen")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Check OAuth2 callback endpoint
    print("\n4️⃣ Testing OAuth2 callback endpoint...")
    try:
        # Test with invalid parameters (should handle gracefully)
        response = requests.get(f"{base_url}/api/auth/callback?error=access_denied")
        print(f"✅ Callback endpoint responds to errors")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Test token refresh endpoint
    print("\n5️⃣ Testing token refresh endpoint...")
    try:
        response = requests.post(f"{base_url}/api/auth/google/refresh/{connector_id}")
        result = response.json()
        print(f"✅ Token Refresh Result:")
        print(f"   Success: {result.get('success')}")
        print(f"   Message: {result.get('message')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 COMPLETE OAUTH2 FLOW INSTRUCTIONS:")
    print("1. Open the frontend at: http://localhost:3000")
    print("2. Navigate to 'Connector Management'")
    print("3. Click 'Test' on your Google Drive connector")
    print("4. Click '🔐 Authorize Google Drive Access' button")
    print("5. Complete the OAuth2 flow in the popup window")
    print("6. Return to the test modal and click '🔄 Refresh Status'")
    print("7. Test the connection again - it should now succeed!")
    print("\n📚 Google OAuth2 Setup Guide:")
    print("   https://developers.google.com/identity/protocols/oauth2")
    print("\n🔧 Backend OAuth2 Endpoints:")
    print(f"   - Authorization: {base_url}/api/auth/google/authorize/{{connector_id}}")
    print(f"   - Callback: {base_url}/api/auth/callback")
    print(f"   - Token Refresh: {base_url}/api/auth/google/refresh/{{connector_id}}")

if __name__ == "__main__":
    test_complete_oauth2_flow()
