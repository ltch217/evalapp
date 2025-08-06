import React, { useState } from 'react';
import './spinner.css'

function Form() {
  const [file, setFile] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [resumeColTitle, setResumeColTitle] = useState('');
  const [runningDownload, setRunningDownload] = useState(false);
   const [runningEval, setRunningEval] = useState(false);

  const handleRunEvaluation = async () => {
    if (!file || !prompt || !apiKey || !resumeColTitle) {
        alert('CSV, Evaluation Prompt, API Key, and the title of the column containing resume links are necessary for evaluation')
        return;
    }

    setRunningEval(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('prompt', prompt);
    formData.append('api_key', apiKey);
    formData.append('resume_col_title', resumeColTitle);

    const response = await fetch('/process', {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
      console.error("Failed to process");
      return;
    }

    setRunningEval(false);

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'result.csv';
    a.click();


  };

  
  const handleDownloadZip = async () => {
      if (!file || !resumeColTitle) {
        alert('CSV and and the title of the column containing resume links are necessary to download the resumes')
        return;
      }

       setRunningDownload(true);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('resume_col_title', resumeColTitle);

      const response = await fetch('/create-zip', {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
      console.error("Failed to process");
      return;
      }

      setRunningDownload(false);

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'all_files.zip';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    }

    

    return (
    <form>
    <h4>Hirevire CSV Upload</h4>
    <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
     <h4>Resume Links Column Title</h4>
    <input type="text" placeholder="Column title(copy and paste)" value={resumeColTitle} onChange={(e) => setResumeColTitle(e.target.value)} />
    <h4>CV Evaluation Prompt</h4>
    <textarea placeholder="Enter prompt..." value={prompt} onChange={(e) => setPrompt(e.target.value)} />
    <h4>OpenAI API Key</h4>
    <input type="text" placeholder="API Key" value={apiKey} onChange={(e) => setApiKey(e.target.value)} />

      <div style={{ display: 'flex' }}>
      <button type="button" disabled={runningEval | runningDownload} 
      onClick={handleRunEvaluation}>
         {runningEval ? <span className="spinner"/> : 'Generate Evaluations'}
        </button>
      <button type="button" disabled={runningEval | runningDownload} onClick={handleDownloadZip} >
        {runningDownload ? <span className="spinner"/> : 'Download Resumes'}
        </button>
    </div>
    </form>
  );

};

export default Form;