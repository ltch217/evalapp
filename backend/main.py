from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import io
import csv
from evaluateResumes import evaluate_csv
from downloadPDFs import create_zip_of_pdfs


app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend/dist/assets"), name="static")

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_vue_app(full_path: str):
    index_path = os.path.join("frontend", "dist", "index.html")
    with open(index_path, "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/process")
async def process_csv_and_prompt(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    api_key: str = Form(...),
    resume_col_title: str = Form(...)
):
    contents = await file.read()

    # Call your service to get the processed DataFrame (or list of rows)
    last_processed_data = evaluate_csv(contents, prompt, api_key, resume_col_title)

    # Generate CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Evaluation']) 
    writer.writerows(last_processed_data)
    output.seek(0)

    bytes_output = io.BytesIO(output.getvalue().encode('utf-8'))
    bytes_output.seek(0)

    # Return CSV as downloadable file
    return StreamingResponse(
        bytes_output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=results.csv"}
    )

    

@app.post("/create-zip")
async def create_zip(
    file: UploadFile = File(...),
    resume_col_title: str = Form(...)
):
    contents = await file.read()
    zip_buffer = create_zip_of_pdfs(contents, resume_col_title)

    zip_buffer.seek(0)

    return StreamingResponse(zip_buffer, media_type="application/zip", headers={
    "Content-Disposition": "attachment; filename=all_files.zip"
    })