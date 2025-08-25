"""
OAuth2 Authorization endpoints for Google Drive API
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
import secrets

from ..database import get_db
from ..models.connector import Connector, ConnectorStatus
from ..services.connectors.google_drive_connector import GoogleDriveConnector

router = APIRouter(prefix="/auth", tags=["authentication"])

# Store OAuth2 state for security
oauth_states = {}

@router.get("/google/authorize/{connector_id}")
async def authorize_google_drive(connector_id: int, db: Session = Depends(get_db)):
    """Start OAuth2 authorization flow for Google Drive"""
    try:
        # Get the connector
        connector = db.query(Connector).filter(Connector.id == connector_id).first()
        if not connector:
            raise HTTPException(status_code=404, detail="Connector not found")
        
        if connector.connector_type.value != "GOOGLE_WORKSPACE":
            raise HTTPException(status_code=400, detail="Connector is not a Google Workspace connector")
        
        config = connector.config or {}
        client_id = config.get('client_id')
        client_secret = config.get('client_secret')
        redirect_uri = config.get('redirect_uri', 'http://localhost:8000/api/auth/callback')
        
        if not client_id or not client_secret:
            raise HTTPException(status_code=400, detail="OAuth2 credentials not configured")
        
        # Generate state for security
        state = secrets.token_urlsafe(32)
        oauth_states[state] = connector_id
        
        # Build OAuth2 authorization URL
        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            "response_type=code&"
            f"redirect_uri={redirect_uri}&"
            "scope=https://www.googleapis.com/auth/drive.readonly "
            "https://www.googleapis.com/auth/drive.file "
            "https://www.googleapis.com/auth/drive.metadata.readonly&"
            f"state={state}&"
            "access_type=offline&"
            "prompt=consent"
        )
        
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authorization failed: {str(e)}")

@router.get("/callback")
async def oauth_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Handle OAuth2 callback from Google"""
    print(f"🔍 OAuth2 Callback Debug:")
    print(f"   Code: {code[:20] + '...' if code else 'None'}")
    print(f"   State: {state}")
    print(f"   Error: {error}")
    
    try:
        if error:
            raise HTTPException(status_code=400, detail=f"OAuth2 error: {error}")
        
        if not code or not state:
            raise HTTPException(status_code=400, detail="Missing authorization code or state")
        
        # Verify state
        if state not in oauth_states:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        connector_id = oauth_states[state]
        del oauth_states[state]  # Clean up
        
        # Get the connector
        connector = db.query(Connector).filter(Connector.id == connector_id).first()
        if not connector:
            raise HTTPException(status_code=404, detail="Connector not found")
        
        config = connector.config or {}
        client_id = config.get('client_id')
        client_secret = config.get('client_secret')
        redirect_uri = config.get('redirect_uri', 'http://localhost:8000/api/auth/callback')
        
        # Exchange code for tokens
        from google_auth_oauthlib.flow import Flow
        
        print(f"🔍 Starting token exchange...")
        print(f"   Client ID: {client_id}")
        print(f"   Redirect URI: {redirect_uri}")
        
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=[
                    'https://www.googleapis.com/auth/drive.readonly',
                    'https://www.googleapis.com/auth/drive.file',
                    'https://www.googleapis.com/auth/drive.metadata.readonly'
                ]
            )
            
            print(f"🔍 Flow created successfully")
            # Set the redirect URI explicitly for token exchange
            flow.redirect_uri = redirect_uri
            flow.fetch_token(code=code)
            credentials = flow.credentials
            print(f"🔍 Token fetch completed")
            
        except Exception as token_error:
            print(f"❌ Token exchange failed: {token_error}")
            raise token_error
        
        print(f"🔍 Token Exchange Successful:")
        print(f"   Token: {credentials.token[:20] + '...' if credentials.token else 'None'}")
        print(f"   Refresh Token: {credentials.refresh_token[:20] + '...' if credentials.refresh_token else 'None'}")
        print(f"   Scopes: {credentials.scopes}")
        
        # Store tokens in connector config
        token_info = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        try:
            config['token_info'] = token_info
            connector.config = config
            connector.status = ConnectorStatus.CONNECTED
            db.commit()
            print(f"🔍 Database update successful")
        except Exception as db_error:
            print(f"❌ Database update failed: {db_error}")
            raise db_error
        
        print(f"🔍 Connector Updated:")
        print(f"   Status: {connector.status}")
        print(f"   Config keys: {list(config.keys())}")
        
        # Redirect back to the main frontend page with success
        return RedirectResponse(
            url=f"http://localhost:3000?success=true&connector_id={connector_id}"
        )
        
    except Exception as e:
        print(f"❌ OAuth2 Callback Error: {e}")
        # Redirect back to the main frontend page with error
        return RedirectResponse(
            url=f"http://localhost:3000?error={str(e)}"
        )

@router.post("/google/refresh/{connector_id}")
async def refresh_google_tokens(connector_id: int, db: Session = Depends(get_db)):
    """Refresh OAuth2 tokens for Google Drive connector"""
    try:
        connector = db.query(Connector).filter(Connector.id == connector_id).first()
        if not connector:
            raise HTTPException(status_code=404, detail="Connector not found")
        
        # Create connector instance and refresh tokens
        connector_instance = GoogleDriveConnector(connector, db)
        credentials = connector_instance._get_credentials()
        
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            
            # Update stored tokens
            config = connector.config or {}
            config['token_info'] = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            connector.config = config
            db.commit()
            
            return {"success": True, "message": "Tokens refreshed successfully"}
        else:
            return {"success": False, "message": "No valid credentials to refresh"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")
