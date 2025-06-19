"""
GitHub Service for handling authentication and repository operations
Supports both public and private repositories via GitHub tokens
"""

import os
import requests
import base64
from typing import Optional, Dict, List, Any
from urllib.parse import urlparse


class GitHubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.client_id = os.getenv('GITHUB_CLIENT_ID')
        self.client_secret = os.getenv('GITHUB_CLIENT_SECRET')
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange GitHub OAuth code for access token
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("GitHub OAuth not configured. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables.")
        
        url = "https://github.com/login/oauth/access_token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code
        }
        headers = {"Accept": "application/json"}
        
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_info(self, token: str) -> Dict[str, Any]:
        """
        Get authenticated user information
        """
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(f"{self.base_url}/user", headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def list_repositories(self, token: str, repo_type: str = "all", per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """
        List repositories for the authenticated user
        repo_type: all, owner, public, private, member
        """
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        params = {
            "type": repo_type,
            "per_page": per_page,
            "page": page,
            "sort": "updated"
        }
        
        response = requests.get(f"{self.base_url}/user/repos", headers=headers, params=params)
        response.raise_for_status()
        
        repos = response.json()
        
        # Process repos to include relevant information
        processed_repos = []
        for repo in repos:
            processed_repos.append({
                "id": repo["id"],
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo.get("description", ""),
                "private": repo["private"],
                "html_url": repo["html_url"],
                "clone_url": repo["clone_url"],
                "ssh_url": repo["ssh_url"],
                "language": repo.get("language"),
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "updated_at": repo["updated_at"],
                "size": repo["size"]
            })
        
        return {
            "repositories": processed_repos,
            "total_count": len(processed_repos),
            "page": page,
            "per_page": per_page
        }
    
    def get_repository_info(self, token: str, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific repository
        """
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(f"{self.base_url}/repos/{owner}/{repo}", headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_repository_contents(self, token: str, owner: str, repo: str, path: str = "") -> List[Dict[str, Any]]:
        """
        Get repository contents at a specific path
        """
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(f"{self.base_url}/repos/{owner}/{repo}/contents/{path}", headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_file_content(self, token: str, owner: str, repo: str, path: str) -> str:
        """
        Get the content of a specific file
        """
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(f"{self.base_url}/repos/{owner}/{repo}/contents/{path}", headers=headers)
        response.raise_for_status()
        
        file_data = response.json()
        
        if file_data.get("encoding") == "base64":
            content = base64.b64decode(file_data["content"]).decode('utf-8')
            return content
        else:
            return file_data.get("content", "")
    
    def validate_repository_access(self, token: str, repo_url: str) -> Dict[str, Any]:
        """
        Validate that the user has access to the specified repository
        """
        try:
            # Parse repository URL to extract owner and repo name
            parsed_url = urlparse(repo_url)
            if parsed_url.hostname not in ['github.com', 'www.github.com']:
                raise ValueError("Invalid GitHub repository URL")
            
            # Extract owner and repo from path
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) < 2:
                raise ValueError("Invalid repository URL format")
            
            owner = path_parts[0]
            repo = path_parts[1].replace('.git', '')
            
            # Try to access the repository
            repo_info = self.get_repository_info(token, owner, repo)
            
            return {
                "valid": True,
                "owner": owner,
                "repo": repo,
                "private": repo_info.get("private", False),
                "permissions": repo_info.get("permissions", {}),
                "repository_info": {
                    "name": repo_info["name"],
                    "full_name": repo_info["full_name"],
                    "description": repo_info.get("description", ""),
                    "language": repo_info.get("language"),
                    "stars": repo_info["stargazers_count"],
                    "forks": repo_info["forks_count"]
                }
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "message": "Unable to access repository. Please check the URL and your permissions."
            }
    
    def is_oauth_configured(self) -> bool:
        """
        Check if GitHub OAuth is properly configured
        """
        return bool(self.client_id and self.client_secret)


# Global instance
github_service = GitHubService() 