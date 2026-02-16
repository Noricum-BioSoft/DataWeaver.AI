import React, { useState, useEffect } from 'react';
import './App.css';
import SidebarLayout from './components/SidebarLayout';
import AIChatLayout from './components/AIChatLayout';
import ConnectorManagement from './components/ConnectorManagement';
import UIThemeToggle from './components/UIThemeToggle';

const App: React.FC = () => {
  // Default to AI Chat interface
  const [currentTheme, setCurrentTheme] = useState<'sidebar' | 'dashboard' | 'connectors'>('dashboard');

  const handleThemeChange = (theme: 'sidebar' | 'dashboard' | 'connectors') => {
    setCurrentTheme(theme);
  };

  // Handle OAuth2 callback and popup messages
  useEffect(() => {
    // Check if this is an OAuth2 callback
    const urlParams = new URLSearchParams(window.location.search);
    const success = urlParams.get('success');
    const connectorId = urlParams.get('connector_id');
    const error = urlParams.get('error');

    if (success === 'true' && connectorId) {
      // OAuth2 authorization successful
      console.log('OAuth2 authorization successful for connector:', connectorId);
      
      // Show success message
      alert('✅ Google Drive authorization successful! The connector is now connected.');
      
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
      
    } else if (error) {
      // OAuth2 authorization failed
      console.error('OAuth2 authorization failed:', error);
      
      // Show error message
      alert(`❌ OAuth2 authorization failed: ${error}`);
      
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    // Handle OAuth2 success/error messages from popup
    const handleMessage = (event: MessageEvent) => {
      if (event.origin !== 'http://localhost:3000') return;
      
      if (event.data.type === 'OAUTH2_SUCCESS') {
        console.log('OAuth2 authorization successful:', event.data.connectorId);
        alert('✅ Google Drive authorization successful! The connector is now connected.');
      } else if (event.data.type === 'OAUTH2_ERROR') {
        console.error('OAuth2 authorization failed:', event.data.error);
        alert(`❌ OAuth2 authorization failed: ${event.data.error}`);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  return (
    <div className="App">
      <div className="theme-toggle-container">
        <UIThemeToggle 
          currentTheme={currentTheme} 
          onThemeChange={handleThemeChange} 
        />
      </div>
      
      {currentTheme === 'sidebar' && <SidebarLayout />}
      {currentTheme === 'dashboard' && <AIChatLayout />}
      {currentTheme === 'connectors' && <ConnectorManagement />}
    </div>
  );
};

export default App; 