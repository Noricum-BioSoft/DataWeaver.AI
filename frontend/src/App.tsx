import React, { useState } from 'react';
import './App.css';
import SidebarLayout from './components/SidebarLayout';
import AIChatLayout from './components/AIChatLayout';
import UIThemeToggle from './components/UIThemeToggle';

const App: React.FC = () => {
  // Default to AI Chat interface
  const [currentTheme, setCurrentTheme] = useState<'sidebar' | 'dashboard'>('dashboard');

  const handleThemeChange = (theme: 'sidebar' | 'dashboard') => {
    setCurrentTheme(theme);
  };

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
    </div>
  );
};

export default App; 