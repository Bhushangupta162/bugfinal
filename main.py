from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from src.jobs import create_job, get_job_status
from src.controller import run_analysis
import os

app = FastAPI()

# Allow frontend (optional for local testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RepoInput(BaseModel):
    repo_url: str

@app.post("/start-job")
def start_job(data: RepoInput, background_tasks: BackgroundTasks):
    repo_url = data.repo_url.strip()
    job_id = create_job(repo_url)
    background_tasks.add_task(run_analysis, repo_url, job_id)
    return {"message": "Job started", "job_id": job_id}

@app.get("/job-status/{job_id}")
def check_job_status(job_id: str):
    status = get_job_status(job_id)
    return status

@app.get("/download-report/{filename}")
def download_pdf(filename: str):
    file_path = os.path.join("reports", filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/pdf', filename=filename)
    return {"error": "File not found"}