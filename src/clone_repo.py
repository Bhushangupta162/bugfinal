import os
import re
import git
from clean import clean_directories

def get_safe_repo_name(repo_url):
    """Sanitize and extract a safe folder name from the repo URL."""
    raw = repo_url.strip().split("/")[-1]
    return re.sub(r"[^\w\-]", "_", raw)

def clone_github_repo(repo_url, base_dir="repo_code"):
    """Clone a GitHub repo into a sanitized local directory."""
    clean_directories()

    safe_name = get_safe_repo_name(repo_url)
    clone_path = os.path.join(base_dir, safe_name)

    try:
        print("Cloning fresh repo...")
        git.Repo.clone_from(
            repo_url,
            clone_path,
            multi_options=["--config", "core.protectNTFS=false"],
            allow_unsafe_options=True
        )
        return clone_path
    except Exception as e:
        print(f"❌ Git clone failed: {e}")
        return None

def extract_code_files(repo_path, extensions=None):
    """Extract code files from the cloned repo, skipping junk and non-essential files."""
    if extensions is None:
        extensions = [
            ".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rb", ".php", ".rs",
            ".html", ".css", ".swift", ".kt", ".sh", ".sql", ".dart"
        ]

    code_files = []
    skip_dirs = {
        '.git', 'node_modules', '__pycache__', '.vscode', '.github',
        'venv', 'dist', 'build', 'assets', '.idea', '.pytest_cache'
    }

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if file.endswith(".min.js") or "test" in file.lower() or "mock" in file.lower():
                continue

            if any(file.endswith(ext) for ext in extensions):
                full_path = os.path.join(root, file)
                try:
                    if os.path.getsize(full_path) > 50:  # Ignore tiny files
                        code_files.append(full_path)
                except Exception:
                    continue

    return code_files