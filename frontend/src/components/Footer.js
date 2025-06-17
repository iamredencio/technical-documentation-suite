import React from 'react';
import { Link } from 'react-router-dom';
import { Github, Cloud, Mail, Heart } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-secondary-800 text-white">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="md:col-span-2">
            <h3 className="text-xl font-bold mb-4">Technical Documentation Suite</h3>
            <p className="text-secondary-300 mb-4 max-w-md">
              Revolutionary multi-agent system for automated technical documentation generation. 
              Built for the Google Cloud ADK Hackathon 2024.
            </p>
            <div className="flex space-x-4">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-secondary-400 hover:text-white transition-colors"
              >
                <Github className="h-5 w-5" />
              </a>
              <a
                href="https://cloud.google.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-secondary-400 hover:text-white transition-colors"
              >
                <Cloud className="h-5 w-5" />
              </a>
              <a
                href="mailto:support@techdocsuite.com"
                className="text-secondary-400 hover:text-white transition-colors"
              >
                <Mail className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-secondary-300 hover:text-white transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/generate" className="text-secondary-300 hover:text-white transition-colors">
                  Generate Docs
                </Link>
              </li>
              <li>
                <Link to="/test" className="text-secondary-300 hover:text-white transition-colors">
                  Test Suite
                </Link>
              </li>
              <li>
                <Link to="/about" className="text-secondary-300 hover:text-white transition-colors">
                  About
                </Link>
              </li>
            </ul>
          </div>

          {/* Technology Stack */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Built With</h4>
            <ul className="space-y-2 text-secondary-300">
              <li>FastAPI</li>
              <li>React</li>
              <li>Google Cloud</li>
              <li>BigQuery</li>
              <li>Cloud Storage</li>
              <li>Multi-Agent AI</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-secondary-700 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-secondary-400 text-sm">
              © 2024 Technical Documentation Suite. Built for Google Cloud ADK Hackathon.
            </div>
            <div className="flex items-center space-x-2 text-secondary-400 text-sm">
              <span>Made with</span>
              <Heart className="h-4 w-4 text-red-500 fill-current" />
              <span>for developers</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 