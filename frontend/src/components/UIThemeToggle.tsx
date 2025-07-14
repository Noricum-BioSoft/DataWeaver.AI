import React from 'react';
import { Layout, Grid } from 'lucide-react';
import './UIThemeToggle.css';

interface UIThemeToggleProps {
  currentTheme: 'sidebar' | 'dashboard';
  onThemeChange: (theme: 'sidebar' | 'dashboard') => void;
}

const UIThemeToggle: React.FC<UIThemeToggleProps> = ({
  currentTheme,
  onThemeChange
}) => {
  return (
    <div className="ui-theme-toggle">
      <div className="toggle-container">
        <button
          className={`toggle-button ${currentTheme === 'sidebar' ? 'active' : ''}`}
          onClick={() => onThemeChange('sidebar')}
          title="Sidebar Layout"
        >
          <Layout size={16} />
          <span>Sidebar</span>
        </button>
        <button
          className={`toggle-button ${currentTheme === 'dashboard' ? 'active' : ''}`}
          onClick={() => onThemeChange('dashboard')}
          title="AI Chat Interface"
        >
          <Grid size={16} />
          <span>AI Chat</span>
        </button>
      </div>
    </div>
  );
};

export default UIThemeToggle; 