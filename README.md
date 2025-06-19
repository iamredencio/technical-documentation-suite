# Technical Documentation Suite

Revolutionary multi-agent system for automated technical documentation generation. Built for Google Cloud ADK Hackathon 2024.

## Features

- **AI-Powered Documentation Generation**: Leverages Google Gemini for intelligent content creation
- **Multi-Agent Architecture**: Orchestrator-driven workflow with specialized agents
- **Real-time Progress Tracking**: Live updates on documentation generation process
- **Multi-language Translation**: Automatic translation to multiple languages
- **Modern Tech Stack**: FastAPI backend with React frontend
- **Cloud-Native Deployment**: Optimized for Google Cloud Platform

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/iamredencio/technical-documentation-suite.git
   cd technical-documentation-suite
   ```

2. **Set up environment**:
   ```bash
   conda create -n tech_doc_suit python=3.12
   conda activate tech_doc_suit
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .
   ```

4. **Configure environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

5. **Start the application**:
   ```bash
   make dev
   ```

6. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080

## Architecture

The system uses an orchestrator-centric architecture where a central Content Orchestrator manages and coordinates all specialized agents:

1. **Code Analyzer** - Analyzes repository structure and dependencies
2. **Documentation Writer** - Generates comprehensive documentation using AI
3. **Diagram Generator** - Creates visual architecture diagrams
4. **Translation Agent** - Translates content to multiple languages
5. **Quality Reviewer** - Ensures documentation quality and completeness
6. **Feedback Collector** - Gathers user feedback for continuous improvement

## Deployment

Deploy to Google Cloud Platform:

```bash
./deploy-now.sh
```

For detailed deployment instructions, see [docs/CLOUD_DEPLOYMENT_GUIDE.md](docs/CLOUD_DEPLOYMENT_GUIDE.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
