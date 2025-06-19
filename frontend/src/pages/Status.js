import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { apiService } from '../config/api';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  RefreshCw, 
  FileText, 
  BarChart3, 
  Star,
  Download,
  MessageSquare,
  GitBranch,
  Eye,
  Workflow,
  Languages
} from 'lucide-react';

const Status = () => {
  const { workflowId } = useParams();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState({
    rating: 5,
    usefulness_score: 5,
    accuracy_score: 5,
    completeness_score: 5,
    comments: ''
  });
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [currentAgentIndex, setCurrentAgentIndex] = useState(0);
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);

  // Orchestrator-driven architecture: Orchestrator manages all other agents
  const orchestrator = useMemo(() => ({
    icon: Workflow,
    name: 'Content Orchestrator',
    description: 'Manages the complete documentation generation workflow',
    color: 'from-indigo-500 to-indigo-600',
  }), []);

  const delegatedAgents = useMemo(() => [
    {
      icon: GitBranch,
      name: 'Code Analyzer',
      description: 'Analyzes repository structure, extracts functions, classes, and dependencies',
      color: 'from-blue-500 to-blue-600',
      phase: 1
    },
    {
      icon: FileText,
      name: 'Documentation Writer',
      description: 'Generates comprehensive documentation using AI in multiple formats',
      color: 'from-green-500 to-green-600',
      phase: 2
    },
    {
      icon: BarChart3,
      name: 'Diagram Generator',
      description: 'Creates architectural and flow diagrams using Mermaid',
      color: 'from-purple-500 to-purple-600',
      phase: 3
    },
    {
      icon: Languages,
      name: 'Translation Agent',
      description: 'Translates documentation to multiple languages for global accessibility',
      color: 'from-teal-500 to-teal-600',
      phase: 4
    },
    {
      icon: Eye,
      name: 'Quality Reviewer',
      description: 'Assesses documentation quality and provides improvement suggestions',
      color: 'from-orange-500 to-orange-600',
      phase: 5
    },
    {
      icon: MessageSquare,
      name: 'User Feedback',
      description: 'Collects and analyzes user feedback for continuous improvement',
      color: 'from-pink-500 to-pink-600',
      phase: 6
    },
  ], []);

  const fetchStatus = useCallback(async () => {
    try {
      const response = await apiService.getWorkflowStatus(workflowId);
      if (response.data.success) {
        setStatus(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching status:', error);
      toast.error('Failed to fetch status');
    } finally {
      setLoading(false);
    }
  }, [workflowId]);

  useEffect(() => {
    let interval;
    
    if (status?.status === 'processing') {
      // More frequent polling during processing for better real-time updates
      interval = setInterval(fetchStatus, 1000); // Poll every 1 second during processing
    } else if (status?.status === 'initiated') {
      interval = setInterval(fetchStatus, 2000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [fetchStatus, status?.status, workflowId]);

  // Initial fetch when component mounts
  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // Close download menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showDownloadMenu && !event.target.closest('.download-menu-container')) {
        setShowDownloadMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showDownloadMenu]);

  // Update agent status based on orchestrator-driven architecture
  useEffect(() => {
    if (status?.status === 'processing' && status?.agents) {
      // Find currently active agent
      const activeAgentKey = status.current_agent;
      if (activeAgentKey) {
        // Map backend agent keys to delegated agent phases
        // Orchestrator is always active, but delegates to specific agents
        const agentPhaseMapping = {
          'code_analyzer': 1,        // Phase 1: Repository Analysis  
          'doc_writer': 2,           // Phase 2: Documentation Generation
          'diagram_generator': 3,    // Phase 3: Diagram Creation
          'translation_agent': 4,    // Phase 4: Translation
          'quality_reviewer': 5,     // Phase 5: Quality Review
          'feedback_collector': 6,   // Phase 6: Feedback Collection
          'orchestrator': 0          // Orchestrator manages all phases
        };
        
        const currentPhase = agentPhaseMapping[activeAgentKey];
        if (currentPhase !== undefined) {
          setCurrentAgentIndex(currentPhase);
          // Only log in development mode
          if (process.env.NODE_ENV === 'development') {
            if (currentPhase === 0) {
              console.log(`🎼 Orchestrator is coordinating the workflow`);
            } else {
              console.log(`🎼 Orchestrator → Delegating to ${delegatedAgents[currentPhase - 1]?.name} (Phase ${currentPhase}/6)`);
            }
          }
        }
      }
    }
  }, [status?.status, status?.current_agent, status?.agents, delegatedAgents]);

  const submitFeedback = async () => {
    try {
      const response = await apiService.submitFeedback({
        workflow_id: workflowId,
        ...feedback
      });
      
      if (response.data.success) {
        toast.success('Feedback submitted successfully!');
        setFeedbackSubmitted(true);
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      toast.error('Failed to submit feedback');
    }
  };

  const stopWorkflow = async () => {
    try {
      const response = await apiService.stopWorkflow(workflowId);
      if (response.data.success) {
        toast.success('Workflow stopped successfully');
        fetchStatus(); // Refresh status
      }
    } catch (error) {
      console.error('Error stopping workflow:', error);
      toast.error('Failed to stop workflow');
    }
  };

  const downloadFile = async (format) => {
    try {
      setShowDownloadMenu(false);
      const response = await fetch(`${apiService.baseURL}/download/${workflowId}?format=${format}`);
      
      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      
      // Get filename from Content-Disposition header or create default
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `documentation.${format}`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success(`Downloaded ${filename}`);
    } catch (error) {
      console.error('Error downloading file:', error);
      toast.error(`Failed to download ${format} file`);
    }
  };

  const getStatusInfo = (status) => {
    switch (status) {
      case 'initiated':
        return {
          icon: Clock,
          color: 'text-blue-600 bg-blue-100',
          message: 'Documentation generation has been initiated',
          progress: 10
        };
      case 'processing':
        return {
          icon: RefreshCw,
          color: 'text-yellow-600 bg-yellow-100',
          message: 'Agents are analyzing your repository',
          progress: 50
        };
      case 'completed':
        return {
          icon: CheckCircle,
          color: 'text-green-600 bg-green-100',
          message: 'Documentation generation completed successfully',
          progress: 100
        };
      case 'failed':
        return {
          icon: XCircle,
          color: 'text-red-600 bg-red-100',
          message: 'Documentation generation failed',
          progress: 0
        };
      default:
        return {
          icon: Clock,
          color: 'text-gray-600 bg-gray-100',
          message: 'Status unknown',
          progress: 0
        };
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
          <RefreshCw className="h-12 w-12 text-blue-600 mx-auto mb-4 animate-spin" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Loading Status...</h2>
          <p className="text-gray-600">Fetching the latest information about your documentation generation</p>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
          <XCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Workflow Not Found</h2>
          <p className="text-gray-600 mb-6">The requested workflow could not be found.</p>
          <Link to="/generate" className="btn-primary">
            Generate New Documentation
          </Link>
        </div>
      </div>
    );
  }

  const statusInfo = getStatusInfo(status.status);
  const StatusIcon = statusInfo.icon;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Documentation Status
        </h1>
        <p className="text-lg text-gray-600">
          Workflow ID: <span className="font-mono text-primary-600">{workflowId}</span>
        </p>
      </div>

      {/* Status Card */}
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <div className={`p-3 rounded-full ${statusInfo.color}`}>
              <StatusIcon className={`h-6 w-6 ${statusInfo.icon === RefreshCw ? 'animate-spin' : ''}`} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {status.status.charAt(0).toUpperCase() + status.status.slice(1)}
              </h2>
              <p className="text-gray-600">{statusInfo.message}</p>
            </div>
          </div>
          <button
            onClick={fetchStatus}
            className="btn-secondary"
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Progress</span>
            <span className="text-sm text-gray-500">{statusInfo.progress}%</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${statusInfo.progress}%` }}
            />
          </div>
        </div>

        {/* Status Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Details</h3>
            <dl className="space-y-2">
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Created:</dt>
                <dd className="text-sm font-medium text-gray-900">
                  {new Date(status.created_at).toLocaleString()}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Status:</dt>
                <dd className={`text-sm font-medium status-badge status-${status.status}`}>
                  {status.status}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Progress:</dt>
                <dd className="text-sm font-medium text-gray-900">{status.progress}%</dd>
              </div>
              {status.completed_at && (
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-600">Completed:</dt>
                  <dd className="text-sm font-medium text-gray-900">
                    {new Date(status.completed_at).toLocaleString()}
                  </dd>
                </div>
              )}
            </dl>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Message</h3>
            <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
              {status.message}
            </p>
          </div>
        </div>
      </div>

      {/* Orchestrator-Driven Workflow Visualization */}
      {status.status === 'processing' && (
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-semibold text-gray-900 flex items-center">
              <RefreshCw className="h-5 w-5 text-blue-600 mr-2 animate-spin" />
              Orchestrator-Driven Workflow
            </h3>
            <button
              onClick={stopWorkflow}
              className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center space-x-2"
            >
              <XCircle className="h-4 w-4" />
              <span>Stop Workflow</span>
            </button>
          </div>

          {/* Orchestrator (Always Active) */}
          <div className="mb-8 p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border-2 border-indigo-300 shadow-lg">
            <div className="flex items-center space-x-4">
              <div className={`p-3 rounded-lg bg-gradient-to-r ${orchestrator.color} animate-pulse shadow-lg`}>
                {React.createElement(orchestrator.icon, { className: "h-6 w-6 text-white animate-spin" })}
              </div>
              <div className="flex-1">
                <h4 className="text-xl font-bold text-indigo-900 flex items-center">
                  🎼 {orchestrator.name}
                  <span className="ml-3 text-sm bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full font-bold animate-pulse">
                    ACTIVE
                  </span>
                </h4>
                <p className="text-sm text-indigo-700 mt-1">{orchestrator.description}</p>
                <div className="text-xs text-indigo-600 mt-2 font-medium">
                  Currently coordinating: {status?.current_agent ? `${status.current_agent.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}` : 'Workflow initialization'}
                </div>
              </div>
              <div className="flex space-x-1">
                <div className="w-3 h-3 bg-indigo-400 rounded-full animate-ping"></div>
                <div className="w-3 h-3 bg-indigo-400 rounded-full animate-ping" style={{animationDelay: '0.3s'}}></div>
                <div className="w-3 h-3 bg-indigo-400 rounded-full animate-ping" style={{animationDelay: '0.6s'}}></div>
              </div>
            </div>
          </div>

          {/* Delegated Agents */}
          <div className="mb-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <span className="text-indigo-600 mr-2">🎯</span>
              Delegated Agents (Coordinated by Orchestrator)
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {delegatedAgents.map((agent, index) => {
                // Map agent names to backend agent IDs
                const agentBackendMap = {
                  'Code Analyzer': 'code_analyzer',
                  'Documentation Writer': 'doc_writer', 
                  'Diagram Generator': 'diagram_generator',
                  'Translation Agent': 'translation_agent',
                  'Quality Reviewer': 'quality_reviewer',
                  'User Feedback': 'feedback_collector'
                };
                
                const backendAgentId = agentBackendMap[agent.name];
                const backendAgent = status?.agents?.[backendAgentId];
                
                // Simplified logic: Show agent status based on backend data and orchestrator context
                const isActive = backendAgent?.status === 'active';
                const isCompleted = backendAgent?.status === 'completed';
                const isWaiting = !isActive && !isCompleted && status?.status === 'processing';
                
                return (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border-2 transition-all duration-300 ${
                      isActive 
                        ? 'border-yellow-400 bg-gradient-to-r from-yellow-50 to-orange-50 shadow-lg transform scale-105' 
                        : isCompleted 
                          ? 'border-green-400 bg-green-50' 
                          : isWaiting
                            ? 'border-blue-300 bg-blue-50'
                            : 'border-gray-200 bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-bold text-gray-600 bg-gray-200 px-2 py-1 rounded-full">
                          Phase {agent.phase}
                        </span>
                        <div className={`p-2 rounded-lg ${
                          isActive 
                            ? `bg-gradient-to-r ${agent.color} animate-pulse` 
                            : isCompleted 
                              ? 'bg-green-500' 
                              : isWaiting
                                ? 'bg-blue-400'
                                : 'bg-gray-400'
                        }`}>
                          {React.createElement(agent.icon, { 
                            className: `h-4 w-4 text-white ${isActive ? 'animate-spin' : ''}` 
                          })}
                        </div>
                      </div>
                      <div className="flex-1">
                        <h5 className={`font-semibold text-sm ${
                          isActive ? 'text-orange-900' : isCompleted ? 'text-green-900' : isWaiting ? 'text-blue-900' : 'text-gray-700'
                        }`}>
                          {agent.name}
                          {isActive && (
                            <span className="ml-2 text-xs bg-yellow-400 text-yellow-900 px-2 py-1 rounded-full font-bold animate-pulse">
                              ACTIVE
                            </span>
                          )}
                          {isCompleted && (
                            <span className="ml-2 text-xs bg-green-400 text-green-900 px-2 py-1 rounded-full font-bold">
                              ✅ DONE
                            </span>
                          )}
                          {isWaiting && (
                            <span className="ml-2 text-xs bg-blue-400 text-blue-900 px-2 py-1 rounded-full font-bold">
                              ⏳ WAITING
                            </span>
                          )}
                        </h5>
                        <p className="text-xs text-gray-600 mt-1">
                          {backendAgent?.current_task || agent.description}
                        </p>
                        
                        {/* Real-time status info */}
                        {isActive && backendAgent && (
                          <div className="text-xs text-orange-600 mt-1 font-medium">
                            Progress: {backendAgent.progress || 0}%
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {/* Progress bar for active agent */}
                    {isActive && (
                      <div className="mt-3">
                        <div className="w-full bg-gray-200 rounded-full h-1.5">
                          <div 
                            className="bg-gradient-to-r from-yellow-400 to-orange-500 h-1.5 rounded-full transition-all duration-500" 
                            style={{width: `${backendAgent?.progress || 100}%`}}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
          
          {/* Current Delegation Status */}
          {status?.status === 'processing' && status?.agents?.orchestrator?.status === 'active' && (
            <div className="p-4 bg-gradient-to-r from-indigo-50 to-yellow-50 rounded-lg border border-indigo-200">
              <div className="flex items-center space-x-3">
                <div className="text-2xl">🎼</div>
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 text-sm">
                    {(() => {
                      // Find which agent is currently active
                      const activeAgent = Object.entries(status.agents || {}).find(([key, agent]) => 
                        agent.status === 'active' && key !== 'orchestrator'
                      );
                      
                      if (activeAgent) {
                        const [agentKey] = activeAgent;
                        return `Orchestrator → Delegating to: ${agentKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}`;
                      }
                      return 'Orchestrator → Coordinating workflow';
                    })()}
                  </h4>
                  <p className="text-xs text-gray-600 mt-1">
                    {(() => {
                      const activeAgent = Object.entries(status.agents || {}).find(([key, agent]) => 
                        agent.status === 'active' && key !== 'orchestrator'
                      );
                      if (activeAgent) {
                        const [, agentData] = activeAgent;
                        return agentData.current_task || 'Processing...';
                      }
                      return status.message || 'Orchestrating workflow phases';
                    })()}
                  </p>
                  {status?.message && (
                    <p className="text-xs text-indigo-600 mt-1 font-medium">
                      {status.message}
                    </p>
                  )}
                </div>
                <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                  Workflow ID: {status.workflow_id?.slice(0, 8)}...
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      {status.status === 'completed' && (
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
            Documentation Ready!
          </h3>
          <p className="text-gray-600 mb-6">
            Your documentation has been generated successfully. You can now view and download it.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              to={`/documentation/${workflowId}`}
              className="btn-primary"
            >
              <FileText className="h-4 w-4 mr-2" />
              View Documentation
            </Link>
            <div className="relative download-menu-container">
              <button 
                onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                className="btn-outline"
              >
                <Download className="h-4 w-4 mr-2" />
                Download Files
              </button>
              {showDownloadMenu && (
                <div className="absolute top-full left-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                  <div className="py-1">
                    <button
                      onClick={() => downloadFile('markdown')}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      📄 Download Markdown (.md)
                    </button>
                    <button
                      onClick={() => downloadFile('html')}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      🌐 Download HTML (.html)
                    </button>
                    <button
                      onClick={() => downloadFile('json')}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      📊 Download JSON (.json)
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Feedback Section */}
      {status.status === 'completed' && !feedbackSubmitted && (
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <MessageSquare className="h-5 w-5 text-blue-600 mr-2" />
            Share Your Feedback
          </h3>
          <p className="text-gray-600 mb-6">
            Help us improve by sharing your experience with the generated documentation.
          </p>
          
          <div className="space-y-6">
            {/* Rating */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Overall Rating
              </label>
              <div className="flex space-x-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setFeedback(prev => ({ ...prev, rating: star }))}
                    className={`p-1 ${star <= feedback.rating ? 'text-yellow-400' : 'text-gray-300'}`}
                  >
                    <Star className="h-6 w-6 fill-current" />
                  </button>
                ))}
              </div>
            </div>

            {/* Detailed Scores */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { key: 'usefulness_score', label: 'Usefulness' },
                { key: 'accuracy_score', label: 'Accuracy' },
                { key: 'completeness_score', label: 'Completeness' }
              ].map(({ key, label }) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {label}
                  </label>
                  <select
                    value={feedback[key]}
                    onChange={(e) => setFeedback(prev => ({ ...prev, [key]: parseInt(e.target.value) }))}
                    className="input-field"
                  >
                    {[1, 2, 3, 4, 5].map(score => (
                      <option key={score} value={score}>{score} - {
                        score === 1 ? 'Poor' : score === 2 ? 'Fair' : score === 3 ? 'Good' : score === 4 ? 'Very Good' : 'Excellent'
                      }</option>
                    ))}
                  </select>
                </div>
              ))}
            </div>

            {/* Comments */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Comments (Optional)
              </label>
              <textarea
                value={feedback.comments}
                onChange={(e) => setFeedback(prev => ({ ...prev, comments: e.target.value }))}
                placeholder="Share any specific feedback about the generated documentation..."
                rows={4}
                className="textarea-field"
              />
            </div>

            <button
              onClick={submitFeedback}
              className="btn-primary"
            >
              Submit Feedback
            </button>
          </div>
        </div>
      )}

      {/* Feedback Thank You */}
      {feedbackSubmitted && (
        <div className="bg-green-50 border border-green-200 rounded-2xl p-8 text-center">
          <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-green-900 mb-2">
            Thank You for Your Feedback!
          </h3>
          <p className="text-green-700">
            Your feedback helps us improve the documentation generation process for everyone.
          </p>
        </div>
      )}

      {/* Error State */}
      {status.status === 'failed' && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-8">
          <div className="flex items-start space-x-4">
            <XCircle className="h-6 w-6 text-red-600 mt-1" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">
                Generation Failed
              </h3>
              <p className="text-red-700 mb-4">
                Unfortunately, the documentation generation process encountered an error. 
                This could be due to repository access issues or processing errors.
              </p>
              <div className="flex space-x-4">
                <Link to="/generate" className="btn-primary">
                  Try Again
                </Link>
                <button className="btn-outline">
                  Contact Support
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Status; 