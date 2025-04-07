from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
import os
import html
from urllib.parse import urlparse

def generate_pdf_report(reports, repo_url, output_path="reports"):
    os.makedirs(output_path, exist_ok=True)

    # Extract repo name and GitHub user
    path_parts = urlparse(repo_url).path.strip("/").split("/")
    github_user = path_parts[0] if len(path_parts) > 0 else "Unknown"
    repo_name = path_parts[1] if len(path_parts) > 1 else "repository"

    filename = os.path.join(output_path, f"{repo_name}_bug_report.pdf")
    doc = SimpleDocTemplate(filename, pagesize=LETTER)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    header_style = styles["Heading2"]
    issue_style = ParagraphStyle(
        "IssueStyle",
        parent=styles["BodyText"],
        spaceBefore=4,
        spaceAfter=8,
        fontName="Helvetica",
        fontSize=10,
    )
    code_style = ParagraphStyle(
        "CodeStyle",
        parent=styles["BodyText"],
        fontName="Courier",
        fontSize=9,
        textColor=colors.darkblue,
        leftIndent=12,
        spaceBefore=4,
        spaceAfter=6,
    )

    # Count totals
    total_files = len(reports)
    total_issues = sum(len(issues) for issues in reports.values())

    # 🧾 Title
    elements.append(Paragraph(f"🔐 Critical Security Issues Report", title_style))
    elements.append(Spacer(1, 12))

    # 🔎 Report Info Block
    info_text = f"""
        <b>Repository:</b> <a href="{repo_url}">{repo_url}</a><br/>
        <b>GitHub User:</b> {html.escape(github_user)}<br/>
        <b>Project:</b> {html.escape(repo_name)}<br/>
        <b>Files Scanned:</b> {total_files}<br/>
        <b>Critical Issues Found:</b> <font color='red'><b>{total_issues}</b></font>
    """
    elements.append(Paragraph(info_text, styles["BodyText"]))
    elements.append(Spacer(1, 20))

    # 📄 File-by-file results
    for file, issues in reports.items():
        elements.append(Paragraph(f"📁 <b>File:</b> {html.escape(file)}", header_style))

        if not issues:
            elements.append(Paragraph("<i>No critical issues found in this file.</i>", styles["BodyText"]))
            elements.append(Spacer(1, 12))
            continue

        for issue in issues:
            description = html.escape(issue.get("description", "N/A"))
            severity = html.escape(issue.get("severity", "N/A"))
            recommendation = html.escape(issue.get("recommendation", "N/A"))
            code = html.escape(issue.get("code", ""))

            severity_line = f"<b>Severity:</b> <font color='red'>{severity}</font>"

            issue_text = f"""
                <b>Description:</b> {description}<br/>
                {severity_line}<br/>
                <b>Recommendation:</b> {recommendation}
            """
            elements.append(Paragraph(issue_text, issue_style))

            if code.strip():
                elements.append(Paragraph(f"<b>Code Snippet:</b><br/><font face='Courier'>{code}</font>", code_style))

        elements.append(Spacer(1, 20))

    doc.build(elements)
    print(f"📄 PDF Report saved to: {filename}")
