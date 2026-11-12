"""Rebuild the audit as PDF and Word from its HTML. Run from the repo root: python3 report/build.py. Needs LibreOffice (soffice).
The report is no longer built here: report.docx is the final Word version (Ashesi template), and report.pdf is exported from it."""
import base64, re, shutil, subprocess, tempfile
from pathlib import Path

soffice = shutil.which("soffice") or "/Applications/LibreOffice.app/Contents/MacOS/soffice"
for name in ("audit",):
    html = Path(f"report/{name}.html").read_text()
    html = re.sub(r'src="\.\./(learnings/figures/[^"]+)"', lambda m: f'src="data:image/png;base64,{base64.b64encode(Path(m[1]).read_bytes()).decode()}"', html)  # Word and PDF need the pictures inside the file
    html = html.replace("<table>", '<table border="1" cellspacing="0">').replace('<table style', '<table border="1" cellspacing="0" style')
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / f"{name}.html"; f.write_text(html)
        subprocess.run([soffice, "--headless", "--convert-to", "pdf:writer_web_pdf_Export", "--outdir", "report", str(f)], check=True, capture_output=True)
        subprocess.run([soffice, "--headless", "--infilter=HTML (StarWriter)", "--convert-to", "docx:MS Word 2007 XML", "--outdir", "report", str(f)], check=True, capture_output=True)
