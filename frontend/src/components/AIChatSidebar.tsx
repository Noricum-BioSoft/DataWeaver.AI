import React from 'react';
import { 
  Home, 
  FileText, 
  Workflow, 
  Link, 
  Building, 
  GitBranch, 
  BarChart3,
  MessageSquare
} from 'lucide-react';
import './AIChatSidebar.css';

interface AIChatSidebarProps {
  onPromptSelect: (prompt: string) => void;
}

const AIChatSidebar: React.FC<AIChatSidebarProps> = ({ onPromptSelect }) => {
  const menuItems = [
    {
      id: 'home',
      icon: Home,
      label: 'Home',
      prompt: 'Show me an overview of my data and workflows'
    },
    {
      id: 'files',
      icon: FileText,
      label: 'Files',
      prompt: 'Show my recent files and datasets'
    },
    {
      id: 'workflows',
      icon: Workflow,
      label: 'Workflows',
      prompt: 'Display all my active workflows and their status'
    },
    {
      id: 'connectors',
      icon: Link,
      label: 'Connectors',
      prompt: 'Show my connected data sources and their status'
    },
    {
      id: 'vendors',
      icon: Building,
      label: 'Vendors',
      prompt: 'List all vendors and their associated datasets'
    },
    {
      id: 'pipelines',
      icon: GitBranch,
      label: 'Pipelines',
      prompt: 'Show my data processing pipelines and their performance'
    },
    {
      id: 'dashboard',
      icon: BarChart3,
      label: 'Dashboard',
      prompt: 'Create a dashboard with key metrics and visualizations'
    }
  ];

  return (
    <aside className="ai-chat-sidebar">
      <div className="sidebar-header">
        <MessageSquare size={24} className="sidebar-icon" />
        <h2 className="sidebar-title">AI Assistant</h2>
      </div>

      <nav className="sidebar-nav">
        <ul className="nav-list">
          {menuItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <li key={item.id} className="nav-item">
                <button
                  className="nav-button"
                  onClick={() => onPromptSelect(item.prompt)}
                  title={item.prompt}
                >
                  <IconComponent size={20} />
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="sidebar-footer">
        <div className="ai-status">
          <div className="status-indicator online"></div>
          <span>AI Assistant Online</span>
        </div>
      </div>
    </aside>
  );
};

export default AIChatSidebar; 