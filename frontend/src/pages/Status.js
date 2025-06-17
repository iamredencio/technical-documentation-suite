import React, { useState, useEffect } from 'react';
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
  Workflow
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

  const agents = [
    {
      icon: GitBranch,
      name: 'Code Analyzer',
      description: 'Analyzing repository structure and extracting code elements',
      color: 'from-blue-500 to-blue-600',
    },
    {
      icon: FileText,
      name: 'Documentation Writer',
      description: 'Generating comprehensive documentation content',
      color: 'from-green-500 to-green-600',
    },
    {
      icon: BarChart3,
      name: 'Diagram Generator',
      description: 'Creating architectural and flow diagrams',
      color: 'from-purple-500 to-purple-600',
    },
    {
      icon: Eye,
      name: 'Quality Reviewer',
      description: 'Assessing documentation quality and providing feedback',
      color: 'from-orange-500 to-orange-600',
    },
    {
      icon: Workflow,
      name: 'Content Orchestrator',
      description: 'Managing workflow and coordinating agents',
      color: 'from-indigo-500 to-indigo-600',
    },
    {
      icon: MessageSquare,
      name: 'User Feedback',
      description: 'Collecting and processing user feedback',
      color: 'from-pink-500 to-pink-600',
    },
  ];

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [workflowId]);

  // Update agent status based on real backend data
  useEffect(() => {
    if (status?.status === 'processing' && status?.agents) {
      // Find currently active agent
      const activeAgentKey = status.current_agent;
      if (activeAgentKey) {
        // Create a mapping between backend agent keys and frontend agent indices
        const agentMapping = {
          'code_analyzer': 0,
          'doc_writer': 1,
          'diagram_generator': 2,
          'quality_reviewer': 3,
          'orchestrator': 4,
          'feedback_collector': 5
        };
        
        const agentIndex = agentMapping[activeAgentKey];
        if (agentIndex !== undefined) {
          setCurrentAgentIndex(agentIndex);
        }
      }
    }
  }, [status?.status, status?.current_agent, status?.agents]);

  const fetchStatus = async () => {
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
  };

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

      {/* Agent Workflow Visualization */}
      {status.status === 'processing' && (
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
            <RefreshCw className="h-5 w-5 text-blue-600 mr-2 animate-spin" />
            Agent Workflow in Progress
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent, index) => {
              const Icon = agent.icon;
              
              // Get real agent status from backend using correct mapping
              const agentMapping = {
                'Code Analyzer': 'code_analyzer',
                'Documentation Writer': 'doc_writer', 
                'Diagram Generator': 'diagram_generator',
                'Quality Reviewer': 'quality_reviewer',
                'Content Orchestrator': 'orchestrator',
                'User Feedback': 'feedback_collector'
              };
              const agentKey = agentMapping[agent.name];
              const realAgentStatus = status?.agents?.[agentKey];
              
              let agentStatus = 'idle';
              if (realAgentStatus) {
                agentStatus = realAgentStatus.status;
              } else {
                // Fallback to index-based logic for compatibility
                const isActive = index === currentAgentIndex;
                const isCompleted = index < currentAgentIndex;
                const isWaiting = index > currentAgentIndex;
                
                agentStatus = isActive ? 'active' : isCompleted ? 'completed' : 'idle';
              }
              
              const isActive = agentStatus === 'active';
              const isCompleted = agentStatus === 'completed';
              const isWaiting = agentStatus === 'idle' && index > currentAgentIndex;
              
              return (
                <div 
                  key={agent.name}
                  className={`relative p-4 rounded-xl border-2 transition-all duration-500 ${
                    isActive 
                      ? 'border-yellow-400 bg-yellow-50 shadow-lg transform scale-105' 
                      : isCompleted
                      ? 'border-green-400 bg-green-50'
                      : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  {/* Status Indicator */}
                  <div className="absolute top-2 right-2">
                    {isActive && (
                      <div className="flex items-center space-x-1">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                        <span className="text-xs text-yellow-700 font-bold">ACTIVE</span>
                      </div>
                    )}
                    {isCompleted && (
                      <div className="flex items-center space-x-1">
                        <CheckCircle className="w-4 h-4 text-green-600"></CheckCircle>
                        <span className="text-xs text-green-700 font-bold">DONE</span>
                      </div>
                    )}
                    {isWaiting && (
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4 text-gray-400"></Clock>
                        <span className="text-xs text-gray-500 font-medium">WAITING</span>
                      </div>
                    )}
                  </div>

                  <div className={`bg-gradient-to-r ${agent.color} p-2 rounded-lg w-fit mb-3 transition-all duration-300 ${
                    isActive ? 'animate-bounce shadow-md' : ''
                  }`}>
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <h4 className="font-semibold text-gray-900 text-sm mb-1">
                    {agent.name}
                  </h4>
                  <p className="text-xs text-gray-600">
                    {agent.description}
                  </p>
                  
                  {/* Progress bar for active agent */}
                  {isActive && (
                    <div className="mt-3">
                      <div className="w-full bg-gray-200 rounded-full h-1.5">
                        <div className="bg-gradient-to-r from-yellow-400 to-orange-500 h-1.5 rounded-full animate-pulse" style={{width: '100%'}}></div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
          
          {/* Current Agent Details */}
          {status?.current_agent && (
            <div className="mt-6 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
              <div className="flex items-center space-x-3">
                <div className={`bg-gradient-to-r ${agents[currentAgentIndex].color} p-2 rounded-lg animate-bounce`}>
                  {React.createElement(agents[currentAgentIndex].icon, { className: "h-5 w-5 text-white" })}
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">
                    Currently Processing: {agents[currentAgentIndex].name}
                  </h4>
                  <p className="text-sm text-gray-600">
                    {status?.agents?.[status.current_agent]?.current_task || agents[currentAgentIndex].description}
                  </p>
                  {status?.message && (
                    <p className="text-xs text-blue-600 mt-1 font-medium">
                      {status.message}
                    </p>
                  )}
                </div>
                <div className="ml-auto">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-yellow-400 rounded-full animate-ping"></div>
                    <div className="w-2 h-2 bg-yellow-400 rounded-full animate-ping" style={{animationDelay: '0.2s'}}></div>
                    <div className="w-2 h-2 bg-yellow-400 rounded-full animate-ping" style={{animationDelay: '0.4s'}}></div>
                  </div>
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
            <button className="btn-outline">
              <Download className="h-4 w-4 mr-2" />
              Download Files
            </button>
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