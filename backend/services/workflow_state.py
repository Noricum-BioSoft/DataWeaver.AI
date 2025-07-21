import uuid
from typing import Dict, Any, Optional, List
import pandas as pd
import json
from datetime import datetime, timedelta

class WorkflowStateManager:
    """Manages workflow state and session data for multi-step workflows"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=24)  # Sessions expire after 24 hours
    
    def create_session(self) -> str:
        """Create a new workflow session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'created_at': datetime.now(),
            'last_updated': datetime.now(),
            'data': {},
            'steps': []
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data if it exists and is not expired"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        if datetime.now() - session['created_at'] > self.session_timeout:
            del self.sessions[session_id]
            return None
        
        session['last_updated'] = datetime.now()
        return session
    
    def update_session_data(self, session_id: str, key: str, value: Any) -> bool:
        """Update session data with new key-value pair"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session['data'][key] = value
        session['last_updated'] = datetime.now()
        return True
    
    def get_session_data(self, session_id: str, key: str) -> Optional[Any]:
        """Get specific data from session"""
        session = self.get_session(session_id)
        if not session:
            return None
        return session['data'].get(key)
    
    def add_workflow_step(self, session_id: str, step_type: str, step_data: Dict[str, Any]) -> bool:
        """Add a workflow step to the session history"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        step = {
            'type': step_type,
            'timestamp': datetime.now(),
            'data': step_data
        }
        session['steps'].append(step)
        session['last_updated'] = datetime.now()
        return True
    
    def get_workflow_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get the workflow history for a session"""
        session = self.get_session(session_id)
        if not session:
            return []
        return session['steps']
    
    def store_uploaded_file(self, session_id: str, file_data: Dict[str, Any]) -> bool:
        """Store individual uploaded file data in session"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        if 'uploaded_files' not in session['data']:
            session['data']['uploaded_files'] = []
        
        session['data']['uploaded_files'].append(file_data)
        session['last_updated'] = datetime.now()
        return True
    
    def get_uploaded_files(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all uploaded files from session"""
        session = self.get_session(session_id)
        if not session:
            return []
        return session['data'].get('uploaded_files', [])
    
    def store_merged_data(self, session_id: str, merged_data: Dict[str, Any]) -> bool:
        """Store merged CSV data in session"""
        return self.update_session_data(session_id, 'merged_data', merged_data)
    
    def get_merged_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get stored merged data from session"""
        return self.get_session_data(session_id, 'merged_data')
    
    def store_visualization_data(self, session_id: str, viz_data: Dict[str, Any]) -> bool:
        """Store visualization data in session"""
        return self.update_session_data(session_id, 'visualization_data', viz_data)
    
    def get_visualization_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get stored visualization data from session"""
        return self.get_session_data(session_id, 'visualization_data')
    
    def store_filtered_data(self, session_id: str, filtered_data: Dict[str, Any]) -> bool:
        """Store filtered/queried data in session"""
        return self.update_session_data(session_id, 'filtered_data', filtered_data)
    
    def get_filtered_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get stored filtered data from session"""
        return self.get_session_data(session_id, 'filtered_data')
    
    def clear_session(self, session_id: str) -> bool:
        """Clear all data from a session"""
        if session_id in self.sessions:
            self.sessions[session_id] = {
                'created_at': datetime.now(),
                'last_updated': datetime.now(),
                'data': {},
                'steps': []
            }
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session['created_at'] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]

# Global instance
workflow_state_manager = WorkflowStateManager() 