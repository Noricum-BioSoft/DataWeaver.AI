import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Play, Pause, CheckCircle, XCircle } from 'lucide-react';
import { workflowApi } from '../services/api';
import { Workflow, WorkflowStatus } from '../types';

interface WorkflowListProps {
  onWorkflowSelect?: (workflow: Workflow) => void;
  onWorkflowEdit?: (workflow: Workflow) => void;
}

const WorkflowList: React.FC<WorkflowListProps> = ({
  onWorkflowSelect,
  onWorkflowEdit,
}) => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    try {
      setLoading(true);
      const data = await workflowApi.getWorkflows();
      setWorkflows(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load workflows');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteWorkflow = async (workflowId: number) => {
    if (window.confirm('Are you sure you want to delete this workflow?')) {
      try {
        await workflowApi.deleteWorkflow(workflowId);
        setWorkflows(workflows.filter(w => w.id !== workflowId));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete workflow');
      }
    }
  };

  const getStatusIcon = (status: WorkflowStatus) => {
    switch (status) {
      case WorkflowStatus.COMPLETED:
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case WorkflowStatus.FAILED:
        return <XCircle className="h-4 w-4 text-red-500" />;
      case WorkflowStatus.RUNNING:
        return <Play className="h-4 w-4 text-blue-500" />;
      case WorkflowStatus.CANCELLED:
        return <Pause className="h-4 w-4 text-yellow-500" />;
      default:
        return <div className="h-4 w-4 rounded-full bg-gray-300" />;
    }
  };

  const getStatusColor = (status: WorkflowStatus) => {
    switch (status) {
      case WorkflowStatus.COMPLETED:
        return 'bg-green-100 text-green-800';
      case WorkflowStatus.FAILED:
        return 'bg-red-100 text-red-800';
      case WorkflowStatus.RUNNING:
        return 'bg-blue-100 text-blue-800';
      case WorkflowStatus.CANCELLED:
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={loadWorkflows}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Workflows</h2>
        <button className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          <Plus className="h-4 w-4 mr-2" />
          New Workflow
        </button>
      </div>

      {/* Workflow List */}
      {workflows.length === 0 ? (
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400 mb-4">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No workflows yet</h3>
          <p className="text-gray-500 mb-4">Create your first workflow to get started</p>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Create Workflow
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {workflows.map((workflow) => (
            <div
              key={workflow.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => onWorkflowSelect?.(workflow)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(workflow.status)}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{workflow.name}</h3>
                    {workflow.description && (
                      <p className="text-sm text-gray-500 mt-1">{workflow.description}</p>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(
                      workflow.status
                    )}`}
                  >
                    {workflow.status}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between mt-4">
                <div className="text-sm text-gray-500">
                  Created {formatDate(workflow.created_at)}
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onWorkflowEdit?.(workflow);
                    }}
                    className="p-1 text-gray-400 hover:text-gray-600"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteWorkflow(workflow.id);
                    }}
                    className="p-1 text-gray-400 hover:text-red-600"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default WorkflowList; 