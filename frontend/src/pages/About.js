import React from 'react';
import { 
  Award,
  Github,
  Mail,
  Users,
  Zap,
  Code,
  Brain,
  Cloud,
  Target,
  Trophy,
  Rocket
} from 'lucide-react';

const About = () => {
  const teamMembers = [
    {
      name: 'AI Development Team',
      role: 'Multi-Agent Architecture',
      description: 'Specialized in building intelligent agent systems and workflow orchestration',
      skills: ['Python', 'FastAPI', 'Multi-Agent Systems', 'Google Cloud']
    }
  ];

  const techStack = [
    { name: 'FastAPI', description: 'High-performance Python web framework', category: 'Backend' },
    { name: 'React', description: 'Modern frontend library for building user interfaces', category: 'Frontend' },
    { name: 'Google Cloud', description: 'Cloud platform for scalable infrastructure', category: 'Infrastructure' },
    { name: 'BigQuery', description: 'Data warehouse for analytics and feedback storage', category: 'Data' },
    { name: 'Cloud Storage', description: 'Object storage for generated documentation', category: 'Storage' },
    { name: 'Multi-Agent AI', description: 'Intelligent agents for automated processing', category: 'AI/ML' }
  ];

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Advanced code analysis using specialized AI agents that understand code structure, dependencies, and patterns.'
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Parallel processing with 7 specialized agents working simultaneously to generate documentation quickly.'
    },
    {
      icon: Cloud,
      title: 'Cloud Native',
      description: 'Built on Google Cloud Platform with auto-scaling, reliability, and global accessibility.'
    },
    {
      icon: Target,
      title: 'Quality Focused',
      description: 'Integrated quality assessment with scoring and improvement suggestions for every documentation.'
    }
  ];

  const achievements = [
    { icon: Trophy, title: 'Google Cloud ADK Hackathon 2024', description: 'Built for innovation competition' },
    { icon: Code, title: '7 Specialized Agents', description: 'Multi-agent architecture for comprehensive analysis' },
    { icon: Rocket, title: '95% Test Coverage', description: 'Comprehensive testing and quality assurance' },
    { icon: Award, title: 'Enterprise Ready', description: 'Scalable, secure, and production-ready solution' }
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-6">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl p-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            About Technical Documentation Suite
          </h1>
          <p className="text-xl opacity-90 max-w-3xl mx-auto">
            A revolutionary multi-agent system that transforms the way technical documentation 
            is created, making it faster, smarter, and more comprehensive than ever before.
          </p>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
            <Target className="h-6 w-6 text-blue-600 mr-2" />
            Our Mission
          </h2>
          <p className="text-gray-600 leading-relaxed">
            To democratize high-quality technical documentation by automating the entire process 
            through intelligent AI agents. We believe every codebase deserves comprehensive, 
            accurate, and maintainable documentation without the traditional overhead.
          </p>
        </div>
        
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
            <Rocket className="h-6 w-6 text-purple-600 mr-2" />
            Our Vision
          </h2>
          <p className="text-gray-600 leading-relaxed">
            To become the global standard for automated technical documentation, enabling 
            developers worldwide to focus on building great software while our AI agents 
            handle the documentation seamlessly and intelligently.
          </p>
        </div>
      </section>

      {/* Key Features */}
      <section className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Why Choose Our Platform?
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Built with cutting-edge technology and designed for the modern development workflow
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div key={index} className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-shadow">
                <div className="flex items-start space-x-4">
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
              </div>
            );
          })}
        </div>
      </section>

      {/* Hackathon Achievement */}
      <section className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-2xl p-8">
        <div className="text-center mb-8">
          <Trophy className="h-16 w-16 text-yellow-600 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Google Cloud ADK Hackathon 2024
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            This project was created for the Google Cloud Application Development Kit (ADK) Hackathon, 
            showcasing innovation in cloud-native application development and AI-powered automation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {achievements.map((achievement, index) => {
            const Icon = achievement.icon;
            return (
              <div key={index} className="text-center">
                <div className="bg-white p-4 rounded-lg shadow-md mb-3">
                  <Icon className="h-8 w-8 text-primary-600 mx-auto" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">{achievement.title}</h3>
                <p className="text-sm text-gray-600">{achievement.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Technology Stack */}
      <section className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Technology Stack
          </h2>
          <p className="text-lg text-gray-600">
            Built with modern, scalable technologies
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {techStack.map((tech, index) => (
            <div key={index} className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-primary-500">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold text-gray-900">{tech.name}</h3>
                <span className="text-xs bg-primary-100 text-primary-800 px-2 py-1 rounded">
                  {tech.category}
                </span>
              </div>
              <p className="text-gray-600 text-sm">{tech.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Multi-Agent Architecture */}
      <section className="bg-white rounded-2xl shadow-lg p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Multi-Agent Architecture
          </h2>
          <p className="text-lg text-gray-600">
            Six specialized AI agents working in harmony
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            {
              name: 'Code Analyzer',
              description: 'Analyzes repository structure, extracts functions, classes, and calculates complexity metrics',
              color: 'from-blue-500 to-blue-600'
            },
            {
              name: 'Documentation Writer',
              description: 'Generates comprehensive documentation in multiple formats tailored to the target audience',
              color: 'from-green-500 to-green-600'
            },
            {
              name: 'Diagram Generator',
              description: 'Creates architectural diagrams and flow charts using Mermaid notation',
              color: 'from-purple-500 to-purple-600'
            },
            {
              name: 'Quality Reviewer',
              description: 'Assesses documentation quality and provides improvement suggestions',
              color: 'from-orange-500 to-orange-600'
            },
            {
              name: 'Content Orchestrator',
              description: 'Manages the complete workflow and coordinates between all agents',
              color: 'from-indigo-500 to-indigo-600'
            },
            {
              name: 'User Feedback',
              description: 'Collects and analyzes user feedback for continuous improvement',
              color: 'from-pink-500 to-pink-600'
            }
          ].map((agent, index) => (
            <div key={index} className="relative">
              <div className="bg-gray-50 rounded-lg p-6 h-full">
                <div className={`bg-gradient-to-r ${agent.color} p-3 rounded-lg w-fit mb-4`}>
                  <Brain className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {agent.name}
                </h3>
                <p className="text-gray-600 text-sm">
                  {agent.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Team Section */}
      <section className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Development Team
          </h2>
          <p className="text-lg text-gray-600">
            Passionate developers building the future of documentation
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {teamMembers.map((member, index) => (
            <div key={index} className="bg-white rounded-2xl shadow-lg p-8 text-center">
              <div className="bg-gradient-to-r from-blue-500 to-purple-500 w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center">
                <Users className="h-10 w-10 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {member.name}
              </h3>
              <p className="text-primary-600 font-medium mb-3">
                {member.role}
              </p>
              <p className="text-gray-600 text-sm mb-4">
                {member.description}
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {member.skills.map((skill, skillIndex) => (
                  <span
                    key={skillIndex}
                    className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Contact & Contribution */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-center text-white">
        <h2 className="text-3xl font-bold mb-4">
          Get Involved
        </h2>
        <p className="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
          Interested in contributing to the future of automated documentation? 
          We'd love to hear from you!
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="https://github.com/iamredencio/technical-documentation-suite"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-white text-blue-600 hover:bg-gray-100 font-semibold py-3 px-6 rounded-lg inline-flex items-center space-x-2 transition-colors"
          >
            <Github className="h-5 w-5" />
            <span>View on GitHub</span>
          </a>
          <a
            href="mailto:contact@techdocsuite.com"
            className="bg-transparent border-2 border-white text-white hover:bg-white hover:text-blue-600 font-semibold py-3 px-6 rounded-lg inline-flex items-center space-x-2 transition-colors"
          >
            <Mail className="h-5 w-5" />
            <span>Contact Us</span>
          </a>
        </div>
      </section>
    </div>
  );
};

export default About; 