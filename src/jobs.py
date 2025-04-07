import json
import os
import uuid
from datetime import datetime

JOBS_FILE = "jobs.json"

# Ensure jobs.json exists
def init_jobs_file():
    if not os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, "w") as f:
            json.dump({}, f)

# Load all jobs
def load_jobs():
    init_jobs_file()
    with open(JOBS_FILE, "r") as f:
        return json.load(f)

# Save all jobs
def save_jobs(jobs):
    # ✅ Keep only the latest 50 jobs
    if len(jobs) > 50:
        sorted_jobs = sorted(
            jobs.items(),
            key=lambda x: x[1]["started_at"]
        )
        jobs = dict(sorted_jobs[-50:])  # Keep last 50 only

    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=4)

# Create a new job
def create_job(repo_url):
    jobs = load_jobs()
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    jobs[job_id] = {
        "status": "queued",
        "repo": repo_url,
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "chunks_done": 0,
        "total_chunks": None,
        "result": None,
        "error": None
    }
    save_jobs(jobs)
    return job_id

# Update job progress
def update_job(job_id, **kwargs):
    jobs = load_jobs()
    if job_id not in jobs:
        return
    jobs[job_id].update(kwargs)
    save_jobs(jobs)

# Get job status
def get_job_status(job_id):
    jobs = load_jobs()
    return jobs.get(job_id, {"error": "Job ID not found"})

# Append error to job
def mark_job_error(job_id, error_msg):
    update_job(job_id, status="error", error=error_msg)

# Mark job as done
def mark_job_done(job_id, result):
    update_job(job_id, status="done", result=result)
