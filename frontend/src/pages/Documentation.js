import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import axios from 'axios';
import toast from 'react-hot-toast';
import mermaid from 'mermaid';
import { 
  FileText, 
  Download, 
  Eye, 
  Share2, 
  Star,
  BarChart3,
  RefreshCw,
  CheckCircle,
  XCircle
} from 'lucide-react';

const Documentation = () => {
  const { workflowId } = useParams();
  const [documentation, setDocumentation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('documentation');
  const [qualityMetrics, setQualityMetrics] = useState(null);

  useEffect(() => {
    fetchDocumentation();
    // Initialize Mermaid
    mermaid.initialize({ startOnLoad: true, theme: 'default' });
  }, [workflowId]);

  useEffect(() => {
    // Re-render Mermaid diagrams when content changes
    if (documentation && activeTab === 'diagrams') {
      mermaid.init();
    }
  }, [documentation, activeTab]);

  const fetchDocumentation = async () => {
    try {
      // Fetch the actual workflow status and results from the backend
      const response = await axios.get(`http://localhost:8080/status/${workflowId}`);
      
      if (response.data.success && response.data.data.result) {
        const workflowData = response.data.data;
        const result = workflowData.result;
        
        // Structure the documentation data from backend result
        const docData = {
          workflow_id: workflowId,
          project_name: result.analysis?.project_id || 'Generated Project',
          generated_at: workflowData.completed_at || new Date().toISOString(),
          status: workflowData.status,
          ai_generated: result.ai_generated || false,
          documentation: {
            content: result.documentation || '# No documentation generated',
            diagrams: Array.isArray(result.diagrams) ? result.diagrams : 
                     typeof result.diagrams === 'string' ? [{ type: 'architecture', title: 'System Architecture', content: result.diagrams }] : [],
            quality_score: result.quality?.overall_score || 0,
            suggestions: result.quality?.feedback ? [result.quality.feedback] : []
          }
        };

        setDocumentation(docData);
        
        // Set quality metrics from backend result
        if (result.quality) {
          setQualityMetrics({
            overall_score: result.quality.overall_score || 0,
            completeness: result.quality.completeness || 0,
            accuracy: result.quality.technical_accuracy || 0,
            usefulness: result.quality.clarity || 0,
            suggestions_count: result.quality.feedback ? 1 : 0
          });
        }
      } else {
        // Fallback to sample documentation if no result available
        console.log('No result data available from backend, using sample documentation');
        const mockDoc = {
          workflow_id: workflowId,
          project_name: 'Sample Project',
          generated_at: new Date().toISOString(),
          status: 'completed',
          ai_generated: false,
          documentation: {
            content: `# Sample Project Documentation

## Overview
This is a sample technical documentation generated in demo mode. To see real AI-generated documentation, please set your GEMINI_API_KEY environment variable.

## Features
- Multi-agent documentation generation
- Real-time progress tracking
- Quality assessment and scoring
- Support for multiple output formats

## Architecture
The system uses a multi-agent approach with specialized agents for different tasks:
- **Code Analyzer**: Analyzes repository structure and extracts key information
- **Documentation Writer**: Generates comprehensive documentation using AI
- **Diagram Generator**: Creates architectural and flow diagrams
- **Quality Reviewer**: Assesses documentation quality and completeness

## Getting Started
1. Set your GEMINI_API_KEY environment variable
2. Start the application
3. Enter a GitHub repository URL
4. Watch the agents work their magic!

## API Endpoints
- \`POST /generate\` - Generate documentation for a repository
- \`GET /status/{workflow_id}\` - Check generation progress
- \`POST /feedback\` - Submit feedback on generated documentation

*This is demo content. Enable AI features by setting GEMINI_API_KEY for real documentation generation.*`,
            diagrams: [],
            quality_score: 0.85,
            suggestions: ['Enable AI features for better documentation quality']
          }
        };

        setDocumentation(mockDoc);
        setQualityMetrics({
          overall_score: 8.5,
          completeness: 9.0,
          accuracy: 8.0,
          usefulness: 8.5,
          suggestions_count: 1
        });
      }
    } catch (error) {
      console.error('Error fetching documentation:', error);
      toast.error('Failed to load documentation');
    } finally {
      setLoading(false);
    }
  };

  const downloadDocumentation = (format = 'markdown') => {
    if (!documentation) return;
    
    const content = documentation.documentation.content;
    const filename = `${documentation.project_name}-docs.${format === 'markdown' ? 'md' : format}`;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success(`Downloaded ${filename}`);
  };

  const shareDocumentation = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
      toast.success('Link copied to clipboard!');
    });
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
          <RefreshCw className="h-12 w-12 text-blue-600 mx-auto mb-4 animate-spin" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Loading Documentation...</h2>
          <p className="text-gray-600">Fetching your generated documentation</p>
        </div>
      </div>
    );
  }

  if (!documentation) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
          <XCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Documentation Not Found</h2>
          <p className="text-gray-600">The requested documentation could not be found.</p>
        </div>
      </div>
    );
  }

  const MermaidDiagram = ({ chart }) => {
    const [svg, setSvg] = useState('');

    useEffect(() => {
      const renderDiagram = async () => {
        try {
          const result = await mermaid.render('mermaid-diagram', chart);
          setSvg(result.svg);
        } catch (error) {
          console.error('Error rendering Mermaid diagram:', error);
        }
      };
      renderDiagram();
    }, [chart]);

    return (
      <div 
        className="mermaid-container bg-white p-4 rounded-lg border"
        dangerouslySetInnerHTML={{ __html: svg }}
      />
    );
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {documentation.project_name} Documentation
            </h1>
            <p className="text-gray-600">
              Generated on {new Date(documentation.generated_at).toLocaleDateString()} 
              {documentation.status === 'completed' && (
                <span className="ml-2 inline-flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-600 mr-1" />
                  Complete
                </span>
              )}
            </p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={() => downloadDocumentation('markdown')}
              className="btn-outline"
            >
              <Download className="h-4 w-4 mr-2" />
              Download
            </button>
            <button
              onClick={shareDocumentation}
              className="btn-outline"
            >
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-2xl shadow-lg">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-8">
            {[
              { id: 'documentation', name: 'Documentation', icon: FileText },
              { id: 'diagrams', name: 'Diagrams', icon: BarChart3 },
              { id: 'quality', name: 'Quality Metrics', icon: Star }
            ].map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-8">
          {/* Documentation Tab */}
          {activeTab === 'documentation' && (
            <div className="prose prose-lg max-w-none">
              <ReactMarkdown
                components={{
                  code({node, inline, className, children, ...props}) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={oneDark}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  }
                }}
              >
                {documentation.documentation.content}
              </ReactMarkdown>
            </div>
          )}

          {/* Diagrams Tab */}
          {activeTab === 'diagrams' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  System Architecture Diagram
                </h3>
                <MermaidDiagram chart={documentation.documentation.diagrams} />
              </div>
            </div>
          )}

          {/* Quality Metrics Tab */}
          {activeTab === 'quality' && qualityMetrics && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Quality Assessment
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  {[
                    { label: 'Overall Score', value: qualityMetrics.overall_score, color: 'blue' },
                    { label: 'Completeness', value: qualityMetrics.completeness, color: 'green' },
                    { label: 'Accuracy', value: qualityMetrics.accuracy, color: 'purple' },
                    { label: 'Usefulness', value: qualityMetrics.usefulness, color: 'orange' }
                  ].map((metric, index) => (
                    <div key={index} className="text-center p-4 bg-gray-50 rounded-lg">
                      <div className={`text-3xl font-bold text-${metric.color}-600 mb-1`}>
                        {metric.value}/10
                      </div>
                      <div className="text-sm text-gray-600">{metric.label}</div>
                    </div>
                  ))}
                </div>
              </div>

              {documentation.documentation.suggestions && (
                <div>
                  <h4 className="text-md font-semibold text-gray-900 mb-3">
                    Improvement Suggestions
                  </h4>
                  <ul className="space-y-2">
                    {documentation.documentation.suggestions.map((suggestion, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-gray-700">{suggestion}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Export Options */}
      <div className="bg-gray-50 rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Export Options
        </h3>
        <div className="flex space-x-4">
          <button
            onClick={() => downloadDocumentation('markdown')}
            className="btn-outline"
          >
            <FileText className="h-4 w-4 mr-2" />
            Markdown
          </button>
          <button
            onClick={() => downloadDocumentation('html')}
            className="btn-outline"
          >
            <Eye className="h-4 w-4 mr-2" />
            HTML
          </button>
          <button
            onClick={() => downloadDocumentation('pdf')}
            className="btn-outline"
          >
            <Download className="h-4 w-4 mr-2" />
            PDF
          </button>
        </div>
      </div>
    </div>
  );
};

export default Documentation; 