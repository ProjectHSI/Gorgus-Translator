import subprocess
import os


def check_for_updates():
    """This function will return `True` when updates are available, otherwise it will return `False`.
    """

    repo_path = os.getcwd()  # Get the current directory
    subprocess.run(["git", "fetch"], cwd=repo_path)  # Fetch updates from the remote
    result = subprocess.run(["git", "status"], cwd=repo_path, capture_output=True, text=True)
    
    if "Your branch is behind" in result.stdout:
        return True
    else:
        return False