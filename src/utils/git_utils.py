import tempfile
import shutil
import subprocess

def clone_repo(repo_url):
    temp_dir = tempfile.mkdtemp()
    try:
        subprocess.check_call(['git', 'clone', '--depth', '1', repo_url, temp_dir])
        return temp_dir
    except Exception as e:
        shutil.rmtree(temp_dir)
        raise RuntimeError(f"Failed to clone repo: {e}") 