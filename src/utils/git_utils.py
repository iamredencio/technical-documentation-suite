import tempfile
import shutil
import subprocess
import os
from urllib.parse import urlparse, urlunparse
from typing import Optional

def clone_repo(repo_url: str, github_token: Optional[str] = None, github_username: Optional[str] = None):
    """
    Clone a repository, supporting both public and private repos with authentication
    
    Args:
        repo_url: The repository URL to clone
        github_token: GitHub personal access token for private repos
        github_username: GitHub username (optional, can be inferred from token)
    
    Returns:
        str: Path to the cloned repository
    """
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Prepare the clone URL with authentication if provided
        clone_url = repo_url
        
        if github_token:
            clone_url = _add_auth_to_url(repo_url, github_token, github_username)
        
        # Clone the repository
        subprocess.check_call([
            'git', 'clone', 
            '--depth', '1',
            '--quiet',
            clone_url, 
            temp_dir
        ])
        
        return temp_dir
        
    except subprocess.CalledProcessError as e:
        shutil.rmtree(temp_dir)
        if github_token:
            raise RuntimeError(f"Failed to clone private repository: {e}. Please check your GitHub token and repository access.")
        else:
            raise RuntimeError(f"Failed to clone repository: {e}. If this is a private repository, please provide a GitHub token.")
    except Exception as e:
        shutil.rmtree(temp_dir)
        raise RuntimeError(f"Unexpected error during repository cloning: {e}")

def _add_auth_to_url(repo_url: str, github_token: str, github_username: Optional[str] = None) -> str:
    """
    Add authentication to a GitHub repository URL
    
    Args:
        repo_url: Original repository URL
        github_token: GitHub personal access token
        github_username: GitHub username (optional)
    
    Returns:
        str: Authenticated repository URL
    """
    parsed = urlparse(repo_url)
    
    # Handle different URL formats
    if parsed.hostname and 'github.com' in parsed.hostname:
        # For HTTPS URLs, add token authentication
        if parsed.scheme == 'https':
            # Use token as username for GitHub's token authentication
            auth_netloc = f"{github_token}@{parsed.hostname}"
            if parsed.port:
                auth_netloc += f":{parsed.port}"
            
            auth_url = urlunparse((
                parsed.scheme,
                auth_netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            return auth_url
        
        # For SSH URLs, convert to HTTPS with token
        elif parsed.scheme == 'ssh' or repo_url.startswith('git@'):
            # Extract owner/repo from SSH URL
            if repo_url.startswith('git@github.com:'):
                path = repo_url.replace('git@github.com:', '')
                if path.endswith('.git'):
                    path = path[:-4]
                return f"https://{github_token}@github.com/{path}.git"
    
    # For other formats, try to use the URL as-is
    return repo_url

def validate_git_url(repo_url: str) -> bool:
    """
    Validate if the provided URL is a valid Git repository URL
    
    Args:
        repo_url: Repository URL to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        parsed = urlparse(repo_url)
        
        # Check for GitHub URLs
        if parsed.hostname and 'github.com' in parsed.hostname:
            return True
        
        # Check for SSH format
        if repo_url.startswith('git@'):
            return True
        
        # Check for other Git hosting services
        git_hosts = ['gitlab.com', 'bitbucket.org', 'git.sr.ht']
        if parsed.hostname and any(host in parsed.hostname for host in git_hosts):
            return True
        
        return False
        
    except Exception:
        return False 