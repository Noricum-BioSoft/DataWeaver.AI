import React, { useState, useRef, useEffect } from 'react';
import PromptBox from './PromptBox';
import ChatHistory from './ChatHistory';
import WorkflowCreationForm from './WorkflowCreationForm';
import { parseWorkflowCommand, isWorkflowCreationCommand } from '../utils/workflowParser';
import { bioMatcherApi } from '../services/api';
import './AIChatMain.css';

interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  result?: any;
}

interface AIChatMainProps {
  onPromptSelect?: (prompt: string) => void;
}

const AIChatMain: React.FC<AIChatMainProps> = ({ onPromptSelect }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'ai',
      content: 'Hello! I\'m your AI assistant. I can help you with data sources, workflows, and visualizations. What would you like to do?',
      timestamp: new Date(),
      result: null
    }
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [showWorkflowForm, setShowWorkflowForm] = useState(false);
  const [workflowFormData, setWorkflowFormData] = useState<any>({});
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const createWorkflowSession = async () => {
    try {
      const result = await bioMatcherApi.createWorkflowSession();
      setCurrentSessionId(result.session_id);
      return result.session_id;
    } catch (error) {
      console.error('Failed to create workflow session:', error);
      return null;
    }
  };

  const handlePromptSubmit = async (prompt: string) => {
    if (!prompt.trim()) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: prompt,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);

    // Check for visualization requests first (higher priority)
    const lowerPrompt = prompt.toLowerCase();
    if ((lowerPrompt.includes('plot') || lowerPrompt.includes('visualize') || lowerPrompt.includes('chart') || lowerPrompt.includes('graph') || lowerPrompt.includes('scatter') || lowerPrompt.includes('histogram') || lowerPrompt.includes('correlation')) && (uploadedFiles.length > 0 || currentSessionId)) {
      await handleVisualization(prompt);
    }
    // Check if this is a workflow creation command
    else if (isWorkflowCreationCommand(prompt)) {
      const parsed = parseWorkflowCommand(prompt);
      
      // Show workflow creation form with parsed data
      setWorkflowFormData({
        name: parsed.workflowName || '',
        description: parsed.description || '',
        status: parsed.status || 'draft',
        metadata: parsed.metadata || {}
      });
      setShowWorkflowForm(true);
      
      // Add AI response indicating form will be shown
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `I'll help you create the workflow "${parsed.workflowName || 'New Workflow'}". Please fill out the details in the form below.`,
        timestamp: new Date(),
        result: null
      };

      setMessages(prev => [...prev, aiMessage]);
      setIsProcessing(false);
    } else {
      // Check if this is a merge request
      if ((lowerPrompt.includes('merge') || lowerPrompt.includes('combine')) && uploadedFiles.length >= 2) {
        await handleFileMerge();
      } else {
        // Simulate AI processing for other commands
        setTimeout(() => {
          const aiResponse = generateAIResponse(prompt);
          const aiMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'ai',
            content: aiResponse.message,
            timestamp: new Date(),
            result: aiResponse.result
          };

          setMessages(prev => [...prev, aiMessage]);
          setIsProcessing(false);
        }, 1500);
      }
    }
  };

  const handleFileMerge = async () => {
    try {
      if (uploadedFiles.length < 2) {
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: 'I need at least 2 CSV files to merge them. Please upload more files.',
          timestamp: new Date(),
          result: null
        };
        setMessages(prev => [...prev, aiMessage]);
        setIsProcessing(false);
        return;
      }

      // Create workflow session if not exists
      let sessionId = currentSessionId;
      if (!sessionId) {
        sessionId = await createWorkflowSession();
        if (!sessionId) {
          throw new Error('Failed to create workflow session');
        }
      }

      // Create FormData with the uploaded files and session
      const formData = new FormData();
      formData.append('file1', uploadedFiles[0]);
      formData.append('file2', uploadedFiles[1]);
      formData.append('session_id', sessionId);

      // Call the bio-matcher API to merge files
      const result = await bioMatcherApi.mergeFiles(formData);

      // Create merged CSV content
      const headers = result.headers.join(',');
      const rows = result.rows.map(row => row.join(',')).join('\n');
      const mergedCsv = `${headers}\n${rows}`;

      // Create downloadable blob
      const blob = new Blob([mergedCsv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `✅ Successfully merged your CSV files! I found ${result.matchedRows} matched rows and ${result.unmatchedRows} unmatched rows. The merged data is now stored in your workflow session and ready for visualization.`,
        timestamp: new Date(),
        result: {
          type: 'merged-data',
          data: {
            totalRows: result.totalRows,
            matchedRows: result.matchedRows,
            unmatchedRows: result.unmatchedRows,
            headers: result.headers,
            sampleRows: result.rows.slice(0, 5), // Show first 5 rows
            downloadUrl: url,
            fileName: `merged_${uploadedFiles[0].name.replace('.csv', '')}_${uploadedFiles[1].name.replace('.csv', '')}.csv`,
            sessionId: sessionId,
            workflowStep: result.workflow_step
          }
        }
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ Sorry, I couldn't merge the files. Please make sure both files are valid CSV files with matching ID columns.`,
        timestamp: new Date(),
        result: null
      };
      setMessages(prev => [...prev, aiMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleVisualization = async (prompt: string) => {
    try {
      // Determine if we should use session data or uploaded file
      const useSessionData = currentSessionId && uploadedFiles.length === 0;
      
      if (!useSessionData && uploadedFiles.length === 0) {
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: 'I need either uploaded files or merged data from a previous step to generate a visualization. Please upload files or merge data first.',
          timestamp: new Date(),
          result: null
        };
        setMessages(prev => [...prev, aiMessage]);
        setIsProcessing(false);
        return;
      }

      const file = uploadedFiles.length > 0 ? uploadedFiles[0] : undefined;
      
      // Determine plot type from prompt
      const lowerPrompt = prompt.toLowerCase();
      let plotType = 'scatter';
      if (lowerPrompt.includes('histogram')) plotType = 'histogram';
      else if (lowerPrompt.includes('correlation') || lowerPrompt.includes('heatmap')) plotType = 'correlation';
      else if (lowerPrompt.includes('box') || lowerPrompt.includes('boxplot')) plotType = 'boxplot';
      
      // Create workflow session if not exists and using session data
      let sessionId = currentSessionId;
      if (useSessionData && !sessionId) {
        sessionId = await createWorkflowSession();
        if (!sessionId) {
          throw new Error('Failed to create workflow session');
        }
      }

      // Generate visualization
      const result = await bioMatcherApi.generateVisualization(
        file,
        plotType,
        undefined, // xColumn - let backend auto-detect
        undefined, // yColumn - let backend auto-detect
        sessionId || undefined,
        useSessionData || false
      );

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `📊 Here's your ${plotType} visualization! I've analyzed the data and created a chart showing the relationships in your dataset.`,
        timestamp: new Date(),
        result: {
          type: 'visualization',
          data: {
            plotType: result.plot_type,
            plotData: result.plot_data,
            columns: result.columns,
            dataShape: result.data_shape,
            numericColumns: result.numeric_columns,
            sessionId: result.session_id,
            workflowStep: result.workflow_step
          }
        }
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ Sorry, I couldn't generate the visualization. Please make sure you have valid data and try again.`,
        timestamp: new Date(),
        result: null
      };
      setMessages(prev => [...prev, aiMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const generateAIResponse = (prompt: string) => {
    const lowerPrompt = prompt.toLowerCase();
    
    // Handle file upload messages
    if (lowerPrompt.includes('uploaded') && lowerPrompt.includes('csv file')) {
      return {
        message: 'Great! I can see you\'ve uploaded CSV files. I can help you analyze, process, or merge these files. What would you like me to do with them?',
        result: {
          type: 'file-upload',
          data: {
            suggestions: [
              'Analyze the data structure and show me a summary',
              'Merge multiple CSV files if you have more',
              'Create visualizations from the data',
              'Process the data for machine learning',
              'Export the data in a different format'
            ]
          }
        }
      };
    }
    
    // Handle merge requests
    if ((lowerPrompt.includes('merge') || lowerPrompt.includes('combine')) && uploadedFiles.length >= 2) {
      return {
        message: 'I\'ll merge your CSV files for you. Let me process them...',
        result: {
          type: 'merge-request',
          data: {
            files: uploadedFiles.map(f => f.name)
          }
        }
      };
    }

    // Handle visualization requests
    if ((lowerPrompt.includes('plot') || lowerPrompt.includes('visualize') || lowerPrompt.includes('chart') || lowerPrompt.includes('graph')) && uploadedFiles.length > 0) {
      return {
        message: 'I\'ll create visualizations from your data. Let me analyze the structure and generate some plots...',
        result: {
          type: 'visualization-request',
          data: {
            files: uploadedFiles.map(f => f.name),
            suggestions: [
              'Create a scatter plot of Activity_Score vs Stability_Index',
              'Show a histogram of Expression_Level',
              'Generate a correlation heatmap',
              'Create a box plot of Activity_Score by mutation type',
              'Show a line plot of trends over sequence position'
            ]
          }
        }
      };
    }
    
    // Simple rules-based response system
    if (lowerPrompt.includes('connect') && lowerPrompt.includes('google')) {
      return {
        message: 'I\'ll help you connect to Google Drive. Let me check your current connections and set up the integration.',
        result: {
          type: 'connector',
          data: {
            provider: 'Google Drive',
            status: 'connecting',
            steps: ['Authenticating...', 'Setting up permissions...', 'Testing connection...']
          }
        }
      };
    }

    if (lowerPrompt.includes('workflow') || lowerPrompt.includes('pipeline')) {
      return {
        message: 'Here are your current workflows and pipelines. I can help you create new ones or modify existing ones.',
        result: {
          type: 'workflow-list',
          data: [
            { id: 1, name: 'Data Processing Pipeline', status: 'running', progress: 75 },
            { id: 2, name: 'Vendor Data Sync', status: 'completed', progress: 100 },
            { id: 3, name: 'Analytics Dashboard', status: 'pending', progress: 0 }
          ]
        }
      };
    }

    if (lowerPrompt.includes('visualize') || lowerPrompt.includes('chart')) {
      return {
        message: 'I\'ll create a visualization for you. Here\'s what I found based on your request.',
        result: {
          type: 'chart',
          data: {
            type: 'line',
            title: 'Data Processing Trends',
            data: [
              { month: 'Jan', value: 65 },
              { month: 'Feb', value: 78 },
              { month: 'Mar', value: 90 },
              { month: 'Apr', value: 85 },
              { month: 'May', value: 95 },
              { month: 'Jun', value: 88 }
            ]
          }
        }
      };
    }

    if (lowerPrompt.includes('file') || lowerPrompt.includes('dataset')) {
      return {
        message: 'Here are your recent files and datasets. I can help you process or analyze any of them.',
        result: {
          type: 'file-list',
          data: [
            { id: 1, name: 'Sales Data Q1 2024.csv', size: '2.3 MB', type: 'CSV', status: 'processed' },
            { id: 2, name: 'Customer Analytics.json', size: '1.8 MB', type: 'JSON', status: 'processing' },
            { id: 3, name: 'Inventory Report.xlsx', size: '4.1 MB', type: 'Excel', status: 'processed' }
          ]
        }
      };
    }

    // Default response
    return {
      message: 'I understand you want to work with your data. Let me help you with that. What specific action would you like me to take?',
      result: {
        type: 'suggestions',
        data: [
          'Show me my recent files',
          'Connect to a new data source',
          'Create a new workflow',
          'Generate a visualization'
        ]
      }
    };
  };

  const handleVoiceToggle = () => {
    setIsListening(!isListening);
    // TODO: Implement voice input
  };

  const handleWorkflowCreated = (workflow: any) => {
    // Add success message to chat
    const successMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      type: 'ai',
      content: `✅ Workflow "${workflow.name}" has been created successfully! You can now add files and configure steps.`,
      timestamp: new Date(),
      result: {
        type: 'workflow-created',
        data: workflow
      }
    };

    setMessages(prev => [...prev, successMessage]);
  };

  const handleWorkflowFormClose = () => {
    setShowWorkflowForm(false);
    setWorkflowFormData({});
  };

  const handleFileUpload = (files: File[]) => {
    // Handle file uploads - this could trigger file processing, analysis, etc.
    console.log('Files uploaded:', files);
    
    // Store uploaded files for later use
    setUploadedFiles(prev => [...prev, ...files]);
    
    // You could add logic here to:
    // 1. Upload files to backend
    // 2. Process files for analysis
    // 3. Create datasets from files
    // 4. Generate insights from the data
    
    // For now, we'll just log the files and let the AI handle the response
    // In a real implementation, you might:
    // - Upload files to your backend storage
    // - Process the CSV data
    // - Extract metadata and structure
    // - Generate initial insights
    // - Store file references for later use
    
    files.forEach(file => {
      console.log(`Processing file: ${file.name} (${file.size} bytes)`);
      // Here you could add actual file processing logic
    });
  };

  return (
    <main className="ai-chat-main">
      <div className="chat-container">
        <ChatHistory messages={messages} isProcessing={isProcessing} />
        <div ref={messagesEndRef} />
      </div>
      
      <div className="prompt-section">
        <PromptBox 
          onSubmit={handlePromptSubmit}
          onVoiceToggle={handleVoiceToggle}
          isListening={isListening}
          isProcessing={isProcessing}
          onFileUpload={handleFileUpload}
        />
      </div>

      <WorkflowCreationForm
        isOpen={showWorkflowForm}
        onClose={handleWorkflowFormClose}
        onWorkflowCreated={handleWorkflowCreated}
        initialData={workflowFormData}
      />
    </main>
  );
};

export default AIChatMain; 