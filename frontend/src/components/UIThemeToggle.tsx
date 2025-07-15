import React from 'react';
import { Layout, Grid, Database } from 'lucide-react';
import './UIThemeToggle.css';

interface UIThemeToggleProps {
  currentTheme: 'sidebar' | 'dashboard' | 'bio-matcher';
  onThemeChange: (theme: 'sidebar' | 'dashboard' | 'bio-matcher') => void;
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
        
        {/* Bio-Matcher button - secondary option */}
        <button
          className={`toggle-button ${currentTheme === 'bio-matcher' ? 'active' : ''}`}
          onClick={() => onThemeChange('bio-matcher')}
          title="Bio-Matcher"
        >
          <Database size={16} />
          <span>Bio-Matcher</span>
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