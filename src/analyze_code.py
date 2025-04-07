import os
import json
import re
import time
import random
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI

load_dotenv()

def safe_json_parse(data):
    try:
        parsed = json.loads(data)
        if isinstance(parsed, list) and all(
            isinstance(item, dict) and "description" in item for item in parsed
        ):
            return parsed
    except json.JSONDecodeError:
        pass
    return [{"error": "Invalid or malformed JSON from model."}]


llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))

# 🔹 Prompt: Returns only critical issues
bug_analysis_prompt = PromptTemplate(
    input_variables=["code_chunk", "language"],
    template="""
    You are a software engineer with a cybersecurity mindset. Analyze the following {language} code and report only **critical issues** in strict JSON format.

    Focus on:
    - Critical bugs that may cause functional failure or crashes
    - Security vulnerabilities such as:
        - Data leaks (e.g., hardcoded credentials, logging passwords)
        - Unsafe input handling (e.g., lack of validation, SQL injection risks)
        - Use of dangerous functions (e.g., eval, exec, shell access)

    For each issue, return:
    - `description`: A clear explanation of the issue
    - `severity`: Always "Critical"
    - `recommendation`: How to fix or prevent it
    - `code`: The exact code snippet where the issue occurs

    Only return issues of **critical severity**. Skip minor suggestions or best practices.

    Code:
    ```{language}
    {code_chunk}
    ```

    Output must be valid JSON (no markdown formatting), like:
    [
        {{
          "description": "...",
          "severity": "Critical",
          "recommendation": "...",
          "code": "..."
        }}
    ]
    """
)

# 🔹 Extract retry delay from Gemini error (for 429s)
def extract_retry_delay_from_error(error_msg, default=30):
    try:
        match = re.search(r'retry_delay\s*{\s*seconds:\s*(\d+)', str(error_msg))
        if match:
            return int(match.group(1)) + random.randint(2, 5)
    except Exception:
        pass
    return default

# 🔹 Language detection based on file extension
def detect_language_from_filename(filename):
    ext = os.path.splitext(filename)[1].lower()
    ext_language_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript", ".java": "java",
        ".cpp": "c++", ".c": "c", ".cs": "c#", ".go": "go", ".rb": "ruby",
        ".php": "php", ".swift": "swift", ".kt": "kotlin", ".m": "objective-c",
        ".html": "html", ".css": "css", ".sql": "sql", ".sh": "bash",
        ".r": "r", ".scala": "scala", ".dart": "dart"
    }
    return ext_language_map.get(ext, "plaintext")

# 🔹 Analyze a single code chunk with retry logic (no default sleep!)
def analyze_code_chunk(code_chunk, language="python", retries=4):
    chain = bug_analysis_prompt | llm

    def invoke_with_retry():
        for attempt in range(retries):
            try:
                response = chain.invoke({"code_chunk": code_chunk, "language": language})
                cleaned_response = re.sub(r"```json\n(.*?)\n```", r"\1", response, flags=re.DOTALL).strip()
                issues = safe_json_parse(cleaned_response)
                return [i for i in issues if i.get("severity", "").lower() == "critical"]
            except Exception as e:
                wait = extract_retry_delay_from_error(e)
                print(f"[Retry {attempt + 1}/{retries}] Error: {e} — Retrying in {wait}s")
                time.sleep(wait)
        return [{"error": "Failed after retries"}]

    return invoke_with_retry()

# 🔹 Analyze all chunks from one file
def analyze_multiple_chunks(chunks, filename):
    language = detect_language_from_filename(filename)
    all_issues = []
    for i, chunk in enumerate(chunks, start=1):
        print(f"🔍 Analyzing chunk {i}/{len(chunks)} as {language}...")
        issues = analyze_code_chunk(chunk, language=language)
        all_issues.extend(issues)
    return all_issues