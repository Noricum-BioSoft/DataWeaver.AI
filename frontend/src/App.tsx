import React, { useState } from 'react';
import './App.css';
import SidebarLayout from './components/SidebarLayout';
import AIChatLayout from './components/AIChatLayout';
import BioMatcherPage from './components/BioMatcherPage';
import UIThemeToggle from './components/UIThemeToggle';

const App: React.FC = () => {
  // Default to AI Chat interface
  const [currentTheme, setCurrentTheme] = useState<'sidebar' | 'dashboard' | 'bio-matcher'>('dashboard');

  const handleThemeChange = (theme: 'sidebar' | 'dashboard' | 'bio-matcher') => {
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
      {currentTheme === 'bio-matcher' && <BioMatcherPage />}
    </div>
  );
};

export default App; 