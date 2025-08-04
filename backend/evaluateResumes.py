
import io
import pdfplumber
import docx
import requests
import pandas as pd
from openai import OpenAI 


def extract_text(url : str):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return (f"HTTP error while fetching {url}: {e}")

    content_type = response.headers.get('Content-Type', '').lower()
    file_bytes = response.content
    # First try the Content-Type header
    if 'pdf' in content_type:
        return extract_text_pdf(file_bytes)
    elif 'wordprocessingml' in content_type:
        return extract_text_docx(file_bytes)

    # If header was useless, inspect the first bytes
    if file_bytes.startswith(b'%PDF'):
        return extract_text_pdf(file_bytes)
    elif file_bytes.startswith(b'PK'):
        return extract_text_docx(file_bytes)
    else:
        return (f"Cannot determine file type for {url}")

def extract_text_pdf(pdf_bytes: bytes) -> str:
    try:
        text = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text
        return text.strip()
    except Exception as e:
        return (f"Error extracting PDF text: {e}")

def extract_text_docx(docx_bytes: bytes) -> str:
    try:
        docx_buffer = io.BytesIO(docx_bytes)
        document = docx.Document(docx_buffer)
        return "\n".join(para.text for para in document.paragraphs).strip()
    except Exception as e:
        return (f"Error extracting DOCX text: {e}")

def create_prompt(prompt_text: str, resume_text: str):
    return f"{prompt_text} Resume: {resume_text}"

def openAI_Call(prompt: str, APIKey : str):
    client = OpenAI(api_key=APIKey)
    try:
        response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{'role': 'user', 'content': prompt}], temperature=0.01)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error processing: {e}"

def evaluate_csv(csv : bytes, prompt_text: str, apiKey : str, resume_col_title : str):
    results = []
    csv_text = csv.decode('utf-8')
    df = pd.read_csv(io.StringIO(csv_text))
    for i, row in df.iterrows():
        name = row['Name']
        print(f"looking at {name}")
        url = row[resume_col_title].split(",")[0].strip()
        resume_text = extract_text(url)
        linkError = "HTTP error while fetching"
        typeError = "Cannot determine file type for"
        if ((linkError in resume_text) | (typeError in resume_text)):
            eval = f"Error: {resume_text}"
        elif (resume_text.strip() == ""):
            eval = "Error: no text"
        else:
            prompt = create_prompt(prompt_text, resume_text)
            eval = 'iterating!' #openAI_call(prompt, apiKey)
        results.append([name, eval])
    return results
