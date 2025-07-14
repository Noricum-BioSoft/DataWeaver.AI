import React, { useState } from 'react';
import './App.css';
import SidebarLayout from './components/SidebarLayout';
import AIChatLayout from './components/AIChatLayout';
import UIThemeToggle from './components/UIThemeToggle';

const App: React.FC = () => {
  const [currentTheme, setCurrentTheme] = useState<'sidebar' | 'dashboard'>('sidebar');

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
      
      {currentTheme === 'sidebar' ? (
        <SidebarLayout />
      ) : (
        <AIChatLayout />
      )}
    </div>
  );
};

export default App; 