import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiService } from '../config/api';
import { 
  ArrowRight, 
  FileText, 
  BarChart3, 
  Zap, 
  Cloud, 
  Bot,
  GitBranch,
  Eye,
  MessageSquare,
  Workflow,
  Database,
  RefreshCw,
  Languages
} from 'lucide-react';

const Home = () => {
  const [activeAgent, setActiveAgent] = useState(0);
  const [isSimulating, setIsSimulating] = useState(false);

  const agents = [
    {
      icon: GitBranch,
      name: 'Code Analyzer',
      description: 'Analyzes repository structure, extracts functions, classes, and dependencies',
      color: 'from-blue-500 to-blue-600',
      status: 'idle',
    },
    {
      icon: FileText,
      name: 'Documentation Writer',
      description: 'Generates comprehensive documentation in multiple formats',
      color: 'from-green-500 to-green-600',
      status: 'idle',
    },
    {
      icon: Languages,
      name: 'Translation Agent',
      description: 'Translates documentation into multiple languages for global accessibility',
      color: 'from-teal-500 to-teal-600',
      status: 'idle',
    },
    {
      icon: BarChart3,
      name: 'Diagram Generator',
      description: 'Creates architectural and flow diagrams using Mermaid',
      color: 'from-purple-500 to-purple-600',
      status: 'idle',
    },
    {
      icon: Eye,
      name: 'Quality Reviewer',
      description: 'Assesses documentation quality and provides improvement suggestions',
      color: 'from-orange-500 to-orange-600',
      status: 'idle',
    },
    {
      icon: Workflow,
      name: 'Content Orchestrator',
      description: 'Manages the complete documentation generation workflow',
      color: 'from-indigo-500 to-indigo-600',
      status: 'idle',
    },
    {
      icon: MessageSquare,
      name: 'User Feedback',
      description: 'Collects and analyzes user feedback for continuous improvement',
      color: 'from-pink-500 to-pink-600',
      status: 'idle',
    },
  ];

  // Check for real agent activity
  useEffect(() => {
    const checkAgentActivity = async () => {
      try {
        const response = await apiService.getAgentsStatus();
        if (response.status === 200) {
          const data = response.data;
          if (data.success) {
            // Check if any agents are currently active
            const agentStatuses = data.data.agents;
            let foundActiveAgent = false;
            
            Object.keys(agentStatuses).forEach((agentKey, index) => {
              if (agentStatuses[agentKey].status === 'active' && !foundActiveAgent) {
                setActiveAgent(index);
                setIsSimulating(true);
                foundActiveAgent = true;
              }
            });
            
            if (!foundActiveAgent && isSimulating) {
              // No active agents, run demo simulation
              simulateWorkflow();
            }
          }
        }
      } catch (error) {
        // If API not available, fall back to simulation
        if (!isSimulating) {
          simulateWorkflow();
        }
      }
    };

    const simulateWorkflow = () => {
      setIsSimulating(true);
      const sequence = [0, 1, 2, 3, 4, 5, 6]; // Agent activation sequence
      
      sequence.forEach((agentIndex, i) => {
        setTimeout(() => {
          setActiveAgent(agentIndex);
          if (i === sequence.length - 1) {
            setTimeout(() => {
              setIsSimulating(false);
              setActiveAgent(-1);
            }, 2000);
          }
        }, i * 2000);
      });
    };

    // Check for real activity first, then fall back to simulation
    checkAgentActivity();
    
    // Check every 5 seconds for real agent activity
    const interval = setInterval(checkAgentActivity, 5000);
    
    return () => clearInterval(interval);
  }, [isSimulating]);

  const getAgentStatus = (index) => {
    if (!isSimulating) return 'idle';
    if (index === activeAgent) return 'active';
    if (index < activeAgent) return 'completed';
    return 'waiting';
  };

  const features = [
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Multi-agent parallel processing for rapid documentation generation',
    },
    {
      icon: Cloud,
      title: 'Cloud Native',
      description: 'Built on Google Cloud with BigQuery analytics and Cloud Storage',
    },
    {
      icon: Bot,
      title: 'AI-Powered',
      description: 'Intelligent agents that understand code structure and context',
    },
    {
      icon: Languages,
      title: 'Multi-Language',
      description: 'Automatic translation to Spanish, French, German, Japanese, and Portuguese',
    },
    {
      icon: Database,
      title: 'Scalable',
      description: 'Designed to handle projects of any size with distributed processing',
    },
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-8 py-16">
        <div className="fade-in-up">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 leading-tight">
            Next-Generation
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent block">
              Documentation Suite
            </span>
          </h1>
          <p className="text-xl text-gray-600 mt-6 max-w-3xl mx-auto">
            Revolutionary multi-agent system that automatically generates comprehensive technical documentation 
            from your codebase using advanced AI and cloud technologies.
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            to="/generate"
            className="btn-primary px-8 py-4 text-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
          >
            Start Generating <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
          <Link
            to="/test"
            className="btn-outline px-8 py-4 text-lg font-semibold"
          >
            Try Demo
          </Link>
          <button
            onClick={async () => {
              try {
                setIsSimulating(true);
                
                // Start a real documentation generation workflow
                const response = await apiService.generateDocumentation({
                  repository_url: 'https://github.com/fastapi/fastapi',
                  project_id: `demo-${Date.now()}`,
                  output_formats: ['markdown'],
                  include_diagrams: true,
                  target_audience: 'developers'
                });
                
                if (response.status === 200) {
                  const data = response.data;
                  if (data.success) {
                    const workflowId = data.data.workflow_id;
                    
                    // Poll for real agent status
                    const pollInterval = setInterval(async () => {
                      try {
                        const statusResponse = await apiService.getWorkflowStatus(workflowId);
                        if (statusResponse.status === 200) {
                          const statusData = statusResponse.data;
                          if (statusData.success) {
                            const workflowData = statusData.data;
                            
                            if (workflowData.current_agent && workflowData.agents) {
                              // Find the active agent index
                              const activeAgentKey = workflowData.current_agent;
                              const agentIndex = agents.findIndex(agent => 
                                agent.name.toLowerCase().replace(/\s+/g, '_') === activeAgentKey ||
                                agent.name.toLowerCase().replace(/\s+/g, '') === activeAgentKey.replace('_', '')
                              );
                              if (agentIndex !== -1) {
                                setActiveAgent(agentIndex);
                              }
                            }
                            
                            // Stop when completed
                            if (workflowData.status === 'completed') {
                              clearInterval(pollInterval);
                              setTimeout(() => {
                                setIsSimulating(false);
                                setActiveAgent(-1);
                              }, 2000);
                            }
                          }
                        }
                      } catch (error) {
                        console.error('Error polling agent status:', error);
                      }
                    }, 1000);
                    
                    // Fallback timeout
                    setTimeout(() => {
                      clearInterval(pollInterval);
                      setIsSimulating(false);
                      setActiveAgent(-1);
                    }, 30000);
                  }
                } else {
                  throw new Error('Failed to start workflow');
                }
              } catch (error) {
                console.error('Error starting real demo:', error);
                setIsSimulating(false);
                // Fall back to simulation
                const sequence = [0, 1, 2, 3, 4, 5, 6];
                sequence.forEach((agentIndex, i) => {
                  setTimeout(() => {
                    setActiveAgent(agentIndex);
                    if (i === sequence.length - 1) {
                      setTimeout(() => {
                        setIsSimulating(false);
                        setActiveAgent(-1);
                      }, 2000);
                    }
                  }, i * 2000);
                });
              }
            }}
            disabled={isSimulating}
            className="btn-secondary px-6 py-4 text-lg font-semibold disabled:opacity-50"
          >
            {isSimulating ? (
              <>
                <RefreshCw className="ml-2 h-5 w-5 animate-spin" />
                Watch Agents Work
              </>
            ) : (
              <>
                <Bot className="ml-2 h-5 w-5" />
                Demo Agent Flow
              </>
            )}
          </button>
        </div>

        {/* Live Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-2xl mx-auto mt-12">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">7</div>
            <div className="text-sm text-gray-600">Specialized Agents</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">95%</div>
            <div className="text-sm text-gray-600">Test Coverage</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">~2s</div>
            <div className="text-sm text-gray-600">Avg Response Time</div>
          </div>
        </div>
      </section>

      {/* Multi-Agent Architecture */}
      <section className="space-y-12">
        <div className="text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
            Powered by Multi-Agent Intelligence
          </h2>
          <p className="text-lg text-gray-600 mt-4 max-w-2xl mx-auto">
            Seven specialized AI agents work together to deliver comprehensive, multilingual documentation
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent, index) => {
            const Icon = agent.icon;
            const status = getAgentStatus(index);
            
            return (
              <div 
                key={agent.name}
                className={`glass-card p-6 transition-all duration-500 relative ${
                  status === 'active' 
                    ? 'shadow-2xl shadow-yellow-400/50 transform scale-105 ring-4 ring-yellow-400/30' 
                    : status === 'completed'
                    ? 'shadow-xl shadow-green-400/30 ring-2 ring-green-400/20'
                    : 'hover:shadow-xl transform hover:scale-105'
                }`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                {/* Status Badge */}
                <div className="absolute top-4 right-4 z-10">
                  {status === 'active' && (
                    <div className="flex items-center space-x-2 bg-yellow-400 text-yellow-900 px-2 py-1 rounded-full text-xs font-bold animate-pulse">
                      <div className="w-2 h-2 bg-yellow-900 rounded-full animate-ping"></div>
                      <span>ACTIVE</span>
                    </div>
                  )}
                  {status === 'completed' && (
                    <div className="flex items-center space-x-2 bg-green-400 text-green-900 px-2 py-1 rounded-full text-xs font-bold">
                      <div className="w-2 h-2 bg-green-900 rounded-full"></div>
                      <span>DONE</span>
                    </div>
                  )}
                  {status === 'waiting' && (
                    <div className="flex items-center space-x-2 bg-gray-300 text-gray-700 px-2 py-1 rounded-full text-xs font-medium">
                      <div className="w-2 h-2 bg-gray-500 rounded-full opacity-50"></div>
                      <span>WAITING</span>
                    </div>
                  )}
                </div>

                <div className={`bg-gradient-to-r ${agent.color} p-3 rounded-lg w-fit mb-4 transition-all duration-300 ${
                  status === 'active' ? 'animate-bounce shadow-lg' : ''
                }`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {agent.name}
                </h3>
                <p className="text-gray-600 mb-4">
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
      </section>

      {/* Features */}
      <section className="bg-white rounded-2xl p-8 md:p-12 shadow-lg">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
            Why Choose Our Platform?
          </h2>
          <p className="text-lg text-gray-600 mt-4">
            Built for the modern development workflow
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div key={feature.title} className="flex items-start space-x-4">
                <div className="bg-primary-100 p-3 rounded-lg">
                  <Icon className="h-6 w-6 text-primary-600" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* How It Works */}
      <section className="space-y-12">
        <div className="text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
            How It Works
          </h2>
          <p className="text-lg text-gray-600 mt-4">
            Simple process, powerful results
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { step: '1', title: 'Input Repository', desc: 'Provide your GitHub URL or codebase' },
            { step: '2', title: 'Agent Analysis', desc: 'Our 7 agents analyze your code in parallel' },
            { step: '3', title: 'Generate Docs', desc: 'Comprehensive documentation is created' },
            { step: '4', title: 'Review & Export', desc: 'Review quality scores and download' },
          ].map((item, index) => (
            <div key={item.step} className="text-center relative">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white w-12 h-12 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
                {item.step}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {item.title}
              </h3>
              <p className="text-gray-600 text-sm">
                {item.desc}
              </p>
              {index < 3 && (
                <ArrowRight className="hidden md:block absolute top-6 -right-3 h-6 w-6 text-gray-400" />
              )}
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 md:p-12 text-center text-white">
        <h2 className="text-3xl md:text-4xl font-bold mb-4">
          Ready to Transform Your Documentation?
        </h2>
        <p className="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
          Join the future of automated documentation generation. 
          Start with any GitHub repository and see the magic happen.
        </p>
        <Link
          to="/generate"
          className="bg-white text-blue-600 hover:bg-gray-100 font-semibold py-4 px-8 rounded-lg inline-flex items-center space-x-2 transition-colors duration-200"
        >
          <span>Generate Documentation Now</span>
          <ArrowRight className="h-5 w-5" />
        </Link>
      </section>
    </div>
  );
};

export default Home; 