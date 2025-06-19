# Contributing to Technical Documentation Suite

Thank you for your interest in contributing to the Technical Documentation Suite! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Clone and Setup**
   ```bash
   git clone https://github.com/technical-documentation-suite/tech-doc-suite.git
   cd tech-doc-suite
   make setup
   ```

2. **Start Development**
   ```bash
   make dev          # Start backend
   make frontend     # Start frontend (in another terminal)
   ```

## 📁 Project Structure

```
tech-doc-suite/
├── src/tech_doc_suite/          # Main Python package
│   ├── agents/                  # AI agent implementations
│   ├── services/                # External service integrations
│   ├── utils/                   # Utility functions
│   ├── main.py                  # FastAPI application
│   └── config.py                # Configuration management
├── frontend/                    # React frontend application
├── tests/                       # Test suite
├── docs/                        # Documentation
├── scripts/                     # Development and deployment scripts
├── deployment/                  # Docker and cloud deployment configs
├── terraform/                   # Infrastructure as code
├── config/                      # Configuration files
│   └── secrets/                 # Sensitive configuration (gitignored)
├── .github/                     # GitHub workflows and templates
├── pyproject.toml              # Modern Python project configuration
├── Makefile                    # Development commands
└── README.md                   # Project documentation
```

## 🛠️ Development Workflow

### Prerequisites
- Python 3.10+
- Node.js 16+
- Git
- Docker (optional)

### Setting Up Development Environment

1. **Install Dependencies**
   ```bash
   make install-dev
   ```

2. **Configure Environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

### Code Style and Quality

We use modern Python tooling for code quality:

- **Formatting**: Black + isort
- **Linting**: Ruff (replaces flake8)
- **Type Checking**: MyPy
- **Security**: Bandit

Run all checks:
```bash
make lint       # Check code quality
make format     # Format code
make test       # Run tests
```

### Testing

```bash
make test                    # Run all tests
make test-cov               # Run with coverage
make test-integration       # Run integration tests only
```

Test files should be placed in the `tests/` directory and follow the naming convention `test_*.py`.

### Documentation

Documentation is built with MkDocs Material:

```bash
make docs          # Build documentation
make docs-serve    # Serve documentation locally
```

## 🔄 Contribution Process

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation if needed

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   
   We follow [Conventional Commits](https://conventionalcommits.org/):
   - `feat:` new features
   - `fix:` bug fixes
   - `docs:` documentation changes
   - `style:` formatting changes
   - `refactor:` code refactoring
   - `test:` adding tests
   - `chore:` maintenance tasks

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 🏗️ Architecture Guidelines

### Backend (FastAPI)
- Use dependency injection for services
- Follow RESTful API conventions
- Implement proper error handling
- Add type hints to all functions
- Use Pydantic models for data validation

### Frontend (React)
- Use functional components with hooks
- Follow component composition patterns
- Implement proper error boundaries
- Use TypeScript for type safety
- Follow accessibility guidelines

### Agents
- Inherit from `BaseAgent` class
- Implement async message handling
- Add comprehensive logging
- Include proper error handling
- Write unit tests for agent logic

## 🧪 Testing Guidelines

- Write tests for all new features
- Maintain high test coverage (>80%)
- Use meaningful test names
- Mock external dependencies
- Include integration tests for critical paths

## 📝 Documentation Guidelines

- Update README for user-facing changes
- Add docstrings to all public functions
- Include type hints in function signatures
- Provide examples in documentation
- Keep documentation up to date

## 🚀 Deployment

### Local Testing
```bash
make deploy-docker    # Test with Docker
```

### Production Deployment
```bash
make deploy-gcp       # Deploy to Google Cloud Run
```

## 🤝 Code Review Guidelines

- Keep PRs focused and small
- Provide clear PR descriptions
- Include screenshots for UI changes
- Ensure all CI checks pass
- Address reviewer feedback promptly

## 🆘 Getting Help

- Open an issue for bug reports
- Use discussions for questions
- Join our community chat (link TBD)
- Check existing documentation

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Happy contributing! 🎉 