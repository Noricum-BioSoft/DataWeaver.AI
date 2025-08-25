#!/usr/bin/env python3
"""
OAuth2 Configuration Test Script
Helps troubleshoot 403 access_denied errors
"""

import requests
import json

def test_oauth2_config():
    """Test OAuth2 configuration and help troubleshoot issues"""
    base_url = "http://localhost:8000"
    
    print("🔧 OAuth2 Configuration Test & Troubleshooting")
    print("=" * 60)
    
    # Test 1: Check connector configuration
    print("\n1️⃣ Checking connector configuration...")
    try:
        response = requests.get(f"{base_url}/api/connectors/")
        connectors = response.json()
        
        google_connectors = [c for c in connectors if c['connector_type'] == 'GOOGLE_WORKSPACE']
        
        if not google_connectors:
            print("❌ No Google Workspace connectors found")
            return
        
        connector = google_connectors[0]
        print(f"✅ Found connector: {connector['name']} (ID: {connector['id']})")
        
        config = connector.get('config', {})
        client_id = config.get('client_id')
        client_secret = config.get('client_secret')
        
        print(f"   Client ID: {client_id}")
        print(f"   Client Secret: {'*' * len(client_secret) if client_secret else 'NOT SET'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Generate authorization URL
    print(f"\n2️⃣ Generating authorization URL for connector {connector['id']}...")
    try:
        auth_url = f"{base_url}/api/auth/google/authorize/{connector['id']}"
        print(f"✅ Authorization URL: {auth_url}")
        
        # Test the URL
        response = requests.get(auth_url, allow_redirects=False)
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 307:
            redirect_url = response.headers.get('Location', '')
            print(f"   Redirect URL: {redirect_url}")
            
            # Parse the redirect URL to check parameters
            if 'accounts.google.com' in redirect_url:
                print("   ✅ Redirecting to Google OAuth2")
                
                # Check for common issues in the URL
                if 'localhost:3000' in redirect_url:
                    print("   ⚠️  WARNING: URL contains localhost:3000 - should be localhost:8000")
                if 'localhost:8000' in redirect_url:
                    print("   ✅ URL contains correct localhost:8000")
                    
            else:
                print("   ❌ Not redirecting to Google OAuth2")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🔧 TROUBLESHOOTING STEPS:")
    print("\n1. **Google Cloud Console Configuration**")
    print("   - Go to: https://console.cloud.google.com/")
    print("   - Select your project")
    print("   - Go to: APIs & Services > Credentials")
    print("   - Edit your OAuth2 client ID")
    print("   - Add these Authorized Redirect URIs:")
    print("     * http://localhost:8000/api/auth/callback")
    print("     * http://localhost:3000/auth/callback")
    print("     * http://localhost:3000")
    
    print("\n2. **OAuth Consent Screen**")
    print("   - Go to: APIs & Services > OAuth consent screen")
    print("   - Make sure app is in 'Testing' mode")
    print("   - Add your email as a test user")
    print("   - Add these scopes:")
    print("     * https://www.googleapis.com/auth/drive.readonly")
    print("     * https://www.googleapis.com/auth/drive.file")
    print("     * https://www.googleapis.com/auth/drive.metadata.readonly")
    
    print("\n3. **Google Drive API**")
    print("   - Go to: APIs & Services > Library")
    print("   - Search for 'Google Drive API'")
    print("   - Make sure it's enabled")
    
    print("\n4. **Test the Flow**")
    print("   - Open the authorization URL in your browser")
    print("   - Sign in with the same Google account used in test users")
    print("   - Grant permissions when prompted")
    
    print("\n5. **Common Issues**")
    print("   - Make sure you're signed in with a test user account")
    print("   - Check that the redirect URI exactly matches")
    print("   - Ensure the app is in 'Testing' mode, not 'Production'")
    print("   - Verify all required scopes are added")

if __name__ == "__main__":
    test_oauth2_config()
