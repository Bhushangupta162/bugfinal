import datetime
import os
import json
import re
from src.clone_repo import clone_github_repo, extract_code_files
from src.chunk_code import process_all_code_files
from src.analyze_code import analyze_code_chunk, detect_language_from_filename
from src.generate_pdf_report import generate_pdf_report
from src.jobs import update_job, mark_job_error, mark_job_done

def is_valid_github_url(url):
    pattern = r'^https:\/\/github\.com\/[\w\-]+\/[\w\-]+$'
    return re.match(pattern, url)

def run_analysis(repo_url, job_id=None):
    try:
        if job_id:
            update_job(job_id, status="cloning")

        if not is_valid_github_url(repo_url):
            if job_id:
                mark_job_error(job_id, "❌ Invalid GitHub URL.")
            return None, "❌ Invalid GitHub URL."

        repo_path = clone_github_repo(repo_url)
        if not repo_path:
            if job_id:
                mark_job_error(job_id, "❌ Failed to clone repository.")
            return None, "❌ Failed to clone repository."

        if job_id:
            update_job(job_id, status="extracting")

        code_files = extract_code_files(repo_path)
        if not code_files:
            if job_id:
                mark_job_error(job_id, "❌ No code files found.")
            return None, "❌ No code files found."

        if job_id:
            update_job(job_id, status="chunking")

        code_chunks = process_all_code_files(code_files)

        reports = {}
        total_issues = 0
        total_chunks = sum(len(chunks) for chunks in code_chunks.values())
        completed_chunks = 0

        if job_id:
            update_job(job_id, status="analyzing", total_chunks=total_chunks)

        for file_path, chunks in code_chunks.items():
            language = detect_language_from_filename(file_path)
            file_reports = []

            for chunk in chunks:
                analysis_result = analyze_code_chunk(chunk, language=language)
                file_reports.extend(analysis_result)

                completed_chunks += 1
                if job_id:
                    update_job(job_id, chunks_done=completed_chunks)

            reports[file_path] = file_reports
            total_issues += len(file_reports)

        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        repo_name = repo_url.strip("/").split("/")[-1]

        pdf_filename = f"{repo_name}_bug_report.pdf"
        generate_pdf_report(reports, repo_url)

        result = {
            "total_issues": total_issues,
            "total_files": len(code_chunks),
            "repo_url": repo_url,
            "repo_name": repo_name,
            "pdf_filename": pdf_filename,
            "job_id": job_id
        }

        if job_id:
            mark_job_done(job_id, result)

        return result, None

    except Exception as e:
        if job_id:
            mark_job_error(job_id, f"❌ Unexpected error: {str(e)}")
        return None, f"❌ Internal Error: {str(e)}"
