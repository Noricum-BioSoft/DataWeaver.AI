import React from 'react';
import { Layout, Grid, Database } from 'lucide-react';
import './UIThemeToggle.css';

interface UIThemeToggleProps {
  currentTheme: 'sidebar' | 'dashboard' | 'connectors';
  onThemeChange: (theme: 'sidebar' | 'dashboard' | 'connectors') => void;
}

const UIThemeToggle: React.FC<UIThemeToggleProps> = ({
  currentTheme,
  onThemeChange
}) => {
  return (
    <div className="ui-theme-toggle">
      <div className="toggle-container">
        {/* AI Chat button - primary option */}
        <button
          className={`toggle-button ${currentTheme === 'dashboard' ? 'active' : ''}`}
          onClick={() => onThemeChange('dashboard')}
          title="AI Chat Interface"
        >
          <Grid size={16} />
          <span>AI Chat</span>
        </button>
        
        {/* Connectors button - secondary option */}
        <button
          className={`toggle-button ${currentTheme === 'connectors' ? 'active' : ''}`}
          onClick={() => onThemeChange('connectors')}
          title="Connector Management"
        >
          <Database size={16} />
          <span>Connectors</span>
        </button>
        
        {/* Sidebar button - tertiary option */}
        <button
          className={`toggle-button ${currentTheme === 'sidebar' ? 'active' : ''}`}
          onClick={() => onThemeChange('sidebar')}
          title="Sidebar Layout"
        >
          <Layout size={16} />
          <span>Sidebar</span>
        </button>
      </div>
    </div>
  );
};

export default UIThemeToggle; 