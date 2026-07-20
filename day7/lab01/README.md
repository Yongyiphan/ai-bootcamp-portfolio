# Lab 01 — AI Resume Analyzer Web App

This Streamlit application wraps the Day 4 Resume × Job Description Analyzer
pipeline in a browser interface. It accepts an uploaded PDF résumé and pasted
job description, runs the complete analysis, and produces downloadable JSON
and Markdown reports. The selected RTIS, IMGD, UXGD, or BFA program is also
checked against the job title using the degree-alignment list in the Day 7 brief.

## Local setup

```powershell
cd day7\lab01
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` to select a model. For local Ollama, use a model that is installed:

```dotenv
MODEL=ollama/llama3.2:3b
OLLAMA_API_BASE=http://localhost:11434
```

Then start the app:

```powershell
ollama pull llama3.2:3b
python -m streamlit run app.py
```

## Streamlit Community Cloud

Deploy `day7/lab01/app.py` and add the cloud model configuration in the app's
Secrets panel. A local Ollama endpoint is not accessible from Streamlit Cloud,
so use a supported hosted model there, for example:

```toml
MODEL = "openai/gpt-4o-mini"
OPENAI_API_KEY = "your-key"
```

Never commit `.env`, API keys, generated reports, or database files.

The app performs the complete eight-stage pipeline: PDF/JD parsing, resume and
JD profiling, keyword matching, bullet audit, jargon audit, ATS structure audit,
degree alignment, weighted scoring, and summary generation. It is feedback-only
and never rewrites resume content.
