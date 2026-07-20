"""Streamlit front end for the Resume x Job Description Analyzer."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv


# Configuration must be loaded before analyzer imports llm.py, because llm.py
# reads MODEL once during import. Local values come from lab01/.env; deployed
# values come from the Streamlit Community Cloud Secrets panel.
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
load_dotenv(APP_DIR / ".env")
try:
    for key in (
        "MODEL",
        "OLLAMA_API_BASE",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
    ):
        if key in st.secrets and str(st.secrets[key]).strip():
            os.environ[key] = str(st.secrets[key]).strip()
except (FileNotFoundError, KeyError):
    pass

from analyzer import (  # noqa: E402
    analyse_degree_alignment,
    analyse_bullets,
    analyse_jargon,
    analyse_keyword_match,
    analyse_structure,
    compute_overall_score,
    extract_jd_profile,
    extract_resume_profile,
    summarise_overall,
)
from parse import read_resume_pdf  # noqa: E402
from report import render_markdown_text  # noqa: E402


ATS_PASS_THRESHOLD = 60
VALID_DEGREES = ["RTIS", "IMGD", "UXGD", "BFA"]


def run_analysis(resume_file, jd_text: str, degree: str) -> dict:
    """Run the same analysis stages as the Day 5 command-line application."""
    progress = st.progress(0, text="Preparing analysis...")

    progress.progress(8, text="1/8 — Reading résumé PDF")
    resume_text = read_resume_pdf(resume_file)

    progress.progress(16, text="2/8 — Reading job description")
    clean_jd = jd_text.strip()
    if len(clean_jd) < 100:
        raise ValueError(
            f"Job description is too short ({len(clean_jd)} characters); "
            "please provide at least 100 characters."
        )

    progress.progress(28, text="3/8 — Extracting résumé profile")
    resume_profile = extract_resume_profile(resume_text)

    progress.progress(40, text="4/8 — Extracting job profile")
    jd_profile = extract_jd_profile(clean_jd)

    progress.progress(52, text="5/8 — Checking keyword match")
    keyword_match = analyse_keyword_match(resume_profile, jd_profile)

    progress.progress(64, text="6/8 — Auditing résumé bullets")
    bullets = analyse_bullets(resume_profile)

    progress.progress(80, text="7/8 — Checking terminology, structure, and degree alignment")
    jargon = analyse_jargon(resume_profile, jd_profile)
    structure = analyse_structure(resume_text)
    degree_alignment = analyse_degree_alignment(jd_profile, degree)

    report = {
        "meta": {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "resume_file": resume_file.name,
            "target_degree": degree,
        },
        "resume_profile": resume_profile,
        "jd_profile": jd_profile,
        "keyword_match": keyword_match,
        "bullets": bullets,
        "jargon": jargon,
        "structure": structure,
        "degree_alignment": degree_alignment,
    }
    report["overall_score"] = compute_overall_score(report)
    report["passes_ats_threshold"] = (
        report["overall_score"] >= ATS_PASS_THRESHOLD
    )

    progress.progress(92, text="8/8 — Generating final summary")
    report["summary"] = summarise_overall(report)
    progress.progress(100, text="Analysis complete")
    return report


def show_results(report: dict) -> None:
    """Display the completed analysis and download controls."""
    score = report["overall_score"]
    passed = report["passes_ats_threshold"]
    verdict = "PASS" if passed else "FAIL"

    st.subheader("Analysis result")
    score_col, verdict_col, model_col = st.columns(3)
    score_col.metric("Overall score", f"{score}/100")
    verdict_col.metric("ATS threshold", verdict, help="Pass threshold: 60/100")
    model_col.metric("Model", os.getenv("MODEL", "openai/gpt-4o-mini"))

    if passed:
        st.success("This résumé meets the 60% ATS threshold.")
    else:
        st.warning("This résumé is below the 60% ATS threshold.")
    st.markdown(report.get("summary", ""))

    scores = {
        "Keyword match": report.get("keyword_match", {}).get("keyword_match_score", 0),
        "Bullet quality": report.get("bullets", {}).get("bullet_quality_avg", 0),
        "Structure": report.get("structure", {}).get("structure_score", 0),
        "Terminology": report.get("jargon", {}).get("jargon_score", 0),
        "Degree alignment": report.get("degree_alignment", {}).get("degree_alignment_score", 0),
    }
    st.bar_chart(scores, horizontal=True, x_label="Score", y_label="Category")

    with st.expander("Keyword match", expanded=True):
        st.json(report.get("keyword_match", {}))
    with st.expander("Bullet quality audit"):
        st.json(report.get("bullets", {}))
    with st.expander("Terminology and jargon"):
        st.json(report.get("jargon", {}))
    with st.expander("Structure and ATS formatting"):
        st.json(report.get("structure", {}))
    with st.expander("Degree alignment"):
        st.json(report.get("degree_alignment", {}))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_data = json.dumps(report, indent=2, ensure_ascii=False)
    markdown_data = render_markdown_text(report)
    json_col, markdown_col = st.columns(2)
    json_col.download_button(
        "Download JSON report",
        data=json_data,
        file_name=f"resume_analysis_{stamp}.json",
        mime="application/json",
        use_container_width=True,
    )
    markdown_col.download_button(
        "Download Markdown report",
        data=markdown_data,
        file_name=f"resume_analysis_{stamp}.md",
        mime="text/markdown",
        use_container_width=True,
    )


st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
st.title("📄 AI Resume Analyzer")
st.caption(
    "Upload a résumé and paste a job description to receive diagnostic, "
    "ATS-focused feedback. The app does not rewrite résumé content."
)

with st.sidebar:
    st.header("Configuration")
    st.write(f"**Model:** `{os.getenv('MODEL', 'openai/gpt-4o-mini')}`")
    st.info("A local Ollama model requires Ollama to be running on this computer.")
    if st.button("Clear results", use_container_width=True):
        st.session_state.pop("analysis_report", None)
        st.rerun()

resume_file = st.file_uploader("Upload résumé (PDF)", type=["pdf"])
jd_text = st.text_area(
    "Paste job description",
    height=250,
    placeholder="Paste the complete job posting here...",
)
degree = st.selectbox("Select degree/program", VALID_DEGREES)

if st.button("Analyze Resume", type="primary", use_container_width=True):
    if resume_file is None or not jd_text.strip():
        st.error("Please upload a résumé PDF and paste a job description.")
    else:
        try:
            with st.spinner("Running the résumé analysis pipeline..."):
                st.session_state.analysis_report = run_analysis(
                    resume_file, jd_text, degree
                )
        except (ValueError, RuntimeError) as error:
            st.error(str(error))
        except Exception as error:
            st.error(f"Analysis failed: {error}")

if "analysis_report" in st.session_state:
    show_results(st.session_state.analysis_report)
