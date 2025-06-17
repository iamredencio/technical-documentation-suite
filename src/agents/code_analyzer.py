"""
Code Analyzer Agent - Analyzes repository structure and extracts code information
"""

import os
import re
import ast
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, Message

class CodeAnalyzerAgent(BaseAgent):
    """Agent responsible for analyzing code repositories"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "CodeAnalyzer")
        self.supported_languages = ["python", "javascript", "typescript", "java", "go", "c", "cpp", "ruby", "php"]
        self.analysis_cache = {}
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming messages"""
        if message.type == "analyze_repository":
            return await self._analyze_repository(message)
        elif message.type == "analyze_file":
            return await self._analyze_file(message)
        elif message.type == "get_complexity_metrics":
            return await self._get_complexity_metrics(message)
        else:
            self.logger.warning(f"Unknown message type: {message.type}")
            return None
    
    async def _analyze_repository(self, message: Message) -> Message:
        """Analyze a complete repository"""
        repo_url = message.data.get("repository_url")
        project_id = message.data.get("project_id")
        
        self.logger.info(f"Analyzing repository: {repo_url}")
        
        # Mock analysis for demo - in real implementation would clone and analyze repo
        analysis_result = {
            "project_id": project_id,
            "repository_url": repo_url,
            "structure": self._mock_project_structure(),
            "functions": self._mock_functions_analysis(),
            "classes": self._mock_classes_analysis(),
            "dependencies": self._mock_dependencies_analysis(),
            "complexity_metrics": self._mock_complexity_metrics(),
            "api_endpoints": self._mock_api_endpoints(),
            "file_count": 42,
            "lines_of_code": 1337,
            "language_distribution": {
                "python": 0.8,
                "yaml": 0.1,
                "markdown": 0.1
            }
        }
        
        return Message(
            type="repository_analysis_complete",
            data=analysis_result,
            sender=self.agent_id,
            recipient=message.sender
        )
    
    async def _analyze_file(self, message: Message) -> Message:
        """Analyze a specific file"""
        file_path = message.data.get("file_path")
        file_content = message.data.get("content", "")
        
        # Basic Python AST analysis for demo
        try:
            if file_path.endswith('.py'):
                tree = ast.parse(file_content)
                analysis = self._analyze_python_ast(tree)
            else:
                analysis = {"type": "unknown", "elements": []}
        except Exception as e:
            analysis = {"error": str(e), "type": "parse_error"}
        
        return Message(
            type="file_analysis_complete",
            data={
                "file_path": file_path,
                "analysis": analysis
            },
            sender=self.agent_id,
            recipient=message.sender
        )
    
    def _analyze_python_ast(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze Python AST"""
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "line": node.lineno,
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                else:
                    imports.append(node.module)
        
        return {
            "type": "python",
            "functions": functions,
            "classes": classes,
            "imports": list(set(filter(None, imports)))
        }
    
    def _mock_project_structure(self) -> Dict[str, Any]:
        """Mock project structure analysis"""
        return {
            "src/": {
                "agents/": ["base_agent.py", "code_analyzer.py", "doc_writer.py"],
                "models/": ["workflow.py", "documentation.py"],
                "services/": ["repository_service.py", "storage_service.py"]
            },
            "tests/": {
                "unit/": ["test_agents.py"],
                "integration/": ["test_api.py"]
            },
            "config/": ["settings.py", "cloud_config.py"],
            "scripts/": ["setup.sh", "test.py"]
        }
    
    def _mock_functions_analysis(self) -> List[Dict[str, Any]]:
        """Mock function analysis"""
        return [
            {
                "name": "analyze_repository",
                "file": "src/agents/code_analyzer.py",
                "parameters": ["self", "repo_url"],
                "return_type": "Dict[str, Any]",
                "complexity": 3,
                "docstring": "Analyze a code repository structure"
            },
            {
                "name": "generate_documentation",
                "file": "src/agents/doc_writer.py", 
                "parameters": ["self", "analysis_data"],
                "return_type": "str",
                "complexity": 5,
                "docstring": "Generate documentation from analysis"
            }
        ]
    
    def _mock_classes_analysis(self) -> List[Dict[str, Any]]:
        """Mock class analysis"""
        return [
            {
                "name": "BaseAgent",
                "file": "src/agents/base_agent.py",
                "methods": ["start", "stop", "handle_message"],
                "inheritance": ["ABC"],
                "docstring": "Base class for all agents"
            },
            {
                "name": "CodeAnalyzerAgent", 
                "file": "src/agents/code_analyzer.py",
                "methods": ["analyze_repository", "analyze_file"],
                "inheritance": ["BaseAgent"],
                "docstring": "Agent for analyzing code repositories"
            }
        ]
    
    def _mock_dependencies_analysis(self) -> List[Dict[str, Any]]:
        """Mock dependency analysis"""
        return [
            {"name": "fastapi", "version": "0.104.1", "type": "runtime"},
            {"name": "pydantic", "version": "2.5.0", "type": "runtime"},
            {"name": "google-cloud-storage", "version": "2.13.0", "type": "runtime"},
            {"name": "pytest", "version": "latest", "type": "development"}
        ]
    
    def _mock_complexity_metrics(self) -> Dict[str, float]:
        """Mock complexity metrics"""
        return {
            "cyclomatic_complexity": 2.3,
            "maintainability_index": 78.5,
            "lines_per_function": 12.4,
            "cognitive_complexity": 1.8
        }
    
    def _mock_api_endpoints(self) -> List[Dict[str, Any]]:
        """Mock API endpoint analysis"""
        return [
            {
                "method": "GET",
                "path": "/health",
                "function": "health_check",
                "parameters": [],
                "response_type": "Dict[str, str]"
            },
            {
                "method": "POST", 
                "path": "/generate",
                "function": "generate_documentation",
                "parameters": ["DocumentationRequest"],
                "response_type": "Dict[str, Any]"
            }
        ]
    
    async def _get_complexity_metrics(self, message: Message) -> Message:
        """Calculate complexity metrics for code"""
        file_content = message.data.get("content", "")
        
        # Simple metrics calculation
        lines = file_content.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        metrics = {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines),
            "comment_lines": len([l for l in lines if l.strip().startswith('#')]),
            "blank_lines": len(lines) - len(non_empty_lines),
            "estimated_complexity": min(len(non_empty_lines) / 10, 10)  # Simple heuristic
        }
        
        return Message(
            type="complexity_metrics_complete",
            data=metrics,
            sender=self.agent_id,
            recipient=message.sender
        )

    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Analyze a real repository directory (multi-language)"""
        structure = {}
        functions = []
        classes = []
        dependencies = set()
        file_count = 0
        lines_of_code = 0
        language_distribution = {}
        api_endpoints = []
        ext_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript", ".java": "java", ".go": "go", ".c": "c", ".cpp": "cpp", ".h": "cpp", ".hpp": "cpp", ".rb": "ruby", ".php": "php"
        }
        lang_files = {}
        
        for root, dirs, files in os.walk(repo_path):
            rel_root = os.path.relpath(root, repo_path)
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                lang = ext_map.get(ext)
                if not lang:
                    continue
                file_count += 1
                lang_files.setdefault(lang, 0)
                lang_files[lang] += 1
                file_path = os.path.join(root, file)
                rel_path = os.path.join(rel_root, file) if rel_root != "." else file
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                        lines_of_code += len(code.splitlines())
                        if lang == "python":
                            py_result = self._analyze_python_file(code, rel_path)
                            functions.extend(py_result["functions"])
                            classes.extend(py_result["classes"])
                            dependencies.update(py_result["imports"])
                        elif lang in ("javascript", "typescript"):
                            js_result = self._analyze_js_ts_file(code, rel_path)
                            functions.extend(js_result["functions"])
                            classes.extend(js_result["classes"])
                            dependencies.update(js_result["imports"])
                        elif lang == "java":
                            java_result = self._analyze_java_file(code, rel_path)
                            functions.extend(java_result["functions"])
                            classes.extend(java_result["classes"])
                            dependencies.update(java_result["imports"])
                        # Add more language handlers as needed
                except Exception as e:
                    continue
        total = sum(lang_files.values())
        for lang, count in lang_files.items():
            language_distribution[lang] = round(count / total, 2) if total else 0
        # Basic structure (folders/files)
        for root, dirs, files in os.walk(repo_path):
            rel_root = os.path.relpath(root, repo_path)
            structure.setdefault(rel_root, [])
            for file in files:
                structure[rel_root].append(file)
        return {
            "structure": structure,
            "functions": functions,
            "classes": classes,
            "dependencies": list(dependencies),
            "file_count": file_count,
            "lines_of_code": lines_of_code,
            "language_distribution": language_distribution,
            "api_endpoints": api_endpoints
        }

    def _analyze_python_file(self, code: str, file_path: str) -> Dict[str, Any]:
        functions = []
        classes = []
        imports = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "file": file_path,
                        "parameters": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node),
                        "line": node.lineno
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "file": file_path,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        "docstring": ast.get_docstring(node),
                        "line": node.lineno
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        imports.append(node.module)
        except Exception as e:
            pass
        return {"functions": functions, "classes": classes, "imports": imports}

    def _analyze_js_ts_file(self, code: str, file_path: str) -> Dict[str, Any]:
        functions = []
        classes = []
        imports = []
        # Regex for function and class (very basic)
        func_pattern = re.compile(r"function\\s+(\\w+)\\s*\\((.*?)\\)")
        class_pattern = re.compile(r"class\\s+(\\w+)")
        import_pattern = re.compile(r"import\\s+(?:[\w*{}, ]+from\s+)?['\"]([\w\-_/]+)['\"]")
        for match in func_pattern.finditer(code):
            functions.append({
                "name": match.group(1),
                "file": file_path,
                "parameters": [p.strip() for p in match.group(2).split(",") if p.strip()],
                "docstring": None
            })
        for match in class_pattern.finditer(code):
            classes.append({
                "name": match.group(1),
                "file": file_path,
                "methods": [],
                "docstring": None
            })
        for match in import_pattern.finditer(code):
            imports.append(match.group(1))
        return {"functions": functions, "classes": classes, "imports": imports}

    def _analyze_java_file(self, code: str, file_path: str) -> Dict[str, Any]:
        functions = []
        classes = []
        imports = []
        class_pattern = re.compile(r"class\\s+(\\w+)")
        method_pattern = re.compile(r"(public|private|protected)?\\s*(static)?\\s*\\w+\\s+(\\w+)\\s*\\((.*?)\\)")
        import_pattern = re.compile(r"import\\s+([\w\.]+);")
        for match in class_pattern.finditer(code):
            classes.append({
                "name": match.group(1),
                "file": file_path,
                "methods": [],
                "docstring": None
            })
        for match in method_pattern.finditer(code):
            functions.append({
                "name": match.group(3),
                "file": file_path,
                "parameters": [p.strip() for p in match.group(4).split(",") if p.strip()],
                "docstring": None
            })
        for match in import_pattern.finditer(code):
            imports.append(match.group(1))
        return {"functions": functions, "classes": classes, "imports": imports} 