import re
import requests
import pandas as pd
from pathlib import Path
import zipfile
import io
from io import BytesIO
import subprocess
import uuid
import tempfile


zip_file_path = None

def sanitize_filename(name : str) -> str:
    return re.sub(r'[\\/*?:"<>| ]', "_", name)


def get_pdf_bytes(url : str) -> bytes | None:
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("failed to access link!")
        return None
    
    content_type = response.headers.get('Content-Type', '').lower()
    file_bytes = response.content
    # First try the Content-Type header
    if 'pdf' in content_type:
        return file_bytes
    elif 'wordprocessingml' in content_type:
        return get_pdf_from_docx(file_bytes)
    else: return None
    

def get_pdf_from_docx(file_bytes: bytes) -> bytes | None:
# Unique filenames to avoid collision
    temp_id = str(uuid.uuid4())
    input_path = f"/tmp/{temp_id}.docx"
    output_path = f"/tmp/{temp_id}.pdf"

    try:
        # Save .docx to disk
        with open(input_path, 'wb') as f:
            f.write(file_bytes)
        # Convert to PDF using LibreOffice CLI
        subprocess.run([
            "libreoffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", "/tmp/"
        ], check=True)
        # Read resulting PDF bytes
        with open(output_path, 'rb') as f:
            pdf_bytes = f.read()
        return pdf_bytes

    except subprocess.CalledProcessError as e:
        print(f"LibreOffice failed: {e}")
        return None

    # finally:
    #     # Cleanup temp files
    #     if os.path.exists(input_path):
    #         os.remove(input_path)
    #     if os.path.exists(output_path):
    #       os.remove(output_path)



def create_zip_of_pdfs(csv : bytes, resume_col_title:str):
    csv_text = csv.decode('utf-8')
    df = pd.read_csv(io.StringIO(csv_text))
    zip_buffer = BytesIO()

    if resume_col_title in df.columns:
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_dir = Path(tmpdir)
            for i, row in df.iterrows():
                filename = sanitize_filename(row['Name'])
                print(f'looking at: {filename}')
                pdf_path = pdf_dir / f"{filename}.pdf"
                url = row[resume_col_title].split(",")[0].strip()
                pdf_bytes = get_pdf_bytes(url)

                if pdf_bytes:
                    with open(pdf_path, "wb") as f:
                        f.write(pdf_bytes)
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for pdf_file in pdf_dir.glob("*.pdf"):
                    print(f'adding {pdf_file} to zip')
                    zipf.write(pdf_file, arcname=pdf_file.name)
                    zip_buffer.seek(0)
    return zip_buffer

