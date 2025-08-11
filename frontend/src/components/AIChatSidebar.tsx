import React from 'react';
import { 
  Home, 
  FileText, 
  Workflow, 
  Link, 
  Building, 
  GitBranch, 
  BarChart3,
  MessageSquare,
  ChevronLeft
} from 'lucide-react';
import './AIChatSidebar.css';

interface AIChatSidebarProps {
  isVisible: boolean;
  onToggle: () => void;
  onPromptSelect: (prompt: string) => void;
  onChatClick?: () => void;
  onFilesClick?: () => void;
  onConnectorsClick?: () => void;
  onWorkflowsClick?: () => void;
  onVendorsClick?: () => void;
  onPipelinesClick?: () => void;
  onDashboardClick?: () => void;
}

const AIChatSidebar: React.FC<AIChatSidebarProps> = ({ 
  isVisible,
  onToggle,
  onPromptSelect,
  onChatClick,
  onFilesClick,
  onConnectorsClick,
  onWorkflowsClick,
  onVendorsClick,
  onPipelinesClick,
  onDashboardClick
}) => {
  const menuItems = [
    {
      id: 'home',
      icon: Home,
      label: 'Home',
      prompt: 'Show me an overview of my data and workflows'
    },
    {
      id: 'chat',
      icon: MessageSquare,
      label: 'Chat',
      prompt: 'Start a new chat or manage existing conversations'
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
    <aside className={`ai-chat-sidebar ${isVisible ? 'sidebar-visible' : 'sidebar-hidden'}`}>
      <div className="sidebar-header">
        <div className="sidebar-header-content">
          <div className="sidebar-title-section">
            <MessageSquare size={24} className="sidebar-icon" />
            <h2 className="sidebar-title">AI Assistant</h2>
          </div>
          <button 
            className="sidebar-toggle-btn"
            onClick={onToggle}
            aria-label={isVisible ? 'Hide sidebar' : 'Show sidebar'}
            title={`${isVisible ? 'Hide' : 'Show'} sidebar (Ctrl+B)`}
          >
            <ChevronLeft 
              size={20} 
              className={`toggle-icon ${isVisible ? 'rotate' : ''}`}
            />
          </button>
        </div>
      </div>

      <nav className="sidebar-nav">
        <ul className="nav-list">
          {menuItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <li key={item.id} className="nav-item">
                <button
                  className="nav-button"
                  onClick={() => {
                    // Handle specific sidebar actions
                    switch (item.id) {
                      case 'chat':
                        onChatClick?.();
                        break;
                      case 'files':
                        onFilesClick?.();
                        break;
                      case 'workflows':
                        onWorkflowsClick?.();
                        break;
                      case 'connectors':
                        onConnectorsClick?.();
                        break;
                      case 'vendors':
                        onVendorsClick?.();
                        break;
                      case 'pipelines':
                        onPipelinesClick?.();
                        break;
                      case 'dashboard':
                        onDashboardClick?.();
                        break;
                      default:
                        onPromptSelect(item.prompt);
                    }
                  }}
                  title={`${item.prompt}${item.id === 'chat' ? ' - Start new conversations and manage existing chat history' :
                    item.id === 'workflows' ? ' - User-defined business processes and data analysis tasks' : 
                    item.id === 'pipelines' ? ' - Technical infrastructure for data processing and ETL operations' : 
                    item.id === 'connectors' ? ' - External data source integrations and APIs' :
                    item.id === 'vendors' ? ' - Third-party data providers and their datasets' :
                    item.id === 'files' ? ' - Uploaded and processed data files' :
                    item.id === 'dashboard' ? ' - System metrics and performance monitoring' : ''}`}
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