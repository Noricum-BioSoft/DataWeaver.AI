import React, { useState, useRef, useEffect } from 'react';
import PromptBox from './PromptBox';
import ChatHistory from './ChatHistory';
import WorkflowCreationForm from './WorkflowCreationForm';
import DataQASuggestions from './DataQASuggestions';
import FilesModal from './FilesModal';
import { parseWorkflowCommand, isWorkflowCreationCommand } from '../utils/workflowParser';
import { bioMatcherApi, dataQaApi, generalChatApi } from '../services/api';
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
  onFilesClick?: () => void;
}

const AIChatMain: React.FC<AIChatMainProps> = ({ onPromptSelect, onFilesClick }) => {
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
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showFilesModal, setShowFilesModal] = useState(false);
  const [generatedFiles, setGeneratedFiles] = useState<Array<{
    name: string;
    size: string;
    downloadUrl: string;
    type: string;
  }>>([]);
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

    // Check for specific commands
    const lowerPrompt = prompt.toLowerCase();
    
    // Check for plot explanation requests (highest priority)
    if ((lowerPrompt.includes('explain') && (lowerPrompt.includes('plot') || lowerPrompt.includes('chart') || 
         lowerPrompt.includes('graph') || lowerPrompt.includes('visualization') || lowerPrompt.includes('trend'))) && 
        (uploadedFiles.length > 0 || currentSessionId)) {
      await handlePlotExplanation(prompt);
    }
    // Check for visualization requests (high priority for visual commands)
    else if ((lowerPrompt.includes('plot') || lowerPrompt.includes('visualize') || lowerPrompt.includes('chart') || 
         lowerPrompt.includes('graph') || lowerPrompt.includes('scatter') || lowerPrompt.includes('histogram') || 
         lowerPrompt.includes('correlation matrix') || lowerPrompt.includes('heatmap')) && 
        (uploadedFiles.length > 0 || currentSessionId)) {
      await handleVisualization(prompt);
    }
    // Check for data Q&A requests
    else if ((lowerPrompt.includes('what') || lowerPrompt.includes('how many') || lowerPrompt.includes('show me') || 
         lowerPrompt.includes('tell me') || lowerPrompt.includes('explain') || lowerPrompt.includes('describe') ||
         lowerPrompt.includes('missing') || lowerPrompt.includes('columns') || lowerPrompt.includes('rows') ||
         lowerPrompt.includes('numeric') || lowerPrompt.includes('data type') || lowerPrompt.includes('outlier') ||
         lowerPrompt.includes('average') || lowerPrompt.includes('mean') || lowerPrompt.includes('correlation') ||
         lowerPrompt.includes('unique') || lowerPrompt.includes('distinct') || lowerPrompt.includes('file')) && 
        (uploadedFiles.length > 0 || currentSessionId)) {
      await handleDataQA(prompt);
    }
    // Check for analysis requests
    else if ((lowerPrompt.includes('analyze') || lowerPrompt.includes('analysis') || lowerPrompt.includes('insights') || 
         lowerPrompt.includes('recommendations') || lowerPrompt.includes('explain') || lowerPrompt.includes('understand')) && 
        (uploadedFiles.length > 0 || currentSessionId)) {
      await handleDataAnalysis(prompt);
    }
    // Check for data query requests
    else if ((lowerPrompt.includes('filter') || lowerPrompt.includes('query') || lowerPrompt.includes('show rows') || 
         lowerPrompt.includes('get rows') || lowerPrompt.includes('where') || lowerPrompt.includes('like') || 
         lowerPrompt.includes('contains') || lowerPrompt.includes('is not null') || lowerPrompt.includes('is null')) && 
        (uploadedFiles.length > 0 || currentSessionId)) {
      await handleDataQuery(prompt);
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
      if ((lowerPrompt.includes('merge') || lowerPrompt.includes('combine')) && currentSessionId) {
        // Check if user wants to re-merge
        const wantsReMerge = lowerPrompt.includes('re-merge') || 
                            lowerPrompt.includes('remerge') || 
                            lowerPrompt.includes('merge again') ||
                            lowerPrompt.includes('merge the files again') ||
                            lowerPrompt.includes('force merge');
        
        await handleFileMerge(wantsReMerge);
      } else {
        // Use general AI chat for other commands
        await handleGeneralChat(prompt);
      }
    }
  };

  const handleFileMerge = async (forceRemerge: boolean = false) => {
    try {
      if (!currentSessionId) {
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: 'I need a session to merge files. Please upload files first.',
          timestamp: new Date(),
          result: null
        };
        setMessages(prev => [...prev, aiMessage]);
        setIsProcessing(false);
        return;
      }

      // Use the new session-based merge endpoint
      const formData = new FormData();
      formData.append('session_id', currentSessionId);
      formData.append('force_remerge', forceRemerge.toString());
      
      const result = await bioMatcherApi.mergeSessionFiles(formData, forceRemerge);
      
      // Create download URL for the merged data
      const url = URL.createObjectURL(new Blob([JSON.stringify(result)], { type: 'application/json' }));

      // Determine message based on whether it was cached or re-merged
      let messageContent: string;
      if (result.cached) {
        messageContent = `📋 Using previously merged data (${result.matchedRows} matched rows, ${result.unmatchedRows} unmatched rows). The merged data is ready for visualization.`;
      } else {
        messageContent = `✅ Successfully merged your CSV files! I found ${result.matchedRows} matched rows and ${result.unmatchedRows} unmatched rows. The merged data is now stored in your workflow session and ready for visualization.`;
      }

      const mergedData = {
        totalRows: result.totalRows,
        matchedRows: result.matchedRows,
        unmatchedRows: result.unmatchedRows,
        headers: result.headers,
        sampleRows: result.rows.slice(0, 5), // Show first 5 rows from the 'rows' field
        downloadUrl: url,
        fileName: `merged_${uploadedFiles.map(f => f.name.replace('.csv', '')).join('_')}.csv`,
        sessionId: currentSessionId,
        workflowStep: result.workflow_step,
        cached: result.cached
      };

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: messageContent,
        timestamp: new Date(),
        result: {
          type: 'merged-data',
          data: mergedData
        }
      };

      // Add the generated file to the state
      const generatedFile = {
        name: `merged_${uploadedFiles.map(f => f.name.replace('.csv', '')).join('_')}.csv`,
        size: `${result.totalRows} rows`,
        downloadUrl: url,
        type: 'merged-csv'
      };
      setGeneratedFiles(prev => [...prev, generatedFile]);

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error in handleFileMerge:', error);
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ Sorry, I couldn't merge the files. Please make sure all files are valid CSV files with matching ID columns.`,
        timestamp: new Date(),
        result: null
      };
      setMessages(prev => [...prev, aiMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePlotExplanation = async (prompt: string) => {
    try {
      // Ensure we have session data
      if (!currentSessionId) {
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: 'I need session data to explain the plots. Please upload files or merge data first.',
          timestamp: new Date(),
          result: null
        };
        setMessages(prev => [...prev, aiMessage]);
        setIsProcessing(false);
        return;
      }

      // Extract plot type from prompt or use default
      let plotType = "scatter";
      if (prompt.toLowerCase().includes("correlation")) {
        plotType = "correlation";
      } else if (prompt.toLowerCase().includes("histogram")) {
        plotType = "histogram";
      } else if (prompt.toLowerCase().includes("boxplot")) {
        plotType = "boxplot";
      }

      // Explain the visualization
      const result = await bioMatcherApi.explainVisualization(
        currentSessionId,
        plotType
      );

      // Format the analysis into a readable response
      const analysis = result.analysis;
      let explanation = `Here's my analysis of the ${plotType} visualization:\n\n`;

      if (analysis.error) {
        explanation += `❌ ${analysis.error}`;
      } else {
        // Add trends
        if (analysis.trends && analysis.trends.length > 0) {
          explanation += "**Key Trends:**\n";
          analysis.trends.forEach((trend: string) => {
            explanation += `• ${trend}\n`;
          });
          explanation += "\n";
        }

        // Add correlations
        if (analysis.correlations && analysis.correlations.length > 0) {
          explanation += "**Correlations:**\n";
          analysis.correlations.forEach((corr: any) => {
            explanation += `• ${corr.columns.join(' ↔ ')}: ${corr.strength} correlation (r=${corr.correlation.toFixed(3)})\n`;
          });
          explanation += "\n";
        }

        // Add strong correlations for correlation matrix
        if (analysis.strong_correlations && analysis.strong_correlations.length > 0) {
          explanation += "**Strong Correlations (|r| > 0.7):**\n";
          analysis.strong_correlations.forEach((corr: string) => {
            explanation += `• ${corr}\n`;
          });
          explanation += "\n";
        }

        // Add outliers
        if (analysis.outliers && analysis.outliers.length > 0) {
          explanation += "**Outliers Detected:**\n";
          analysis.outliers.forEach((outlier: string) => {
            explanation += `• ${outlier}\n`;
          });
          explanation += "\n";
        }

        // Add insights
        if (analysis.insights && analysis.insights.length > 0) {
          explanation += "**Key Insights:**\n";
          analysis.insights.forEach((insight: string) => {
            explanation += `• ${insight}\n`;
          });
          explanation += "\n";
        }

        // Add distribution info for histograms
        if (analysis.distribution) {
          explanation += `**Distribution:** ${analysis.distribution}\n\n`;
        }

        // Add group comparisons for boxplots
        if (analysis.group_comparisons && analysis.group_comparisons.length > 0) {
          explanation += "**Group Comparisons:**\n";
          analysis.group_comparisons.forEach((comp: string) => {
            explanation += `• ${comp}\n`;
          });
          explanation += "\n";
        }
      }

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: explanation,
        timestamp: new Date(),
        result: {
          type: 'plot-explanation',
          data: {
            plotType: result.plot_type,
            analysis: result.analysis,
            dataShape: result.data_shape,
            sessionId: result.session_id
          }
        }
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error explaining plot:', error);
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ Sorry, I couldn't explain the plot. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
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
      const useSessionData = currentSessionId;
      const hasData = currentSessionId || uploadedFiles.length > 0;
      
      if (!hasData) {
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

      // Parse the user's visualization request
      const parsedRequest = parseVisualizationRequest(prompt);
      console.log('Parsed visualization request:', parsedRequest);

      // Use the first uploaded file if no session data
      const file = uploadedFiles.length > 0 ? uploadedFiles[0] : undefined;
      const sessionId = currentSessionId;

      // Generate visualization with parsed parameters
      const result = await bioMatcherApi.generateVisualization(
        file,
        parsedRequest.plotType,
        parsedRequest.xColumn || undefined,
        parsedRequest.yColumn || undefined,
        sessionId || undefined,
        !!useSessionData,
        parsedRequest.isSubplot ? JSON.stringify(parsedRequest.columns) : undefined,
        parsedRequest.isSubplot
      );

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `I've generated ${parsedRequest.isSubplot ? 'multiple' : 'a'} ${parsedRequest.plotType} visualization(s) for your data. The dataset contains ${result.data_shape[0]} rows and ${result.data_shape[1]} columns, with ${result.numeric_columns.length} numeric columns available for analysis.`,
        timestamp: new Date(),
        result: {
          type: 'visualization',
          data: {
            plotType: result.plot_type,
            plotJson: result.plot_json,
            columns: result.columns,
            dataShape: result.data_shape,
            numericColumns: result.numeric_columns,
            sessionId: result.session_id,
            workflowStep: result.workflow_step,
            isSubplot: parsedRequest.isSubplot,
            requestedColumns: parsedRequest.columns
          }
        }
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error generating visualization:', error);
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ Sorry, I couldn't generate the visualization. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
        result: null
      };
      setMessages(prev => [...prev, aiMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  // Parse visualization request to extract plot type and column names
  const parseVisualizationRequest = (prompt: string) => {
    const lowerPrompt = prompt.toLowerCase();
    
    // Extract plot type
    let plotType = "scatter";
    if (lowerPrompt.includes("correlation") || lowerPrompt.includes("heatmap")) {
      plotType = "correlation";
    } else if (lowerPrompt.includes("histogram") || lowerPrompt.includes("bar chart")) {
      plotType = "histogram";
    } else if (lowerPrompt.includes("scatter")) {
      plotType = "scatter";
    } else if (lowerPrompt.includes("boxplot") || lowerPrompt.includes("box plot")) {
      plotType = "boxplot";
    }

    // Extract column names using more precise patterns
    let columns: string[] = [];
    let isSubplot = false;

    // Pattern 1: "histogram of X and Y" or "histograms of X and Y"
    const histogramPattern = /(?:histogram|histograms|bar chart|bar charts) of ([a-zA-Z_\s]+) and ([a-zA-Z_\s]+)/gi;
    const histogramMatch = histogramPattern.exec(lowerPrompt);
    if (histogramMatch) {
      columns = [histogramMatch[1].trim(), histogramMatch[2].trim()];
    } else {
      // Pattern 2: "scatter plot of X vs Y"
      const scatterPattern = /(?:scatter|plot) of ([a-zA-Z_\s]+) vs ([a-zA-Z_\s]+)/gi;
      const scatterMatch = scatterPattern.exec(lowerPrompt);
      if (scatterMatch) {
        columns = [scatterMatch[1].trim(), scatterMatch[2].trim()];
      } else {
        // Pattern 3: "X and Y" (for any plot type)
        const andPattern = /([a-zA-Z_\s]+) and ([a-zA-Z_\s]+)/gi;
        const andMatch = andPattern.exec(lowerPrompt);
        if (andMatch) {
          columns = [andMatch[1].trim(), andMatch[2].trim()];
        } else {
          // Pattern 4: "X, Y, Z" (comma-separated)
          const commaPattern = /([a-zA-Z_\s]+),\s*([a-zA-Z_\s]+)(?:,\s*([a-zA-Z_\s]+))?/gi;
          const commaMatch = commaPattern.exec(lowerPrompt);
          if (commaMatch) {
            columns = [commaMatch[1].trim(), commaMatch[2].trim()];
            if (commaMatch[3]) {
              columns.push(commaMatch[3].trim());
            }
          } else {
            // Pattern 5: Single column - "histogram of X" or "visualize X"
            const singlePattern = /(?:histogram|bar chart|visualize|plot|show) ([a-zA-Z_\s]+)/gi;
            const singleMatch = singlePattern.exec(lowerPrompt);
            if (singleMatch) {
              columns = [singleMatch[1].trim()];
            }
          }
        }
      }
    }

    // Clean up columns - remove common words and duplicates
    const cleanColumns = columns
      .filter((col: string) => 
        col && 
        col.length > 0 && 
        !['the', 'a', 'an', 'of', 'and', 'or', 'vs', 'versus', 'level', 'levels'].includes(col)
      )
      .map((col: string) => col.replace(/\s+/g, ' ').trim());

    // Remove duplicates while preserving order
    const uniqueColumns = cleanColumns.filter((col: string, index: number) => 
      cleanColumns.indexOf(col) === index
    );

    // Determine if this should be a subplot (multiple columns)
    isSubplot = uniqueColumns.length > 1 && (plotType === "histogram" || plotType === "boxplot");

    // For scatter plots, we need exactly 2 columns
    if (plotType === "scatter" && uniqueColumns.length >= 2) {
      return {
        plotType,
        xColumn: uniqueColumns[0],
        yColumn: uniqueColumns[1],
        columns: uniqueColumns.slice(0, 2),
        isSubplot: false
      };
    }

    // For correlation, we don't need specific columns
    if (plotType === "correlation") {
      return {
        plotType,
        xColumn: null,
        yColumn: null,
        columns: [],
        isSubplot: false
      };
    }

    return {
      plotType,
      xColumn: uniqueColumns[0] || null,
      yColumn: uniqueColumns[1] || null,
      columns: uniqueColumns,
      isSubplot
    };
  };

  const handleDataQA = async (prompt: string) => {
    try {
      // Ensure we have a session ID
      let sessionId = currentSessionId;
      if (!sessionId) {
        sessionId = await createWorkflowSession();
        if (!sessionId) {
          throw new Error('Failed to create workflow session');
        }
      }

      // Call the data Q&A API
      const result = await dataQaApi.askQuestion(sessionId, prompt);

      if (result.success) {
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: result.answer || 'I analyzed your data but couldn\'t find a specific answer to your question.',
          timestamp: new Date(),
          result: {
            type: 'data-qa',
            data: {
              insights: result.insights || [],
              confidence: result.confidence || 'medium',
              suggestions: result.suggestions || [],
              data_summary: result.data_summary
            }
          }
        };

        setMessages(prev => [...prev, aiMessage]);
        
        // Show suggestions after Q&A response
        setShowSuggestions(true);
      } else {
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: result.error || 'Sorry, I couldn\'t answer your question about the data.',
          timestamp: new Date(),
          result: null
        };
        setMessages(prev => [...prev, aiMessage]);
      }
    } catch (error) {
      console.error('Error in data Q&A:', error);
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ Sorry, I couldn't answer your question. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
        result: null
      };
      setMessages(prev => [...prev, aiMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDataAnalysis = async (prompt: string) => {
    try {
      // Determine if we should use session data or uploaded file
      const useSessionData = currentSessionId;
      const hasData = currentSessionId || uploadedFiles.length > 0;
      
      if (!hasData) {
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: 'I need either uploaded files or merged data from a previous step to analyze. Please upload files or merge data first.',
          timestamp: new Date(),
          result: null
        };
        setMessages(prev => [...prev, aiMessage]);
        setIsProcessing(false);
        return;
      }

      // Use the first uploaded file if no session data
      const file = uploadedFiles.length > 0 ? uploadedFiles[0] : undefined;
      const sessionId = currentSessionId;

      // Perform data analysis
      const result = await bioMatcherApi.analyzeData(
        file,
        sessionId || undefined,
        !!useSessionData
      );

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `I've analyzed your dataset and found ${result.recommendations.length} recommendations. The dataset contains ${result.dataset_info.total_rows} rows and ${result.dataset_info.total_columns} columns. I've identified ${result.quality_analysis.total_issues} data quality issues and ${result.correlation_analysis.total_correlations || 0} strong correlations.`,
        timestamp: new Date(),
        result: {
          type: 'analysis',
          data: result
        }
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error analyzing data:', error);
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ Sorry, I couldn't analyze the data. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
        result: null
      };
      setMessages(prev => [...prev, aiMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleGeneralChat = async (prompt: string) => {
    try {
      // Call the general chat API
      const result = await generalChatApi.chat(prompt, currentSessionId || undefined);
      
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: result.response,
        timestamp: new Date(),
        result: {
          type: 'general-chat',
          data: {
            suggestions: result.suggestions,
            confidence: result.confidence,
            context: result.context
          }
        }
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error in general chat:', error);
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ Sorry, I couldn't process your request. Please try again.`,
        timestamp: new Date(),
        result: null
      };
      setMessages(prev => [...prev, aiMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDataQuery = async (prompt: string) => {
    try {
      // Ensure we have a session ID
      let sessionId = currentSessionId;
      if (!sessionId) {
        sessionId = await createWorkflowSession();
        if (!sessionId) {
          throw new Error('Failed to create workflow session');
        }
      }

      // Parse the query to extract filter conditions
      const parsedQuery = parseDataQuery(prompt);
      console.log('Parsed data query:', parsedQuery);

      // Call the query API
      const result = await bioMatcherApi.queryData(sessionId, parsedQuery.query);

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `I've filtered your data based on your query. Found ${result.filtered_shape[0]} rows (removed ${result.rows_removed} rows). The filtered dataset contains ${result.filtered_shape[1]} columns.`,
        timestamp: new Date(),
        result: {
          type: 'query',
          data: {
            query: result.query,
            originalShape: result.original_shape,
            filteredShape: result.filtered_shape,
            rowsRemoved: result.rows_removed,
            columns: result.columns,
            sampleRows: result.sample_rows,
            sessionId: result.session_id
          }
        }
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error in data query:', error);
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ Sorry, I couldn't query your data. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
        result: null
      };
      setMessages(prev => [...prev, aiMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  // Parse data query to extract filter conditions
  const parseDataQuery = (prompt: string) => {
    const lowerPrompt = prompt.toLowerCase();
    
    // Common query patterns
    const queryPatterns = [
      // "where column = value"
      /where\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:=|is)\s*["\']?([^"\']+)["\']?/gi,
      // "filter rows where column like pattern"
      /filter\s+rows?\s+where\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:like|contains)\s*["\']?([^"\']+)["\']?/gi,
      // "show rows where column > value"
      /show\s+rows?\s+where\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(>=?|<=?|>|<)\s*([0-9.]+)/gi,
      // "get rows where column in (value1, value2)"
      /get\s+rows?\s+where\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+in\s*\(([^)]+)\)/gi,
      // "query where column is not null"
      /query\s+where\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+is\s+(not\s+)?null/gi
    ];

    // Try to match patterns and construct query
    for (const pattern of queryPatterns) {
      const match = pattern.exec(lowerPrompt);
      if (match) {
        // Return the original prompt as the query (backend will parse it)
        return {
          query: prompt,
          type: 'filter'
        };
      }
    }

    // If no specific pattern found, treat as general query
    return {
      query: prompt,
      type: 'general'
    };
  };


  const handleVoiceToggle = () => {
    setIsListening(!isListening);
    // TODO: Implement voice input functionality
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

  const handleFileUpload = async (files: File[]) => {
    console.log('Files uploaded:', files);
    
    // Store uploaded files for later use
    setUploadedFiles(prev => [...prev, ...files]);
    
    try {
      // Ensure we have a session ID
      let sessionId = currentSessionId;
      if (!sessionId) {
        sessionId = await createWorkflowSession();
        if (!sessionId) {
          throw new Error('Failed to create workflow session');
        }
      }
      
      // Upload files to backend and store in session
      // Always upload files individually, let user request merge separately
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        console.log(`Uploading file ${i + 1}/${files.length}: ${file.name} (${file.size} bytes)`);
        
        // Create FormData for single file upload
        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', sessionId);
        
        // Upload file to bio-matcher API using single file endpoint
        const result = await bioMatcherApi.uploadSingleFile(formData);
        console.log(`File ${i + 1} uploaded successfully:`, result);
      }
      
      // Add success message to chat
      const successMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `✅ Successfully uploaded ${files.length} file(s)! You can now ask me to merge them or analyze the data.`,
        timestamp: new Date(),
        result: {
          type: 'file-upload-success',
          data: {
            files: files.map(f => f.name),
            sessionId: sessionId
          }
        }
      };
      
      setMessages(prev => [...prev, successMessage]);
      
    } catch (error) {
      console.error('Error uploading files:', error);
      
      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ Sorry, I couldn't upload the files. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
        result: null
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    handlePromptSubmit(suggestion);
  };

  // Files Modal Handlers
  const handleFilesClick = () => {
    setShowFilesModal(true);
    onFilesClick?.();
  };

  const handleFilesModalClose = () => {
    setShowFilesModal(false);
  };

  const handleFileSelect = (file: any) => {
    // Add a message about the selected file
    const aiMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      type: 'ai',
      content: `I've selected the file "${file.name}". What would you like me to do with it?`,
      timestamp: new Date(),
      result: {
        type: 'file-selected',
        data: file
      }
    };
    setMessages(prev => [...prev, aiMessage]);
    setShowFilesModal(false);
  };

  const handleFileDelete = (fileId: string) => {
    // Remove file from uploaded files
    setUploadedFiles(prev => prev.filter(f => f.name !== fileId));
    
    // Add a message about the deleted file
    const aiMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      type: 'ai',
      content: `I've deleted the file. It's been removed from your workspace.`,
      timestamp: new Date(),
      result: null
    };
    setMessages(prev => [...prev, aiMessage]);
  };

  const handleFileDownload = (file: any) => {
    // Create a download link for the file
    const blob = new Blob(['File content'], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = file.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Mock files data for the modal
  const getMockFiles = (): any[] => {
    const mockFiles = [
      {
        id: '1',
        name: 'sales_data.csv',
        type: 'csv' as const,
        size: '2.3 MB',
        uploadedAt: new Date(Date.now() - 86400000), // 1 day ago
        lastModified: new Date(Date.now() - 3600000), // 1 hour ago
        status: 'processed' as const,
        path: '/uploads/sales_data.csv',
        description: 'Q1 2024 sales data with customer information'
      },
      {
        id: '2',
        name: 'customer_analytics.json',
        type: 'json' as const,
        size: '1.8 MB',
        uploadedAt: new Date(Date.now() - 172800000), // 2 days ago
        lastModified: new Date(Date.now() - 7200000), // 2 hours ago
        status: 'processing' as const,
        path: '/uploads/customer_analytics.json',
        description: 'Customer behavior analytics and insights'
      },
      {
        id: '3',
        name: 'inventory_report.xlsx',
        type: 'xlsx' as const,
        size: '4.1 MB',
        uploadedAt: new Date(Date.now() - 259200000), // 3 days ago
        lastModified: new Date(Date.now() - 10800000), // 3 hours ago
        status: 'processed' as const,
        path: '/uploads/inventory_report.xlsx',
        description: 'Current inventory levels and stock movements'
      },
      {
        id: '4',
        name: 'merged_dataset.csv',
        type: 'csv' as const,
        size: '5.7 MB',
        uploadedAt: new Date(Date.now() - 43200000), // 12 hours ago
        lastModified: new Date(Date.now() - 1800000), // 30 minutes ago
        status: 'processed' as const,
        path: '/uploads/merged_dataset.csv',
        description: 'Merged customer and sales data'
      },
      {
        id: '5',
        name: 'website_analytics.csv',
        type: 'csv' as const,
        size: '3.2 MB',
        uploadedAt: new Date(Date.now() - 86400000), // 1 day ago
        lastModified: new Date(Date.now() - 5400000), // 1.5 hours ago
        status: 'error' as const,
        path: '/uploads/website_analytics.csv',
        description: 'Website traffic and user behavior data'
      }
    ];

    // Add uploaded files to the list
    const uploadedFileItems = uploadedFiles.map((file, index) => ({
      id: `uploaded-${index}`,
      name: file.name,
      type: file.name.endsWith('.csv') ? 'csv' : file.name.endsWith('.json') ? 'json' : 'txt' as const,
      size: `${(file.size / 1024 / 1024).toFixed(1)} MB`,
      uploadedAt: new Date(),
      lastModified: new Date(),
      status: 'processed' as const,
      path: `/uploads/${file.name}`,
      description: `Uploaded file: ${file.name}`
    }));

    return [...mockFiles, ...uploadedFileItems];
  };

  const handleClearSession = async () => {
    if (!currentSessionId) {
      return;
    }

    try {
      await bioMatcherApi.clearWorkflowSession(currentSessionId);
      
      // Clear local state
      setUploadedFiles([]);
      setCurrentSessionId(null);
      setGeneratedFiles([]);
      
      // Add success message to chat
      const successMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: '✅ Session data cleared successfully! You can now upload new files.',
        timestamp: new Date(),
        result: {
          type: 'session-cleared',
          data: { sessionId: currentSessionId }
        }
      };
      
      setMessages(prev => [...prev, successMessage]);
    } catch (error) {
      console.error('Error clearing session:', error);
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `❌ Sorry, I couldn't clear the session. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
        result: null
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  return (
    <main className="ai-chat-main">
      <div className="chat-container">
        <ChatHistory messages={messages} isProcessing={isProcessing} />
        
        {showSuggestions && currentSessionId && (
          <DataQASuggestions
            sessionId={currentSessionId}
            onSuggestionClick={handleSuggestionClick}
            visible={showSuggestions}
          />
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <div className="prompt-section">
        <PromptBox 
          onSubmit={handlePromptSubmit}
          onVoiceToggle={handleVoiceToggle}
          isListening={isListening}
          isProcessing={isProcessing}
          onFileUpload={handleFileUpload}
          generatedFiles={generatedFiles}
        />
      </div>

      <WorkflowCreationForm
        isOpen={showWorkflowForm}
        onClose={handleWorkflowFormClose}
        onWorkflowCreated={handleWorkflowCreated}
        initialData={workflowFormData}
      />

      {/* Files Modal */}
      <FilesModal
        isOpen={showFilesModal}
        onClose={handleFilesModalClose}
        files={getMockFiles()}
        onFileSelect={handleFileSelect}
        onFileDelete={handleFileDelete}
        onFileDownload={handleFileDownload}
      />
    </main>
  );
};

export default AIChatMain; 