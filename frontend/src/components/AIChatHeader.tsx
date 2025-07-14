import React, { useState } from 'react';
import { Bell, User, Wifi, WifiOff, Settings, LogOut } from 'lucide-react';
import './AIChatHeader.css';

const AIChatHeader: React.FC = () => {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [systemStatus] = useState<'operational' | 'warning' | 'error'>('operational');

  const getStatusIcon = () => {
    switch (systemStatus) {
      case 'operational':
        return <Wifi size={16} className="status-icon operational" />;
      case 'warning':
        return <Wifi size={16} className="status-icon warning" />;
      case 'error':
        return <WifiOff size={16} className="status-icon error" />;
      default:
        return <Wifi size={16} className="status-icon operational" />;
    }
  };

  const getStatusText = () => {
    switch (systemStatus) {
      case 'operational':
        return 'All Systems Operational';
      case 'warning':
        return 'Some Systems Degraded';
      case 'error':
        return 'System Issues Detected';
      default:
        return 'All Systems Operational';
    }
  };

  return (
    <header className="ai-chat-header">
      <div className="header-left">
        <div className="app-brand">
          <h1 className="app-title">DataWeaver.AI</h1>
          <div className="system-status">
            {getStatusIcon()}
            <span className="status-text">{getStatusText()}</span>
          </div>
        </div>
      </div>

      <div className="header-right">
        <button className="notification-button">
          <Bell size={20} />
          <span className="notification-badge">3</span>
        </button>

        <div className="user-menu-container">
          <button
            className="user-button"
            onClick={() => setShowUserMenu(!showUserMenu)}
          >
            <User size={20} />
            <span>Admin User</span>
          </button>

          {showUserMenu && (
            <div className="user-menu">
              <button className="menu-item">
                <User size={16} />
                <span>Profile</span>
              </button>
              <button className="menu-item">
                <Settings size={16} />
                <span>Settings</span>
              </button>
              <hr className="menu-divider" />
              <button className="menu-item">
                <LogOut size={16} />
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default AIChatHeader; 