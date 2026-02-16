"""
Google Drive Connector Implementation
Based on Google Drive API documentation: https://developers.google.com/workspace/drive/api/guides/about-sdk
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io

from sqlalchemy.orm import Session
from ..connector_factory import BaseConnector
from ...models.connector import Connector as ConnectorModel, ConnectorType, ConnectorStatus, AuthenticationType
from ...schemas.connector import ConnectorCreate, ConnectorUpdate


class GoogleDriveConnector(BaseConnector):
    """Google Drive API Connector Implementation"""
    
    def __init__(self, connector: ConnectorModel, db: Session):
        super().__init__(connector, db)
        self.connector_type = ConnectorType.GOOGLE_WORKSPACE
        self.auth_type = AuthenticationType.OAUTH2
        
        # Google Drive API scopes
        self.scopes = [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.metadata.readonly'
        ]
        
        self.service = None
        self.credentials = None
        
    def _get_credentials(self) -> Optional[Credentials]:
        """Get OAuth2 credentials for Google Drive API"""
        try:
            config = self.connector.config or {}
            
            # Check if we have stored credentials
            if 'token_info' in config:
                credentials = Credentials.from_authorized_user_info(
                    config['token_info'], self.scopes
                )
                
                # Refresh if expired
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                    # Update stored token
                    config['token_info'] = {
                        'token': credentials.token,
                        'refresh_token': credentials.refresh_token,
                        'token_uri': credentials.token_uri,
                        'client_id': credentials.client_id,
                        'client_secret': credentials.client_secret,
                        'scopes': credentials.scopes
                    }
                    return credentials
                    
                return credentials if credentials and not credentials.expired else None
            
            # If no stored credentials, we need to initiate OAuth2 flow
            # For now, return None to indicate credentials needed
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting credentials: {e}")
            return None
    
    def _build_service(self) -> bool:
        """Build Google Drive API service"""
        try:
            credentials = self._get_credentials()
            if not credentials:
                self.logger.error("No valid credentials available")
                return False
                
            self.service = build('drive', 'v3', credentials=credentials)
            return True
            
        except Exception as e:
            self.logger.error(f"Error building Drive service: {e}")
            return False
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Google Drive API"""
        try:
            credentials = self._get_credentials()
            if not credentials:
                return {
                    'success': False,
                    'message': 'OAuth2 credentials required. Please complete the OAuth2 flow to get access tokens.',
                    'details': {
                        'error': 'No valid credentials',
                        'next_step': 'Complete OAuth2 authorization flow',
                        'client_id': self.connector.config.get('client_id') if self.connector.config else None
                    }
                }
            
            if not self._build_service():
                return {
                    'success': False,
                    'message': 'Failed to build Drive service - check credentials',
                    'details': {'error': 'Service build failed'}
                }
            
            # Test by getting user info
            about = self.service.about().get(fields='user').execute()
            user_info = about.get('user', {})
            
            return {
                'success': True,
                'message': f'Successfully connected to Google Drive as {user_info.get("displayName", "Unknown User")}',
                'details': {
                    'user_email': user_info.get('emailAddress'),
                    'user_name': user_info.get('displayName'),
                    'permission_id': user_info.get('permissionId')
                }
            }
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return {
                'success': False,
                'message': f'Connection test failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    async def discover_data_sources(self) -> List[Dict[str, Any]]:
        """Discover available data sources in Google Drive"""
        try:
            if not self._build_service():
                return []
            
            data_sources = []
            
            # Get files and folders from My Drive
            results = self.service.files().list(
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, parents, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            for file in files:
                # Filter for common data file types
                mime_type = file.get('mimeType', '')
                if self._is_data_file(mime_type, file.get('name', '')):
                    data_sources.append({
                        'id': file['id'],
                        'name': file['name'],
                        'type': 'file',
                        'path': f"/files/{file['id']}",
                        'mime_type': mime_type,
                        'size': file.get('size'),
                        'modified_time': file.get('modifiedTime'),
                        'web_link': file.get('webViewLink'),
                        'metadata': {
                            'file_id': file['id'],
                            'parents': file.get('parents', []),
                            'trashed': file.get('trashed', False)
                        }
                    })
            
            # Get shared drives (if user has access)
            try:
                drives = self.service.drives().list(pageSize=100).execute()
                for drive in drives.get('drives', []):
                    data_sources.append({
                        'id': drive['id'],
                        'name': f"Shared Drive: {drive['name']}",
                        'type': 'shared_drive',
                        'path': f"/drives/{drive['id']}",
                        'mime_type': 'application/vnd.google-apps.folder',
                        'metadata': {
                            'drive_id': drive['id'],
                            'drive_name': drive['name'],
                            'capabilities': drive.get('capabilities', {})
                        }
                    })
            except Exception as e:
                self.logger.warning(f"Could not access shared drives: {e}")
            
            return data_sources
            
        except Exception as e:
            self.logger.error(f"Error discovering data sources: {e}")
            return []
    
    def _is_data_file(self, mime_type: str, filename: str) -> bool:
        """Check if file is a data file we can process"""
        data_mime_types = [
            'text/csv',
            'application/json',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'application/xml',
            'text/xml'
        ]
        
        data_extensions = ['.csv', '.json', '.xlsx', '.xls', '.txt', '.xml', '.tsv']
        
        # Check MIME type
        if mime_type in data_mime_types:
            return True
            
        # Check file extension
        filename_lower = filename.lower()
        return any(filename_lower.endswith(ext) for ext in data_extensions)
    
    async def extract_data(self, source_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract data from a Google Drive file"""
        try:
            if not self._build_service():
                return {
                    'success': False,
                    'message': 'Failed to build Drive service',
                    'data': None
                }
            
            # Get file metadata
            file_metadata = self.service.files().get(
                fileId=source_id,
                fields='id,name,mimeType,size,modifiedTime,webViewLink'
            ).execute()
            
            mime_type = file_metadata.get('mimeType', '')
            file_name = file_metadata.get('name', '')
            
            # Download file content
            if mime_type == 'text/csv':
                return await self._extract_csv_data(source_id, file_metadata)
            elif mime_type == 'application/json':
                return await self._extract_json_data(source_id, file_metadata)
            elif mime_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                return await self._extract_excel_data(source_id, file_metadata)
            elif mime_type == 'text/plain':
                return await self._extract_text_data(source_id, file_metadata)
            else:
                return {
                    'success': False,
                    'message': f'Unsupported file type: {mime_type}',
                    'data': None
                }
                
        except Exception as e:
            self.logger.error(f"Error extracting data from {source_id}: {e}")
            return {
                'success': False,
                'message': f'Extraction failed: {str(e)}',
                'data': None
            }
    
    async def _extract_csv_data(self, file_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from CSV file"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            content = file_content.getvalue().decode('utf-8')
            
            # Parse CSV content
            lines = content.split('\n')
            if not lines:
                return {
                    'success': False,
                    'message': 'Empty CSV file',
                    'data': None
                }
            
            # Extract headers
            headers = lines[0].split(',')
            
            # Extract data rows
            data_rows = []
            for line in lines[1:]:
                if line.strip():
                    values = line.split(',')
                    row = dict(zip(headers, values))
                    data_rows.append(row)
            
            return {
                'success': True,
                'message': f'Successfully extracted {len(data_rows)} rows from CSV',
                'data': {
                    'file_name': metadata.get('name'),
                    'file_id': file_id,
                    'headers': headers,
                    'rows': data_rows,
                    'row_count': len(data_rows),
                    'column_count': len(headers),
                    'format': 'csv'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'CSV extraction failed: {str(e)}',
                'data': None
            }
    
    async def _extract_json_data(self, file_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from JSON file"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            content = file_content.getvalue().decode('utf-8')
            data = json.loads(content)
            
            return {
                'success': True,
                'message': f'Successfully extracted JSON data',
                'data': {
                    'file_name': metadata.get('name'),
                    'file_id': file_id,
                    'content': data,
                    'format': 'json'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'JSON extraction failed: {str(e)}',
                'data': None
            }
    
    async def _extract_excel_data(self, file_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from Excel file"""
        try:
            # For Excel files, we'll return metadata since parsing requires additional libraries
            return {
                'success': True,
                'message': f'Excel file detected: {metadata.get("name")}',
                'data': {
                    'file_name': metadata.get('name'),
                    'file_id': file_id,
                    'format': 'excel',
                    'note': 'Excel parsing requires additional processing'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Excel extraction failed: {str(e)}',
                'data': None
            }
    
    async def _extract_text_data(self, file_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from text file"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            content = file_content.getvalue().decode('utf-8')
            lines = content.split('\n')
            
            return {
                'success': True,
                'message': f'Successfully extracted {len(lines)} lines from text file',
                'data': {
                    'file_name': metadata.get('name'),
                    'file_id': file_id,
                    'content': content,
                    'lines': lines,
                    'line_count': len(lines),
                    'format': 'text'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Text extraction failed: {str(e)}',
                'data': None
            }
    
    async def sync_data_sources(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sync data from Google Drive sources"""
        try:
            # Discover available sources
            sources = await self.discover_data_sources()
            
            if not sources:
                return {
                    'success': True,
                    'message': 'No data sources found to sync',
                    'records_processed': 0
                }
            
            # Extract data from each source
            extracted_data = []
            for source in sources[:10]:  # Limit to 10 sources for demo
                if source['type'] == 'file':
                    result = await self.extract_data(source['id'])
                    if result['success']:
                        extracted_data.append({
                            'source': source,
                            'data': result['data']
                        })
            
            return {
                'success': True,
                'message': f'Successfully synced {len(extracted_data)} data sources',
                'records_processed': len(extracted_data),
                'data': extracted_data
            }
            
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            return {
                'success': False,
                'message': f'Sync failed: {str(e)}',
                'records_processed': 0
            }
    
    async def sync_data(self, data_sources: List[Any]) -> Dict[str, Any]:
        """Sync data from multiple data sources - required by BaseConnector"""
        try:
            # For Google Drive, we'll use the sync_data_sources method
            return await self.sync_data_sources()
        except Exception as e:
            self.logger.error(f"Sync data failed: {e}")
            return {
                'success': False,
                'message': f'Sync data failed: {str(e)}',
                'data_sources_synced': 0
            }
    
    def get_required_config(self) -> Dict[str, Any]:
        """Get required configuration for Google Drive connector"""
        return {
            'client_id': {
                'type': 'string',
                'required': True,
                'description': 'Google OAuth2 Client ID'
            },
            'client_secret': {
                'type': 'string',
                'required': True,
                'description': 'Google OAuth2 Client Secret'
            },
            'redirect_uri': {
                'type': 'string',
                'required': False,
                'description': 'OAuth2 redirect URI (default: http://localhost:3000/auth/callback)'
            }
        }
    
    def get_supported_file_types(self) -> List[str]:
        """Get supported file types for Google Drive connector"""
        return [
            'text/csv',
            'application/json',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'application/xml',
            'text/xml'
        ]
