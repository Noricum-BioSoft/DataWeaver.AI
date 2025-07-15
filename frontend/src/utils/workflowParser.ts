export interface ParsedWorkflowCommand {
  action: 'create' | 'update' | 'delete' | 'list' | 'view';
  workflowName?: string;
  description?: string;
  status?: string;
  steps?: string[];
  metadata?: Record<string, any>;
}

export function parseWorkflowCommand(command: string): ParsedWorkflowCommand {
  const lowerCommand = command.toLowerCase().trim();
  
  // Initialize result
  const result: ParsedWorkflowCommand = {
    action: 'create',
    metadata: {}
  };

  // Check for different actions
  if (lowerCommand.includes('create') || lowerCommand.includes('new') || lowerCommand.includes('add')) {
    result.action = 'create';
  } else if (lowerCommand.includes('update') || lowerCommand.includes('edit') || lowerCommand.includes('modify')) {
    result.action = 'update';
  } else if (lowerCommand.includes('delete') || lowerCommand.includes('remove')) {
    result.action = 'delete';
  } else if (lowerCommand.includes('list') || lowerCommand.includes('show') || lowerCommand.includes('view')) {
    result.action = 'list';
  }

  // Extract workflow name
  const namePatterns = [
    /(?:called|named|titled)\s+["']?([^"']+)["']?/i,
    /(?:create|new|add)\s+(?:a\s+)?(?:workflow|pipeline)\s+(?:called\s+)?["']?([^"']+)["']?/i,
    /workflow\s+["']?([^"']+)["']?/i
  ];

  for (const pattern of namePatterns) {
    const match = command.match(pattern);
    if (match && match[1]) {
      result.workflowName = match[1].trim();
      break;
    }
  }

  // Extract description
  const descPatterns = [
    /(?:for|that|which)\s+(.+?)(?:\s+with|\s+using|\s+to|$)/i,
    /description[:\s]+(.+?)(?:\s+with|\s+using|\s+to|$)/i
  ];

  for (const pattern of descPatterns) {
    const match = command.match(pattern);
    if (match && match[1] && !result.workflowName?.includes(match[1])) {
      result.description = match[1].trim();
      break;
    }
  }

  // Extract status
  if (lowerCommand.includes('draft')) {
    result.status = 'draft';
  } else if (lowerCommand.includes('ready') || lowerCommand.includes('active')) {
    result.status = 'ready';
  } else if (lowerCommand.includes('running')) {
    result.status = 'running';
  }

  // Extract steps
  const stepPatterns = [
    /steps?[:\s]+(.+?)(?:\s+with|\s+using|\s+to|$)/i,
    /pipeline\s+with\s+(.+?)(?:\s+with|\s+using|\s+to|$)/i
  ];

  for (const pattern of stepPatterns) {
    const match = command.match(pattern);
    if (match && match[1]) {
      const stepsText = match[1].trim();
      result.steps = stepsText.split(/[,;]|\sand\s/).map(s => s.trim()).filter(s => s.length > 0);
      break;
    }
  }

  // Extract metadata
  if (lowerCommand.includes('high priority') || lowerCommand.includes('urgent')) {
    result.metadata!.priority = 'high';
  } else if (lowerCommand.includes('low priority')) {
    result.metadata!.priority = 'low';
  } else {
    result.metadata!.priority = 'medium';
  }

  if (lowerCommand.includes('timeout')) {
    const timeoutMatch = command.match(/timeout\s+(\d+)/i);
    if (timeoutMatch) {
      result.metadata!.timeout = parseInt(timeoutMatch[1]);
    }
  }

  // Extract tags
  const tagMatch = command.match(/tags?[:\s]+(.+?)(?:\s+with|\s+using|\s+to|$)/i);
  if (tagMatch) {
    result.metadata!.tags = tagMatch[1].trim();
  }

  return result;
}

export function extractWorkflowNameFromCommand(command: string): string | null {
  const parsed = parseWorkflowCommand(command);
  return parsed.workflowName || null;
}

export function isWorkflowCreationCommand(command: string): boolean {
  const lowerCommand = command.toLowerCase();
  
  // Check for visualization keywords first - if present, it's not a workflow command
  if (lowerCommand.includes('plot') || 
      lowerCommand.includes('visualize') || 
      lowerCommand.includes('chart') || 
      lowerCommand.includes('graph') || 
      lowerCommand.includes('scatter') || 
      lowerCommand.includes('histogram') || 
      lowerCommand.includes('correlation') ||
      lowerCommand.includes('merge') ||
      lowerCommand.includes('combine')) {
    return false;
  }
  
  // Only trigger on specific workflow creation patterns
  return (lowerCommand.includes('create') && lowerCommand.includes('workflow')) || 
         (lowerCommand.includes('new') && lowerCommand.includes('workflow')) || 
         (lowerCommand.includes('add') && lowerCommand.includes('workflow')) ||
         (lowerCommand.includes('workflow') && lowerCommand.includes('called')) ||
         (lowerCommand.includes('create') && lowerCommand.includes('pipeline')) ||
         (lowerCommand.includes('new') && lowerCommand.includes('pipeline'));
} 