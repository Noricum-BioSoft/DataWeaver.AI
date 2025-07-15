import React, { useState, useEffect } from 'react';
import { X, Save, Plus, Settings, FileText } from 'lucide-react';
import { workflowApi } from '../services/api';
import { WorkflowCreate, WorkflowStatus, StepType } from '../types';
import './WorkflowCreationForm.css';

interface WorkflowCreationFormProps {
  isOpen: boolean;
  onClose: () => void;
  onWorkflowCreated: (workflow: any) => void;
  initialData?: {
    name?: string;
    description?: string;
    status?: WorkflowStatus;
  };
}

interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  stepType: StepType;
  orderIndex: number;
  externalProvider?: string;
  externalConfig?: Record<string, any>;
}

const WorkflowCreationForm: React.FC<WorkflowCreationFormProps> = ({
  isOpen,
  onClose,
  onWorkflowCreated,
  initialData = {}
}) => {
  const [formData, setFormData] = useState<WorkflowCreate>({
    name: initialData.name || '',
    description: initialData.description || '',
    metadata: {}
  });

  const [steps, setSteps] = useState<WorkflowStep[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'basic' | 'steps' | 'advanced'>('basic');

  useEffect(() => {
    if (isOpen) {
      setFormData({
        name: initialData.name || '',
        description: initialData.description || '',
        metadata: {}
      });
      setSteps([]);
      setError(null);
      setActiveTab('basic');
    }
  }, [isOpen, initialData]);

  const handleInputChange = (field: keyof WorkflowCreate, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleMetadataChange = (key: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      metadata: {
        ...prev.metadata,
        [key]: value
      }
    }));
  };

  const addStep = () => {
    const newStep: WorkflowStep = {
      id: `step-${Date.now()}`,
      name: '',
      description: '',
      stepType: StepType.INPUT,
      orderIndex: steps.length
    };
    setSteps(prev => [...prev, newStep]);
  };

  const updateStep = (id: string, field: keyof WorkflowStep, value: any) => {
    setSteps(prev => prev.map(step => 
      step.id === id ? { ...step, [field]: value } : step
    ));
  };

  const removeStep = (id: string) => {
    setSteps(prev => prev.filter(step => step.id !== id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('Workflow name is required');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Create the workflow
      const workflow = await workflowApi.createWorkflow(formData);
      
      // Create workflow steps if any
      if (steps.length > 0) {
        for (const step of steps) {
          if (step.name.trim()) {
            await workflowApi.createWorkflowStep(workflow.id, {
              name: step.name,
              description: step.description,
              step_type: step.stepType,
              order_index: step.orderIndex,
              external_provider: step.externalProvider,
              external_config: step.externalConfig
            });
          }
        }
      }

      onWorkflowCreated(workflow);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create workflow');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="workflow-creation-modal-overlay">
      <div className="workflow-creation-modal">
        <div className="modal-header">
          <h2 className="modal-title">Create New Workflow</h2>
          <button className="close-button" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-tabs">
          <button
            className={`tab-button ${activeTab === 'basic' ? 'active' : ''}`}
            onClick={() => setActiveTab('basic')}
          >
            <FileText size={16} />
            Basic Info
          </button>
          <button
            className={`tab-button ${activeTab === 'steps' ? 'active' : ''}`}
            onClick={() => setActiveTab('steps')}
          >
            <Plus size={16} />
            Workflow Steps
          </button>
          <button
            className={`tab-button ${activeTab === 'advanced' ? 'active' : ''}`}
            onClick={() => setActiveTab('advanced')}
          >
            <Settings size={16} />
            Advanced
          </button>
        </div>

        <form onSubmit={handleSubmit} className="workflow-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {activeTab === 'basic' && (
            <div className="form-section">
              <div className="form-group">
                <label htmlFor="workflow-name">Workflow Name *</label>
                <input
                  id="workflow-name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="Enter workflow name"
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="workflow-description">Description</label>
                <textarea
                  id="workflow-description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Describe what this workflow does..."
                  className="form-textarea"
                  rows={4}
                />
              </div>

              <div className="form-group">
                <label htmlFor="workflow-status">Initial Status</label>
                <select
                  id="workflow-status"
                  value={formData.metadata?.status || WorkflowStatus.DRAFT}
                  onChange={(e) => handleMetadataChange('status', e.target.value)}
                  className="form-select"
                >
                  <option value={WorkflowStatus.DRAFT}>Draft</option>
                  <option value={WorkflowStatus.RUNNING}>Running</option>
                  <option value={WorkflowStatus.COMPLETED}>Completed</option>
                  <option value={WorkflowStatus.FAILED}>Failed</option>
                  <option value={WorkflowStatus.CANCELLED}>Cancelled</option>
                </select>
              </div>
            </div>
          )}

          {activeTab === 'steps' && (
            <div className="form-section">
              <div className="steps-header">
                <h3>Workflow Steps</h3>
                <button
                  type="button"
                  onClick={addStep}
                  className="add-step-button"
                >
                  <Plus size={16} />
                  Add Step
                </button>
              </div>

              {steps.length === 0 ? (
                <div className="empty-steps">
                  <p>No steps added yet. Click "Add Step" to get started.</p>
                </div>
              ) : (
                <div className="steps-list">
                  {steps.map((step, index) => (
                    <div key={step.id} className="step-item">
                      <div className="step-header">
                        <span className="step-number">{index + 1}</span>
                        <button
                          type="button"
                          onClick={() => removeStep(step.id)}
                          className="remove-step-button"
                        >
                          <X size={16} />
                        </button>
                      </div>

                      <div className="step-fields">
                        <div className="form-group">
                          <label>Step Name</label>
                          <input
                            type="text"
                            value={step.name}
                            onChange={(e) => updateStep(step.id, 'name', e.target.value)}
                            placeholder="Enter step name"
                            className="form-input"
                          />
                        </div>

                        <div className="form-group">
                          <label>Description</label>
                          <input
                            type="text"
                            value={step.description}
                            onChange={(e) => updateStep(step.id, 'description', e.target.value)}
                            placeholder="Describe this step"
                            className="form-input"
                          />
                        </div>

                        <div className="form-group">
                          <label>Step Type</label>
                          <select
                            value={step.stepType}
                            onChange={(e) => updateStep(step.id, 'stepType', e.target.value)}
                            className="form-select"
                          >
                            <option value={StepType.INPUT}>Input</option>
                            <option value={StepType.PROCESSING}>Processing</option>
                            <option value={StepType.OUTPUT}>Output</option>
                            <option value={StepType.EXTERNAL}>External</option>
                          </select>
                        </div>

                        {step.stepType === StepType.EXTERNAL && (
                          <div className="form-group">
                            <label>External Provider</label>
                            <input
                              type="text"
                              value={step.externalProvider || ''}
                              onChange={(e) => updateStep(step.id, 'externalProvider', e.target.value)}
                              placeholder="e.g., bioinformatics_tool"
                              className="form-input"
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'advanced' && (
            <div className="form-section">
              <div className="form-group">
                <label htmlFor="workflow-tags">Tags</label>
                <input
                  id="workflow-tags"
                  type="text"
                  value={formData.metadata?.tags || ''}
                  onChange={(e) => handleMetadataChange('tags', e.target.value)}
                  placeholder="Enter tags separated by commas"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="workflow-priority">Priority</label>
                <select
                  id="workflow-priority"
                  value={formData.metadata?.priority || 'medium'}
                  onChange={(e) => handleMetadataChange('priority', e.target.value)}
                  className="form-select"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="workflow-timeout">Timeout (minutes)</label>
                <input
                  id="workflow-timeout"
                  type="number"
                  value={formData.metadata?.timeout || 30}
                  onChange={(e) => handleMetadataChange('timeout', parseInt(e.target.value))}
                  min="1"
                  max="1440"
                  className="form-input"
                />
              </div>
            </div>
          )}

          <div className="modal-actions">
            <button
              type="button"
              onClick={onClose}
              className="cancel-button"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="create-button"
              disabled={isSubmitting || !formData.name.trim()}
            >
              {isSubmitting ? (
                <>
                  <div className="spinner"></div>
                  Creating...
                </>
              ) : (
                <>
                  <Save size={16} />
                  Create Workflow
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default WorkflowCreationForm; 