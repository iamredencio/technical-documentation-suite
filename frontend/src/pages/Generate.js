import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../config/api';
import toast from 'react-hot-toast';
import { 
  Github, 
  FileText, 
  Settings, 
  ArrowRight, 
  AlertCircle,
  Users,
  Download,
  Loader,
  GitBranch,
  Eye,
  BarChart3,
  MessageSquare,
  Workflow,
  CheckCircle,
  Clock,
  RefreshCw,
  Languages,
  XCircle
} from 'lucide-react';

const Generate = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    repository_url: '',
    project_id: '',
    output_formats: ['markdown'],
    include_diagrams: true,
    target_audience: 'developers',
    translation_languages: []
  });
  const [errors, setErrors] = useState({});
  const [activeAgent, setActiveAgent] = useState(-1);
  const [forceUpdate, setForceUpdate] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  
  // Force update mechanism for agent changes
  const updateActiveAgent = useCallback((newAgent) => {
    console.log(`🔄 Updating active agent to: ${newAgent}`);
    setActiveAgent(newAgent);
    setForceUpdate(prev => prev + 1);
  }, []);
  const [currentWorkflowId, setCurrentWorkflowId] = useState(null);
  const [supportedLanguages, setSupportedLanguages] = useState([]);

  const agents = [
    {
      icon: GitBranch,
      name: 'Code Analyzer',
      description: 'Analyzes repository structure, extracts functions, classes, and dependencies',
      color: 'from-blue-500 to-blue-600',
    },
    {
      icon: FileText,
      name: 'Documentation Writer',
      description: 'Generates comprehensive documentation using AI in multiple formats',
      color: 'from-green-500 to-green-600',
    },
    {
      icon: Languages,
      name: 'Translation Agent',
      description: 'Translates documentation to multiple languages for global accessibility',
      color: 'from-teal-500 to-teal-600',
    },
    {
      icon: BarChart3,
      name: 'Diagram Generator',
      description: 'Creates architectural and flow diagrams using Mermaid',
      color: 'from-purple-500 to-purple-600',
    },
    {
      icon: Eye,
      name: 'Quality Reviewer',
      description: 'Assesses documentation quality and provides improvement suggestions',
      color: 'from-orange-500 to-orange-600',
    },
    {
      icon: Workflow,
      name: 'Content Orchestrator',
      description: 'Manages the complete documentation generation workflow',
      color: 'from-indigo-500 to-indigo-600',
    },
    {
      icon: MessageSquare,
      name: 'User Feedback',
      description: 'Collects and analyzes user feedback for continuous improvement',
      color: 'from-pink-500 to-pink-600',
    },
  ];

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.repository_url) {
      newErrors.repository_url = 'Repository URL is required';
    } else if (!formData.repository_url.includes('github.com')) {
      newErrors.repository_url = 'Please provide a valid GitHub URL';
    }
    
    if (!formData.project_id) {
      newErrors.project_id = 'Project ID is required';
    } else if (!/^[a-zA-Z0-9-_]+$/.test(formData.project_id)) {
      newErrors.project_id = 'Project ID can only contain letters, numbers, hyphens, and underscores';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Please fix the errors below');
      return;
    }

    setLoading(true);
    setIsGenerating(true);
    updateActiveAgent(0); // Start with first agent
    console.log('🚀 Starting documentation generation...');
    
    try {
      const response = await apiService.generateDocumentation(formData);
      
      if (response.data.success) {
        const workflowId = response.data.data.workflow_id;
        setCurrentWorkflowId(workflowId);
        toast.success('Documentation generation started!');
        
        // Start monitoring the workflow progress
        monitorWorkflow(workflowId);
      } else {
        toast.error('Failed to start documentation generation');
        setIsGenerating(false);
        updateActiveAgent(-1);
      }
    } catch (error) {
      console.error('Error starting generation:', error);
              toast.error(error.response?.data?.detail || 'Failed to start documentation generation');
        setIsGenerating(false);
        updateActiveAgent(-1);
    } finally {
      setLoading(false);
    }
  };

    const monitorWorkflow = async (workflowId) => {
    let pollCount = 0;
    const maxPolls = 450; // 15 minutes maximum (450 * 2 seconds)
    
    console.log(`🎯 Starting enhanced workflow monitoring for ${workflowId}`);
    
    const pollInterval = setInterval(async () => {
      try {
        pollCount++;
        const response = await apiService.getWorkflowStatus(workflowId);
        
        if (response.data.success) {
          const workflowData = response.data.data;
          console.log(`🔄 Poll ${pollCount}: Status=${workflowData.status}, Agent=${workflowData.current_agent}, Progress=${workflowData.progress}%`);
          
          // Map current agent to frontend index
          if (workflowData.current_agent && workflowData.status === 'processing') {
            const agentMapping = {
              'code_analyzer': 0,
              'doc_writer': 1,
              'diagram_generator': 2,
              'translation_agent': 3,
              'quality_reviewer': 4,
              'orchestrator': 5,
              'feedback_collector': 6
            };
            
            const agentIndex = agentMapping[workflowData.current_agent];
            if (agentIndex !== undefined && agentIndex !== activeAgent) {
              updateActiveAgent(agentIndex);
            }
          }
          
          // Handle completion
          if (workflowData.status === 'completed') {
            console.log('🎉 Workflow completed successfully!');
            clearInterval(pollInterval);
            
            // Show all agents as completed
            updateActiveAgent(-1);
            setIsGenerating(false);
            
            toast.success('Documentation generation completed!');
            setTimeout(() => {
              navigate(`/status/${workflowId}`);
            }, 2000);
            
          } else if (workflowData.status === 'failed') {
            console.log('❌ Workflow failed');
            clearInterval(pollInterval);
            setIsGenerating(false);
            updateActiveAgent(-1);
            toast.error('Documentation generation failed');
          }
        }
      } catch (error) {
        console.error('Error monitoring workflow:', error);
        
        // Only fail after multiple consecutive errors
        if (pollCount > 5) {
          clearInterval(pollInterval);
          setIsGenerating(false);
          updateActiveAgent(-1);
          toast.error('Lost connection to workflow');
        }
      }
      
      // Stop polling after maximum time
      if (pollCount >= maxPolls) {
        clearInterval(pollInterval);
        if (isGenerating) {
          console.log('⏰ Polling timeout reached, navigating to status page');
          navigate(`/status/${workflowId}`);
        }
      }
    }, 1500); // Poll every 1.5 seconds for more responsive updates
  };

  const getAgentStatus = useCallback((index) => {
    let status;
    if (!isGenerating) {
      status = 'idle';
    } else if (index === activeAgent) {
      status = 'active';
    } else if (index < activeAgent) {
      status = 'completed';
    } else if (activeAgent === -1 && index <= 6) {
      status = 'completed'; // Show all as completed when workflow is done
    } else {
      status = 'waiting';
    }
    
    // Debug logging for first few agents
    if (index <= 2) {
      console.log(`🎭 Agent ${index} status: ${status} (activeAgent=${activeAgent}, isGenerating=${isGenerating}, forceUpdate=${forceUpdate})`);
    }
    
    return status;
  }, [activeAgent, isGenerating, forceUpdate]);

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      setIsGenerating(false);
      updateActiveAgent(-1);
    };
  }, [updateActiveAgent]);

  // Load supported languages on component mount
  useEffect(() => {
    const loadSupportedLanguages = async () => {
      try {
        console.log('🔍 Loading supported languages...');
        const response = await apiService.getSupportedLanguages();
        console.log('📡 API Response:', response.data);
        if (response.data.success) {
          console.log('✅ Languages loaded:', response.data.data.languages);
          setSupportedLanguages(response.data.data.languages);
        } else {
          console.error('❌ API returned success=false');
        }
      } catch (error) {
        console.error('❌ Error loading supported languages:', error);
      }
    };

    loadSupportedLanguages();
  }, []);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleFormatChange = (format) => {
    setFormData(prev => ({
      ...prev,
      output_formats: prev.output_formats.includes(format)
        ? prev.output_formats.filter(f => f !== format)
        : [...prev.output_formats, format]
    }));
  };

  const handleLanguageChange = (languageCode) => {
    setFormData(prev => ({
      ...prev,
      translation_languages: prev.translation_languages.includes(languageCode)
        ? prev.translation_languages.filter(lang => lang !== languageCode)
        : [...prev.translation_languages, languageCode]
    }));
  };

  const exampleRepos = [
    {
      url: 'https://github.com/fastapi/fastapi',
      name: 'FastAPI',
      description: 'Modern, fast web framework for building APIs'
    },
    {
      url: 'https://github.com/microsoft/vscode',
      name: 'VS Code',
      description: 'Popular code editor'
    },
    {
      url: 'https://github.com/facebook/react',
      name: 'React',
      description: 'JavaScript library for building user interfaces'
    }
  ];

  const stopWorkflow = async () => {
    try {
      await apiService.stopWorkflow(currentWorkflowId);
      toast.success('Workflow stopped successfully');
      setIsGenerating(false);
      updateActiveAgent(-1);
    } catch (error) {
      console.error('Error stopping workflow:', error);
      toast.error('Failed to stop workflow');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">
          Generate Documentation
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Transform any GitHub repository into comprehensive technical documentation 
          using our advanced multi-agent system
        </p>
      </div>

      {/* Main Form */}
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Repository Section */}
          <div className="space-y-6">
            <div className="flex items-center space-x-2">
              <Github className="h-5 w-5 text-gray-700" />
              <h2 className="text-xl font-semibold text-gray-900">Repository Information</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="repository_url" className="block text-sm font-medium text-gray-700 mb-2">
                  GitHub Repository URL *
                </label>
                <input
                  type="url"
                  id="repository_url"
                  name="repository_url"
                  value={formData.repository_url}
                  onChange={handleInputChange}
                  placeholder="https://github.com/username/repository"
                  className={`input-field ${errors.repository_url ? 'border-red-500' : ''}`}
                />
                {errors.repository_url && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    {errors.repository_url}
                  </p>
                )}
              </div>
              
              <div>
                <label htmlFor="project_id" className="block text-sm font-medium text-gray-700 mb-2">
                  Project ID *
                </label>
                <input
                  type="text"
                  id="project_id"
                  name="project_id"
                  value={formData.project_id}
                  onChange={handleInputChange}
                  placeholder="my-awesome-project"
                  className={`input-field ${errors.project_id ? 'border-red-500' : ''}`}
                />
                <p className="mt-1 text-xs text-gray-500">
                  Unique identifier for this documentation project
                </p>
                {errors.project_id && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    {errors.project_id}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Configuration Section */}
          <div className="space-y-6">
            <div className="flex items-center space-x-2">
              <Settings className="h-5 w-5 text-gray-700" />
              <h2 className="text-xl font-semibold text-gray-900">Configuration</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Output Formats */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Output Formats
                </label>
                <div className="space-y-2">
                  {['markdown', 'html', 'pdf'].map(format => (
                    <label key={format} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.output_formats.includes(format)}
                        onChange={() => handleFormatChange(format)}
                        className="mr-2 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="text-sm text-gray-700 capitalize">{format}</span>
                      {format === 'markdown' && (
                        <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          Recommended
                        </span>
                      )}
                    </label>
                  ))}
                </div>
              </div>

              {/* Target Audience */}
              <div>
                <label htmlFor="target_audience" className="block text-sm font-medium text-gray-700 mb-2">
                  Target Audience
                </label>
                <select
                  id="target_audience"
                  name="target_audience"
                  value={formData.target_audience}
                  onChange={handleInputChange}
                  className="input-field"
                >
                  <option value="developers">Developers</option>
                  <option value="technical-writers">Technical Writers</option>
                  <option value="end-users">End Users</option>
                  <option value="stakeholders">Stakeholders</option>
                </select>
              </div>
            </div>

            {/* Include Diagrams */}
            <div>
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  name="include_diagrams"
                  checked={formData.include_diagrams}
                  onChange={handleInputChange}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm font-medium text-gray-700">
                  Include architectural diagrams and flowcharts
                </span>
              </label>
              <p className="mt-1 text-xs text-gray-500 ml-6">
                Generate Mermaid diagrams to visualize code structure and flow
              </p>
            </div>

            {/* Translation Languages */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                <Languages className="h-4 w-4 inline mr-2" />
                Translation Languages ({supportedLanguages.length} available)
              </label>
              {supportedLanguages.length === 0 ? (
                <div className="text-sm text-gray-500 p-4 bg-gray-50 rounded border">
                  Loading languages... If this persists, check the console for errors.
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {supportedLanguages.map(language => (
                    <label key={language.value} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.translation_languages.includes(language.value)}
                        onChange={() => handleLanguageChange(language.value)}
                        className="mr-2 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="text-sm text-gray-700">{language.label}</span>
                    </label>
                  ))}
                </div>
              )}
              <p className="mt-1 text-xs text-gray-500">
                Select languages for automatic translation of the generated documentation
              </p>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-center pt-6">
            <button
              type="submit"
              disabled={loading || isGenerating}
              className="btn-primary px-8 py-4 text-lg font-semibold min-w-[200px] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center">
                  <Loader className="animate-spin h-5 w-5 mr-2" />
                  Starting Generation...
                </div>
              ) : isGenerating ? (
                <div className="flex items-center">
                  <RefreshCw className="animate-spin h-5 w-5 mr-2" />
                  Agents Working...
                </div>
              ) : (
                <div className="flex items-center">
                  <FileText className="h-5 w-5 mr-2" />
                  Generate Documentation
                  <ArrowRight className="h-5 w-5 ml-2" />
                </div>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Multi-Agent System */}
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <div className="text-center mb-8">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900">
            Powered by Multi-Agent Intelligence
          </h2>
          <p className="text-lg text-gray-600 mt-2 max-w-2xl mx-auto">
            Seven specialized AI agents work together to analyze your code and generate comprehensive multilingual documentation
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent, index) => {
            const Icon = agent.icon;
            const status = getAgentStatus(index);
            
            return (
              <div 
                key={agent.name}
                className={`relative p-6 rounded-xl border-2 transition-all duration-500 ${
                  status === 'active' 
                    ? 'border-yellow-400 bg-yellow-50 shadow-lg transform scale-105 ring-4 ring-yellow-400/30' 
                    : status === 'completed'
                    ? 'border-green-400 bg-green-50 shadow-xl'
                    : status === 'waiting'
                    ? 'border-gray-300 bg-gray-50'
                    : 'border-gray-200 bg-white hover:border-blue-300 hover:shadow-md'
                }`}
              >
                {/* Status Badge */}
                <div className="absolute top-4 right-4">
                  {status === 'active' && (
                    <div className="flex items-center space-x-2 bg-yellow-400 text-yellow-900 px-2 py-1 rounded-full text-xs font-bold animate-pulse">
                      <div className="w-2 h-2 bg-yellow-900 rounded-full animate-ping"></div>
                      <span>ACTIVE</span>
                    </div>
                  )}
                  {status === 'completed' && (
                    <div className="flex items-center space-x-2 bg-green-400 text-green-900 px-2 py-1 rounded-full text-xs font-bold">
                      <CheckCircle className="w-3 h-3"></CheckCircle>
                      <span>DONE</span>
                    </div>
                  )}
                  {status === 'waiting' && (
                    <div className="flex items-center space-x-2 bg-gray-300 text-gray-700 px-2 py-1 rounded-full text-xs font-medium">
                      <Clock className="w-3 h-3"></Clock>
                      <span>WAITING</span>
                    </div>
                  )}
                </div>

                <div className={`bg-gradient-to-r ${agent.color} p-3 rounded-lg w-fit mb-4 transition-all duration-300 ${
                  status === 'active' ? 'animate-bounce shadow-lg' : ''
                }`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {agent.name}
                </h3>
                <p className="text-sm text-gray-600">
                  {agent.description}
                </p>
                
                {/* Progress Bar for Active Agent */}
                {status === 'active' && (
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                      <div className="bg-gradient-to-r from-yellow-400 to-orange-500 h-2 rounded-full animate-pulse" style={{width: '100%'}}></div>
                    </div>
                    <p className="text-xs text-yellow-600 font-medium animate-pulse">Processing...</p>
                  </div>
                )}
                
                {status === 'completed' && (
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                      <div className="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full" style={{width: '100%'}}></div>
                    </div>
                    <p className="text-xs text-green-600 font-medium">Completed!</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Current Processing Status */}
        {isGenerating && activeAgent >= 0 && (
          <div className="mt-8 p-6 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`bg-gradient-to-r ${agents[activeAgent].color} p-3 rounded-lg animate-bounce`}>
                  {React.createElement(agents[activeAgent].icon, { className: "h-6 w-6 text-white" })}
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 text-lg">
                    Currently Processing: {agents[activeAgent].name}
                  </h4>
                  <p className="text-sm text-gray-600">
                    {agents[activeAgent].description}
                  </p>
                  {currentWorkflowId && (
                    <p className="text-xs text-blue-600 mt-1 font-medium">
                      Workflow ID: {currentWorkflowId}
                    </p>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-ping"></div>
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-ping" style={{animationDelay: '0.2s'}}></div>
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-ping" style={{animationDelay: '0.4s'}}></div>
                </div>
                {currentWorkflowId && (
                  <button
                    onClick={stopWorkflow}
                    className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center space-x-2"
                  >
                    <XCircle className="h-4 w-4" />
                    <span>Stop</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Example Repositories */}
      <div className="bg-gray-50 rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Try with Example Repositories
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {exampleRepos.map((repo, index) => (
            <div
              key={index}
              className="bg-white p-4 rounded-lg border border-gray-200 hover:border-primary-300 cursor-pointer transition-colors"
              onClick={() => {
                setFormData(prev => ({
                  ...prev,
                  repository_url: repo.url,
                  project_id: repo.name.toLowerCase().replace(/\s+/g, '-')
                }));
              }}
            >
              <h4 className="font-medium text-gray-900">{repo.name}</h4>
              <p className="text-sm text-gray-600 mt-1">{repo.description}</p>
              <p className="text-xs text-primary-600 mt-2 font-mono">{repo.url}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Features Preview */}
      <div className="bg-white rounded-2xl p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          What You'll Get
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start space-x-3">
            <FileText className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-gray-900">Comprehensive Documentation</h4>
              <p className="text-sm text-gray-600">API references, class documentation, and usage examples</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <Download className="h-5 w-5 text-green-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-gray-900">Multiple Formats</h4>
              <p className="text-sm text-gray-600">Export in Markdown, HTML, or PDF formats</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <Users className="h-5 w-5 text-purple-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-gray-900">Quality Metrics</h4>
              <p className="text-sm text-gray-600">AI-powered quality scoring and improvement suggestions</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <Settings className="h-5 w-5 text-orange-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-gray-900">Visual Diagrams</h4>
              <p className="text-sm text-gray-600">Architectural diagrams and code flow visualization</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <Languages className="h-5 w-5 text-teal-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-gray-900">Multi-Language Support</h4>
              <p className="text-sm text-gray-600">Automatic translation to 5 languages for global accessibility</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Generate; 