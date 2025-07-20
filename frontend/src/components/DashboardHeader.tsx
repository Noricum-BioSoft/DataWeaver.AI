import React, { useState } from 'react';
import { Search, Bell, User, Settings, LogOut } from 'lucide-react';
import './DashboardHeader.css';

const DashboardHeader: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Searching for:', searchQuery);
    // Search functionality will be implemented in future versions
  };

  return (
    <header className="dashboard-header">
      <div className="header-left">
        <h1 className="app-title">DataWeaver.AI</h1>
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-container">
            <Search className="search-icon" size={20} />
            <input
              type="text"
              placeholder="Search workflows, datasets, or files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>
        </form>
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

export default DashboardHeader; 