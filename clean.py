import shutil
import os
import stat

JOBS_FILE = "jobs.json"

def handle_remove_readonly(func, path, exc_info):
    """
    Clear the readonly bit and reattempt the removal.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clean_directories():
    paths_to_clean = ['repo_code', 'reports']

    for path in paths_to_clean:
        if os.path.exists(path):
            print(f"🧹 Cleaning directory: {path}")
            shutil.rmtree(path, onerror=handle_remove_readonly)
        else:
            print(f"⚠️ {path} not found. Skipping...")

    # clean_jobs_file()
    print("✅ Cleanup completed.")

def clean_jobs_file():
    if os.path.exists(JOBS_FILE):
        os.remove(JOBS_FILE)
        print(f"🗑️ Removed {JOBS_FILE}")
    else:
        print(f"⚠️ {JOBS_FILE} not found. Skipping...")

if __name__ == "__main__":
    clean_directories()
